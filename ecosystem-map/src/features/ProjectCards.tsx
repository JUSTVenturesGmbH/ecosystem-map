import React from "react";
import { IColorMap, IFilters, ProjectInfo, TCategory } from "types";
import Card from "./Card";

export default function ProjectCards({
  projects,
  colorMap,
  filters,
  toggleFilter,
}: {
  projects: ProjectInfo[];
  colorMap: IColorMap;
  filters: IFilters;
  toggleFilter: {
    [P in TCategory]: (key: string) => void;
  };
}) {
  return (
    <div className="projects-grid">
      {projects.map((p) => (
        <Card
          key={p.name}
          card={p}
          colorMap={colorMap}
          filters={filters}
          toggleFilter={toggleFilter}
        />
      ))}
    </div>
  );
}
