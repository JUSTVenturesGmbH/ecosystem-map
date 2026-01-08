import React from "react";
import { IColorMap } from "types";
import Chip from "./Chip";

export default function ChipFilterBlock({
  name,
  filters,
  toggle,
  colorMap,
  order,
  counts,
}: {
  name: string;
  filters: { [key: string]: boolean };
  toggle: (key: string) => void;
  colorMap: IColorMap;
  order?: string[];
  counts?: { [key: string]: number };
}) {
  const keys = Object.keys(filters);
  const ordered = order
    ? [
        ...order.filter((item) => filters[item] !== undefined),
        ...keys.filter((item) => !order.includes(item)).sort(),
      ]
    : keys.sort();

  return (
    <div className="filter-block">
      <h3 className="filter-title">{name}</h3>
      <div className="chip-block">
        {ordered.map((i) => (
          <div className="chip-row" key={i}>
            <Chip
              label={i}
              filters={filters}
              colorMap={colorMap}
              toggle={toggle}
            />
            {typeof counts?.[i] === "number" ? (
              <span className="chip-count-label">{counts[i]}</span>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
