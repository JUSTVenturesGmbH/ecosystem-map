import React from "react";
import ChipFilterBlock from "./ChipFilterBlock";
import { IColorMap, IFilters, ProjectInfo } from "../types";
import { cats, colors } from "../utils/helper";
import ProjectCards from "./ProjectCards";

interface ISortState {
  column: keyof ProjectInfo;
  asc: boolean;
}
const catMapping: { [P in keyof IFilters]: string } = {
  category: "Category",
  layer: "Type",
  target_audience: "Audience",
  ecosystem: "Ecosystem"
};

export default function EcosystemMap() {
  const [ecosystemProjects, setEcosystemProjects] = React.useState<
    ProjectInfo[]
  >([]);
  const [data, setData] = React.useState<ProjectInfo[]>([]);
  const [filters, setFilters] = React.useState<IFilters>({
    layer: {},
    category: {},
    target_audience: {}, 
    ecosystem: {},
  });
  const [colorMap, setColorMap] = React.useState<IColorMap>({});
  
  const [sort] = React.useState<ISortState>({ column: "name", asc: true });

  const sortProjects = (projects = ecosystemProjects) => {
    setEcosystemProjects(
      projects.sort((a, b) => {
        let res = 0;

        if (a[sort.column] < b[sort.column]) {
          res = -1;
        } else if (a[sort.column] > b[sort.column]) {
          res = 1;
        }

        return sort.asc ? res : res * -1;
      }),
    );
  };

  const filterProjects = () => {
    const category = Object.keys(filters.category).filter(
      (k) => filters.category[k],
    );
    const layer = Object.keys(filters.layer).filter((k) => filters.layer[k]);
    const audience = Object.keys(filters.target_audience).filter(
      (k) => filters.target_audience[k],
    );
    const ecosystem = Object.keys(filters.ecosystem).filter((k) => filters.ecosystem[k]);

    setData(
      ecosystemProjects.filter(
        (p) =>
          category.every((c) => p.category?.find((d) => d === c)) &&
          layer.every((c) => p.layer?.find((d) => d === c)) &&
          audience.every((c) => p.target_audience?.find((d) => d === c)) &&
          ecosystem.every((c) => p.ecosystem?.find((d) => d === c))
      ),
    );
  };

  const toggleFilterByCategory = (type: keyof IFilters, key: string) => {
    setFilters({
      ...filters,
      [type]: {
        ...filters[type],
        [key]: !filters[type][key],
      },
    });
  };

  const toggleFilter = {
    category: (k: string) => toggleFilterByCategory("category", k),
    layer: (k: string) => toggleFilterByCategory("layer", k),
    target_audience: (k: string) =>
      toggleFilterByCategory("target_audience", k),
    ecosystem: (k: string) => toggleFilterByCategory("ecosystem", k),
  };

  React.useEffect(() => {
    const url = "projects.json";

    fetch(url)
      .then((res) => res.json())
      .then((d) => {
        const f: IFilters = { layer: {}, category: {}, target_audience: {}, ecosystem: {} };

        d.forEach((c: ProjectInfo) => {
          c?.layer?.forEach((l) => {
            if (l) {
              f.layer[l] = false;
            }
          });
          c?.category?.forEach((l) => {
            if (l) {
              f.category[l] = false;
            }
          });

          c?.target_audience?.forEach((l) => {
            if (l) {
              f.target_audience[l] = false;
            }
          });

          c?.ecosystem?.forEach((l) => {
            if (l) {
              f.ecosystem[l] = false;
            }
          });
        });
        setFilters(f);

        const c: { [key: string]: string } = {};

        [
          ...Object.keys(f.category),
          ...Object.keys(f.layer),
          ...Object.keys(f.target_audience),
          ...Object.keys(f.ecosystem),
        ].forEach((k, idx) => {
          c[k] = (colors[idx % colors.length] ?? [33, 150, 243]).join(",");
        });
        setColorMap(c);

        sortProjects(d);
      });
  }, []);

  React.useEffect(() => {
    sortProjects();
    filterProjects();
  }, [sort]);

  React.useEffect(() => filterProjects(), [filters, ecosystemProjects]);

  return (
    <div className="container roboto-regular">
      <div>
        <div className="header">
          Welcome to the community-sourced Polkadot/Kusama ecosystem directory
          of projects
        </div>
        <div className="sub-header">
          Curated by JUST Ventures team. This is a preview of our database,
          for further details please visit <a href="https://github.com/JUSTBeteiligungen/ecosystem-map">our Github</a>. Filter by category, type, ecosystem 
          and potential audience.
          <br />
          <i>
            The directory is available for general information purposes only and is not an official endorsement of the projects by JUST team. Although we do our best to verify the data, there may be errors in the entries. Please check the details yourself!
          </i>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {cats.map((cat) => (
          <ChipFilterBlock
            key={catMapping[cat]}
            name={catMapping[cat]}
            colorMap={colorMap}
            filters={filters[cat]}
            toggle={toggleFilter[cat]}
          />
        ))}
      </div>
      <ProjectCards
        colorMap={colorMap}
        projects={data}
        filters={filters}
        toggleFilter={toggleFilter}
      />

      <div>
        <div>
          All of the data is taken from open sources (mostly social media, Github, app stores, teams websites and comms, gov proposals)
          some fields might be empty. We welcome you to update it as well, especially if you are part of the project.
        </div>
      </div>
    </div>
  );
}
