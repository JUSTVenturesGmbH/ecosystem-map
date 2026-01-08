import React from "react";
import ChipFilterBlock from "./ChipFilterBlock";
import { IColorMap, IFilters, ProjectInfo } from "../types";
import { cats, colors } from "../utils/helper";
import ProjectCards from "./ProjectCards";
import Chip from "./Chip";

interface ISortState {
  column: keyof ProjectInfo;
  asc: boolean;
}
const catMapping: { [P in keyof IFilters]: string } = {
  category: "Category",
  status: "Status",
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
const categoryGroups = [
  {
    title: "Infrastructure",
    items: [
      "API",
      "Data",
      "Indexer",
      "Infra",
      "Library",
      "Oracle",
      "Tools",
      "XCM",
      "Bridge",
      "Smart Contracts",
      "EVM",
    ],
  },
  {
    title: "Finance & Markets",
    items: [
      "DeFi",
      "Exchange",
      "Staking",
      "Wallet",
      "Marketplace",
      "Aggregator",
    ],
  },
  {
    title: "Community & Governance",
    items: [
      "DAO",
      "Governance",
      "Identity",
      "Privacy",
      "Social",
      "Newsletter",
      "Alerts",
      "Education",
      "Video",
    ],
  },
  {
    title: "Apps & Experiences",
    items: ["Dapp", "Game", "NFT", "DePIN"],
  },
];
const statusOrder = [
  "Connected to Relay chain",
  "Connected to Parachain",
  "In production",
  "In development",
  "Validated POC / testnet",
  "In research",
  "Discontinued",
];
const ecosystemOrder = ["Polkadot", "Kusama"];

function GithubIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      height="16"
      width="16"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M8 0.198c-4.418 0-8 3.582-8 8 0 3.535 2.292 6.533 5.471 7.591 0.4 0.074 0.547-0.174 0.547-0.385 0-0.191-0.008-0.821-0.011-1.489-2.226 0.484-2.695-0.944-2.695-0.944-0.364-0.925-0.888-1.171-0.888-1.171-0.726-0.497 0.055-0.486 0.055-0.486 0.803 0.056 1.226 0.824 1.226 0.824 0.714 1.223 1.872 0.869 2.328 0.665 0.072-0.517 0.279-0.87 0.508-1.070-1.777-0.202-3.645-0.888-3.645-3.954 0-0.873 0.313-1.587 0.824-2.147-0.083-0.202-0.357-1.015 0.077-2.117 0 0 0.672-0.215 2.201 0.82 0.638-0.177 1.322-0.266 2.002-0.269 0.68 0.003 1.365 0.092 2.004 0.269 1.527-1.035 2.198-0.82 2.198-0.82 0.435 1.102 0.162 1.916 0.079 2.117 0.513 0.56 0.823 1.274 0.823 2.147 0 3.073-1.872 3.749-3.653 3.947 0.287 0.248 0.543 0.735 0.543 1.481 0 1.070-0.009 1.932-0.009 2.195 0 0.213 0.144 0.462 0.55 0.384 3.177-1.059 5.466-4.057 5.466-7.59 0-4.418-3.582-8-8-8z" />
    </svg>
  );
}

export default function EcosystemMap() {
  const [ecosystemProjects, setEcosystemProjects] = React.useState<
    ProjectInfo[]
  >([]);
  const [data, setData] = React.useState<ProjectInfo[]>([]);
  const [filters, setFilters] = React.useState<IFilters>({
    category: {},
    status: {},
    target_audience: {}, 
    ecosystem: {},
  });
  const [query, setQuery] = React.useState<string>("");
  const [colorMap, setColorMap] = React.useState<IColorMap>({});
  const [theme, setTheme] = React.useState<"light" | "dark">("light");
  const [counts, setCounts] = React.useState<{
    category: { [key: string]: number };
    status: { [key: string]: number };
    target_audience: { [key: string]: number };
    ecosystem: { [key: string]: number };
  }>({ category: {}, status: {}, target_audience: {}, ecosystem: {} });
  
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
    const status = Object.keys(filters.status).filter((k) => filters.status[k]);
    const audience = Object.keys(filters.target_audience).filter(
      (k) => filters.target_audience[k],
    );
    const ecosystem = Object.keys(filters.ecosystem).filter((k) => filters.ecosystem[k]);
    const search = query.trim().toLowerCase();

    setData(
      ecosystemProjects.filter(
        (p) =>
          category.every((c) => p.category?.find((d) => d === c)) &&
          status.every((c) => p.readiness?.technology === c) &&
          audience.every((c) => p.target_audience?.find((d) => d === c)) &&
          ecosystem.every((c) => p.ecosystem?.find((d) => d === c)) &&
          (!search ||
            p.name.toLowerCase().includes(search) ||
            p.description.toLowerCase().includes(search))
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
    status: (k: string) => toggleFilterByCategory("status", k),
    target_audience: (k: string) =>
      toggleFilterByCategory("target_audience", k),
    ecosystem: (k: string) => toggleFilterByCategory("ecosystem", k),
  };

  React.useEffect(() => {
    const url = "projects.json";

    fetch(url)
      .then((res) => res.json())
      .then((d) => {
        const f: IFilters = {
          category: {},
          status: {},
          target_audience: {},
          ecosystem: {},
        };
        const countMap = {
          category: {} as { [key: string]: number },
          status: {} as { [key: string]: number },
          target_audience: {} as { [key: string]: number },
          ecosystem: {} as { [key: string]: number },
        };

        d.forEach((c: ProjectInfo) => {
          c?.category?.forEach((l) => {
            if (l) {
              f.category[l] = false;
              countMap.category[l] = (countMap.category[l] ?? 0) + 1;
            }
          });

          if (c?.readiness?.technology) {
            f.status[c.readiness.technology] = false;
            countMap.status[c.readiness.technology] =
              (countMap.status[c.readiness.technology] ?? 0) + 1;
          }

          c?.target_audience?.forEach((l) => {
            if (l) {
              f.target_audience[l] = false;
              countMap.target_audience[l] =
                (countMap.target_audience[l] ?? 0) + 1;
            }
          });

          c?.ecosystem?.forEach((l) => {
            if (l) {
              if (allowedEcosystems.has(l)) {
                f.ecosystem[l] = false;
                countMap.ecosystem[l] = (countMap.ecosystem[l] ?? 0) + 1;
              }
            }
          });
        });
        setFilters(f);
        setCounts(countMap);

        const c: { [key: string]: string } = {};

        [
          ...Object.keys(f.category),
          ...Object.keys(f.status),
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

  React.useEffect(() => filterProjects(), [filters, ecosystemProjects, query]);

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
                <span className="button-icon">
                  <GithubIcon />
                </span>
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
              <div className="filter-block">
                <h3 className="filter-title">{catMapping.category}</h3>
                <div className="category-groups">
                  {categoryGroups
                    .map((group) => ({
                      title: group.title,
                      items: group.items.filter(
                        (item) => filters.category[item] !== undefined,
                      ),
                    }))
                    .filter((group) => group.items.length > 0)
                    .map((group) => (
                      <div className="category-group" key={group.title}>
                        <div className="category-group-title">
                          {group.title}
                        </div>
                        <div className="chip-block">
                          {group.items.map((item) => (
                            <div className="chip-row" key={item}>
                              <Chip
                                label={item}
                                filters={filters.category}
                                colorMap={colorMap}
                                toggle={toggleFilter.category}
                              />
                              {typeof counts.category[item] === "number" ? (
                                <span className="chip-count-label">
                                  {counts.category[item]}
                                </span>
                              ) : null}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  {Object.keys(filters.category).some(
                    (item) =>
                      !categoryGroups.some((group) =>
                        group.items.includes(item),
                      ),
                  ) ? (
                    <div className="category-group">
                      <div className="category-group-title">Other</div>
                      <div className="chip-block">
                        {Object.keys(filters.category)
                          .filter(
                            (item) =>
                              !categoryGroups.some((group) =>
                                group.items.includes(item),
                              ),
                          )
                          .sort()
                          .map((item) => (
                            <div className="chip-row" key={item}>
                              <Chip
                                label={item}
                                filters={filters.category}
                                colorMap={colorMap}
                                toggle={toggleFilter.category}
                              />
                              {typeof counts.category[item] === "number" ? (
                                <span className="chip-count-label">
                                  {counts.category[item]}
                                </span>
                              ) : null}
                            </div>
                          ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>
              {cats
                .filter((cat) => cat !== "category")
                .map((cat) => (
                  <ChipFilterBlock
                    key={catMapping[cat]}
                    name={catMapping[cat]}
                    colorMap={colorMap}
                    filters={filters[cat]}
                    toggle={toggleFilter[cat]}
                    counts={counts[cat]}
                    order={
                      cat === "status"
                        ? statusOrder
                        : cat === "ecosystem"
                          ? ecosystemOrder
                          : undefined
                    }
                  />
                ))}
            </div>
            <div className="search-bar">
              <label className="search-label" htmlFor="project-search">
                Search projects
              </label>
              <input
                id="project-search"
                className="search-input"
                type="search"
                placeholder="Search by name or description"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
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
            <div className="results-label">Search results</div>
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
