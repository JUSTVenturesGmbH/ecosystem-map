import React from "react";
import { IColorMap, IFilters, ProjectInfo, TCategory } from "types";
import { cats } from "utils/helper";
import MetricsPanel from "./MetricsPanel";
import Chip from "./Chip";


function getReadinessStatus(technology: string | undefined) {
  if (!technology) {
    return "❔ Unknown";
  }
  switch (technology) {
    case "Connected to Relay chain":
    case "Connected to Parachain":
    case "In production":
      return `⚡️ ${technology}`;
    case "In research":
      return `🔬 ${technology}`;
    case "In development":
      return `🚀 ${technology}`;
    case "Validated POC / testnet":
      return `⚠️ ${technology}`;
    case "Discontinued":
      return `💤 ${technology}`;
    default:
      return technology;
  }
}

interface ActivityIndicatorProps {
  githubPushedAt: number | undefined;
}

const ACTIVITY_INDICATORS = {
  active: 'Active 🟢',
  moderate: 'Moderate 🟡',
  inactive: 'Inactive 💤',
  default: 'Unknown ❔',
};

function getActivityIndicator(githubPushedAt: number | undefined): string {

  if (!githubPushedAt) {
    return ACTIVITY_INDICATORS.default;
  }

  const lastPushDate = new Date(githubPushedAt * 1000); // githubPushedAt is in seconds
  if (Number.isNaN(lastPushDate.getTime())) {
    return ACTIVITY_INDICATORS.default;
  }

  const today = new Date();
  const diffMilliseconds = today.getTime() - lastPushDate.getTime();
  const diffDays = Math.floor(diffMilliseconds / (1000 * 60 * 60 * 24));

  if (diffDays <= 90) {
    return ACTIVITY_INDICATORS.active;
  }
  if (diffDays <= 180) {
    return ACTIVITY_INDICATORS.moderate;
  }
  return ACTIVITY_INDICATORS.inactive;
}

export function ActivityIndicator({ githubPushedAt }: ActivityIndicatorProps) {
  const label = getActivityIndicator(githubPushedAt);

  return <span>{label}</span>;
}


export default function Card({
  card,
  colorMap,
  filters,
  toggleFilter,
}: {
  card: ProjectInfo;
  colorMap: IColorMap;
  filters: IFilters;
  toggleFilter: {
    [P in TCategory]: (key: string) => void;
  };
}) {
  const inactive = card?.readiness?.technology === "Discontinued" ? "project-card--inactive" : "";
  const chipCategories = cats.filter(
    (cat) => cat !== "ecosystem" && cat !== "status",
  );

  return (
    <div className={`project-card ${inactive}`}>
      <div className="card-header">
        <div className="card-logo">
          <img
            src={`img/${card?.web?.logo}`}
            alt="logo"
            onError={({ currentTarget }) => {
              currentTarget.onerror = null;
              currentTarget.src = "img/default.png";
            }}
          />
        </div>
        <div>
          <a target="_blank" href={card.web.site} rel="noreferrer noopener">
            <span className="card-title">
              {card.name} {inactive ? "[inactive]" : ""}
            </span>
          </a>
        </div>
        <div className="card-header-meta">
          <ActivityIndicator githubPushedAt={card.metrics?.github_pushed_at?.pop()?.value} />
        </div>
      </div>
      <div className="card-badges">
        {chipCategories.map((cat) =>
          card[cat]?.map((i) => (
            <Chip
              key={i}
              label={i}
              filters={filters[cat]}
              colorMap={colorMap}
              toggle={toggleFilter[cat]}
            />
          )),
        )}
      </div>
      <div className="card-badges">
        <span className="status-pill">
          <strong>Status:</strong> {getReadinessStatus(card?.readiness?.technology)}
        </span>
        {card.ecosystem?.map((i) => (
          <Chip
            key={i}
            label={i}
            filters={filters.ecosystem}
            colorMap={colorMap}
            toggle={toggleFilter.ecosystem}
          />
        ))}
      </div>
      <div className="project-description">{card.description}</div>
      <div>
        <MetricsPanel project={card} />
      </div>
    </div>
  );
}
