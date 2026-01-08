import { TCategory } from "types";

export const round = (n: Number, multi = 1) =>
  Math.round(Number(n) * multi) / multi;

export const cats: TCategory[] = [
  "category",
  "status",
  "target_audience",
  "ecosystem",
];

export const colors = [
  [237, 136, 141],
  [79, 126, 191],
  [255, 127, 0],
  [226, 131, 208],
  [118, 181, 244],
  [130, 191, 130],
  [168, 168, 168],
  [55, 205, 221],
  [153, 102, 51],
  [204, 98, 142],
  [221, 75, 128],
  [192, 134, 242],
  [102, 84, 175],
  [0, 163, 151],
  [124, 91, 77],
  [98, 115, 140],
  [165, 30, 37],
  [255, 97, 97],
  [249, 170, 84],
  [249, 225, 86],
];
