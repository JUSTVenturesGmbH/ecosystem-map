export interface Web {
  site: string;
  logo: string;
  twitter?: string;
  blog?: string;
  discord?: string;
  github?: string;
  contact?: string;
  documentation?: string;
  playstore?: string;
  appstore?: string;
  webstore?: string;
}

export interface Readiness {
  technology: string;
  business: string;
}

export interface MetricsData {
  date: Date;
  value: number;
}

export interface Metrics {
  twitter?: MetricsData[];
  blog?: MetricsData[];
  youtube?: MetricsData[];
  discord?: MetricsData[];
  github?: MetricsData[];
  github_pushed_at?: MetricsData[];
  app_downloads?: MetricsData[];
}

export interface ProjectInfo {
  name: string;
  description: string;
  category?: string[];
  target_audience?: string[];
  ecosystem?: string[];
  layer: string[];
  web: Web;
  metrics?: Metrics;
  readiness?: Readiness;
  treasury_funded?: boolean;
  audit?: boolean;
}

export interface IFilters {
  category: {
    [key: string]: boolean;
  };
  target_audience: {
    [key: string]: boolean;
  };
  ecosystem: {
    [key: string]: boolean;
  };
  status: {
    [key: string]: boolean;
  };
}

export type TCategory = keyof IFilters;

export interface IColorMap {
  [key: string]: string;
}
