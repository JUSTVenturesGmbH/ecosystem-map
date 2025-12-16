#!/usr/bin/env python3
"""
Download Discord server icons for dataset entries that still rely on the default
logo (or have a missing image) and store the files inside img/.
"""
from __future__ import annotations

import argparse
import io
import logging
import re
import sys
from pathlib import Path
from typing import Iterable, Optional, Tuple
from urllib.parse import urlparse

import requests
from PIL import Image
from ruamel.yaml import YAML

INVITE_ENDPOINT = "https://discord.com/api/v10/invites/{code}"
ICON_ENDPOINT = "https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.{extension}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Discord icons for projects whose logo file is missing or "
            "still using default.png"
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory that stores project YAML files (default: data/)",
    )
    parser.add_argument(
        "--img-dir",
        type=Path,
        default=Path("img"),
        help="Directory that stores logo images (default: img/)",
    )
    parser.add_argument(
        "--include-team",
        action="store_true",
        help="Include files in data/team/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without writing files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N YAML entries (useful for testing).",
    )
    return parser.parse_args()


def iter_yaml_files(base_dir: Path, include_team: bool) -> Iterable[Path]:
    for path in sorted(base_dir.rglob("*.yaml")):
        if not include_team:
            relative_parts = path.relative_to(base_dir).parts
            if relative_parts and relative_parts[0] == "team":
                continue
        yield path


def extract_invite_code(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if not path:
        return None

    if "discord.gg" in host:
        return path.split("/")[0]

    if "discord.com" in host:
        if path.startswith("invite/"):
            return path.split("/", 1)[1]
        if path.startswith("widget?id="):
            # widget?id=<guild_id> links don't expose guild icon hashes
            return None

    return None


def fetch_discord_icon(session: requests.Session, invite_code: str) -> Tuple[Image.Image, str]:
    resp = session.get(
        INVITE_ENDPOINT.format(code=invite_code),
        params={"with_counts": "true", "with_expiration": "true"},
        timeout=20,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Invite lookup failed with {resp.status_code}")

    payload = resp.json()
    guild = payload.get("guild") or {}
    guild_id = guild.get("id")
    icon_hash = guild.get("icon")

    if not guild_id or not icon_hash:
        raise RuntimeError("Server does not expose an icon")

    extension = "gif" if icon_hash.startswith("a_") else "png"
    icon_url = ICON_ENDPOINT.format(
        guild_id=guild_id,
        icon_hash=icon_hash,
        extension=extension,
    )

    icon_resp = session.get(icon_url, timeout=20)
    icon_resp.raise_for_status()

    with Image.open(io.BytesIO(icon_resp.content)) as image:
        # Convert all formats to RGBA for consistent downstream conversions
        converted = image.convert("RGBA")

    return converted, guild.get("name") or invite_code


def sanitize_basename(name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]+", " ", name, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.replace(" ", "-")
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "project-logo"


def pick_filename(
    suggested_name: str,
    img_dir: Path,
    allow_overwrite: bool,
) -> str:
    path = img_dir / suggested_name
    if allow_overwrite or not path.exists():
        return suggested_name

    stem = path.stem
    suffix = path.suffix
    counter = 1
    while True:
        candidate = f"{stem}-{counter}{suffix}"
        if not (img_dir / candidate).exists():
            return candidate
        counter += 1


def save_image(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ext = destination.suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        rgb_image = image.convert("RGB")
        rgb_image.save(destination, format="JPEG", quality=92)
    else:
        # Default to PNG to preserve transparency
        image.save(destination, format="PNG")


def main() -> int:
    args = parse_args()
    yaml_parser = YAML(typ="rt")
    yaml_parser.preserve_quotes = True
    yaml_parser.default_flow_style = False
    yaml_parser.width = 4096
    yaml_parser.indent(mapping=2, sequence=4, offset=2)

    session = requests.Session()
    session.headers["User-Agent"] = "ecosystem-map-logo-fetcher/1.0"

    processed = 0
    downloaded = 0
    skipped = 0

    for yaml_path in iter_yaml_files(args.data_dir, args.include_team):
        if args.limit is not None and processed >= args.limit:
            break

        processed += 1

        with yaml_path.open("r", encoding="utf-8") as handle:
            doc = yaml_parser.load(handle)

        project_name = doc.get("name", yaml_path.stem)
        web = doc.get("web") or {}
        logo_name = web.get("logo")
        discord_url = web.get("discord")

        if not logo_name:
            logging.warning("Skipping %s (missing web.logo)", project_name)
            skipped += 1
            continue

        needs_logo = (
            logo_name == "default.png"
            or not (args.img_dir / Path(logo_name).name).exists()
        )

        if not needs_logo:
            continue

        if not discord_url:
            logging.info("Skipping %s (no Discord link)", project_name)
            skipped += 1
            continue

        invite_code = extract_invite_code(discord_url)
        if not invite_code:
            logging.warning(
                "Skipping %s (unsupported Discord URL: %s)", project_name, discord_url
            )
            skipped += 1
            continue

        try:
            image, guild_name = fetch_discord_icon(session, invite_code)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to fetch icon for %s: %s", project_name, exc)
            skipped += 1
            continue

        target_suffix = Path(logo_name).suffix.lower()
        if logo_name == "default.png" or target_suffix not in {".png", ".jpg", ".jpeg"}:
            safe_base = sanitize_basename(project_name)
            target_filename = pick_filename(f"{safe_base}.png", args.img_dir, allow_overwrite=False)
        else:
            target_filename = Path(logo_name).name

        target_path = args.img_dir / target_filename

        if args.dry_run:
            logging.info(
                "[dry-run] Would save icon for %s (%s) -> %s",
                project_name,
                guild_name,
                target_path,
            )
        else:
            save_image(image, target_path)
            logging.info(
                "Saved %s for %s (Discord: %s)",
                target_path,
                project_name,
                guild_name,
            )

        if target_filename != logo_name:
            web["logo"] = target_filename
            if args.dry_run:
                logging.info(
                    "[dry-run] Would update %s web.logo -> %s",
                    yaml_path,
                    target_filename,
                )
            else:
                with yaml_path.open("w", encoding="utf-8") as handle:
                    yaml_parser.dump(doc, handle)

        downloaded += 1

    logging.info(
        "Processed %d yaml files: downloaded %d icons, skipped %d entries",
        processed,
        downloaded,
        skipped,
    )
    if downloaded == 0:
        return 1
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
