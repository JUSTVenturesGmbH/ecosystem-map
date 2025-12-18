#!/usr/bin/env python3
"""Download GitHub repo avatars for projects missing logos."""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path
from typing import Iterable, Optional, Tuple
from urllib.parse import urlparse

import requests
from ruamel.yaml import YAML

GITHUB_API_REPO = "https://api.github.com/repos/{owner}/{repo}"
DEFAULT_IMAGE_SIZE = 512


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch GitHub avatars for entries whose logos are missing or default.png."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Dataset root (default: data/)")
    parser.add_argument("--img-dir", type=Path, default=Path("img"), help="Asset dir (default: img/)")
    parser.add_argument("--include-team", action="store_true", help="Also scan data/team/*.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without touching files.")
    parser.add_argument("--limit", type=int, default=None, help="Process at most N YAML files.")
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"),
        help="GitHub token to avoid rate limiting (default: env GITHUB_TOKEN/GH_TOKEN).",
    )
    return parser.parse_args()


def iter_yaml_files(base_dir: Path, include_team: bool) -> Iterable[Path]:
    for path in sorted(base_dir.rglob("*.yaml")):
        rel = path.relative_to(base_dir)
        if not include_team and rel.parts and rel.parts[0] == "team":
            continue
        yield path


def extract_repo_slug(url: str) -> Optional[Tuple[str, str]]:
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def sanitize_basename(name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]+", " ", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.replace(" ", "-")
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "project-logo"


def pick_filename(suggested_name: str, img_dir: Path) -> str:
    candidate = img_dir / suggested_name
    if not candidate.exists():
        return suggested_name

    stem, suffix = candidate.stem, candidate.suffix
    counter = 1
    while True:
        alternative = f"{stem}-{counter}{suffix}"
        if not (img_dir / alternative).exists():
            return alternative
        counter += 1


def fetch_github_avatar(session: requests.Session, owner: str, repo: str) -> Tuple[bytes, str]:
    resp = session.get(GITHUB_API_REPO.format(owner=owner, repo=repo), timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    full_name = payload.get("full_name") or f"{owner}/{repo}"
    owner_info = payload.get("owner") or {}
    avatar_url = owner_info.get("avatar_url")
    if not avatar_url:
        raise RuntimeError("Repository owner has no avatar.")

    avatar_resp = session.get(avatar_url, params={"size": DEFAULT_IMAGE_SIZE}, timeout=20)
    avatar_resp.raise_for_status()
    return avatar_resp.content, full_name


def main() -> int:
    args = parse_args()
    yaml_parser = YAML(typ="rt")
    yaml_parser.preserve_quotes = True
    yaml_parser.default_flow_style = False
    yaml_parser.width = 4096
    yaml_parser.indent(mapping=2, sequence=4, offset=2)

    session = requests.Session()
    session.headers["User-Agent"] = "ecosystem-map-github-logo-fetcher/1.0"
    if args.token:
        session.headers["Authorization"] = f"Bearer {args.token}"

    processed = downloaded = skipped = 0

    for yaml_path in iter_yaml_files(args.data_dir, args.include_team):
        if args.limit is not None and processed >= args.limit:
            break
        processed += 1

        with yaml_path.open("r", encoding="utf-8") as handle:
            doc = yaml_parser.load(handle)

        project_name = doc.get("name", yaml_path.stem)
        web = doc.get("web") or {}
        github_url = web.get("github")
        logo_name = web.get("logo")

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

        if not github_url:
            logging.info("Skipping %s (no GitHub URL)", project_name)
            skipped += 1
            continue

        repo_slug = extract_repo_slug(github_url)
        if not repo_slug:
            logging.warning("Skipping %s (unsupported GitHub URL: %s)", project_name, github_url)
            skipped += 1
            continue

        owner, repo = repo_slug

        try:
            image_bytes, repo_name = fetch_github_avatar(session, owner, repo)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to fetch repo avatar for %s (%s/%s): %s", project_name, owner, repo, exc)
            skipped += 1
            continue

        if logo_name != "default.png" and Path(logo_name).suffix.lower() == ".png":
            target_filename = Path(logo_name).name
        else:
            safe_base = sanitize_basename(project_name)
            target_filename = pick_filename(f"{safe_base}.png", args.img_dir)

        target_path = args.img_dir / target_filename

        if args.dry_run:
            logging.info(
                "[dry-run] Would save GitHub avatar for %s (%s) -> %s",
                project_name,
                repo_name,
                target_path,
            )
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(image_bytes)
            logging.info("Saved %s for %s (repo: %s)", target_path, project_name, repo_name)

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
        "Processed %d yaml files: downloaded %d avatars, skipped %d entries",
        processed,
        downloaded,
        skipped,
    )
    return 0 if downloaded else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
