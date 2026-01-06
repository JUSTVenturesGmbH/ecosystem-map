import React from "react";
import { IColorMap } from "types";

export default function Chip({
  label,
  filters,
  colorMap,
  toggle,
}: {
  label: string;
  filters: {
    [key: string]: boolean;
  };
  colorMap: IColorMap;
  toggle: (key: string) => void;
}) {
  const style = filters[label]
    ? {
        "--chip-color": `rgb(${colorMap[label]})`,
      }
    : {
        "--chip-color": `rgb(${colorMap[label]})`,
      };

  return (
    <button
      type="button"
      className={`chip${filters[label] ? " chip--active" : ""}`}
      style={style}
      key={label}
      onClick={() => toggle(label)}
    >
      {label}
    </button>
  );
}
