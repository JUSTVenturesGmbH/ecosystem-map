import React from "react";
import { IColorMap } from "types";
import Chip from "./Chip";

export default function ChipFilterBlock({
  name,
  filters,
  toggle,
  colorMap,
}: {
  name: string;
  filters: { [key: string]: boolean };
  toggle: (key: string) => void;
  colorMap: IColorMap;
}) {
  return (
    <div className="filter-block">
      <h3 className="filter-title">{name}</h3>
      <div className="chip-block">
        {Object.keys(filters)
          .sort()
          .map((i) => (
            <Chip
              key={i}
              label={i}
              filters={filters}
              colorMap={colorMap}
              toggle={toggle}
            />
          ))}
      </div>
    </div>
  );
}
