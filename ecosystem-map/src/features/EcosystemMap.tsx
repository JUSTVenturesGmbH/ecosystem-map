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
const allowedEcosystems = new Set([
  "Acala Network",
  "Aleph Zero",
  "Astar Network",
  "Kusama",
  "Moonbeam",
  "Polkadot",
]);

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
  const [theme, setTheme] = React.useState<"light" | "dark">("light");
  
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
              if (allowedEcosystems.has(l)) {
                f.ecosystem[l] = false;
              }
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

  React.useEffect(() => {
    const stored = window.localStorage.getItem("theme");
    if (stored === "light" || stored === "dark") {
      setTheme(stored);
      return;
    }
    const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)")
      .matches;
    setTheme(prefersDark ? "dark" : "light");
  }, []);

  React.useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("theme", theme);
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((current) => (current === "light" ? "dark" : "light"));
  };

  return (
    <div className="page">
      <header className="site-header">
        <nav className="nav">
          <div className="brand">
            Ecosystem Map
            <span className="brand-badge">Polkadot</span>
          </div>
          <div className="nav-links">
            <a href="https://github.com/JUSTBeteiligungen/ecosystem-map">
              GitHub
            </a>
            <button
              type="button"
              className="mode-toggle"
              onClick={handleToggleTheme}
            >
              {theme === "light" ? "Dark mode" : "Light mode"}
            </button>
          </div>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-inner">
            <span className="eyebrow">Community-sourced directory</span>
            <h1 className="hero-title">
              The living map of Polkadot &amp; Kusama ecosystem projects.
            </h1>
            <p className="hero-subtitle">
              Curated by{" "}
              <a href="https://www.justventures.eu">JUST Ventures</a>. Filter by
              category, type, audience, and ecosystem to explore what is
              shipping across the network. This is a preview of our database,
              for further details please visit our Github.
            </p>
            <div className="hero-actions">
              <a
                className="primary-button"
                href="https://github.com/JUSTBeteiligungen/ecosystem-map"
              >
                Contribute on GitHub
              </a>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="section-inner">
            <div className="section-header">
              <h2 className="section-title">Explore the ecosystem</h2>
              <p className="section-description">
                Use the filters below to shape the data. Click chips to include
                or exclude clusters and trace the project landscape.
              </p>
            </div>
            <div className="filters-grid">
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
          </div>
        </section>

        <section className="section alt">
          <div className="section-inner">
            <div className="section-header">
              <h2 className="section-title">Project directory</h2>
              <p className="section-description">
                Browse every project in the dataset, including readiness status,
                activity signals, and key social touchpoints.
              </p>
            </div>
            <ProjectCards
              colorMap={colorMap}
              projects={data}
              filters={filters}
              toggleFilter={toggleFilter}
            />
          </div>
        </section>

        <section className="section">
          <div className="section-inner">
            <div className="section-header">
              <h2 className="section-title">About the data</h2>
              <p className="section-description">
                All of the data is taken from open sources (mostly social media,
                Github, app stores, teams websites and comms, gov proposals)
                some fields might be empty. We welcome you to update it as well,
                especially if you are part of the project.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <span>
            The directory is available for general information purposes only
            and is not an official endorsement of the projects by JUST team.
            Although we do our best to verify the data, there may be errors in
            the entries. Please check the details yourself.
          </span>
        </div>
      </footer>
    </div>
  );
}
