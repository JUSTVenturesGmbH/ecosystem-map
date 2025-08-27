# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Polkadot Ecosystem Map - a community-sourced directory of projects in the Polkadot ecosystem. It consists of:

1. **Data Layer**: YAML files in `/data/` containing structured project information
2. **Web Interface**: React-based visualization in `/ecosystem-map/` 
3. **Python Scripts**: Data processing and validation in `/scripts/`

## Common Commands

### Frontend Development (ecosystem-map/)
```bash
cd ecosystem-map
npm run start          # Start dev server (localhost:3000)
npm run build          # Production build
npm run typecheck      # TypeScript type checking
npm run lint           # ESLint
npm run lint:fix       # Auto-fix ESLint issues
npm run lint:yaml      # Validate YAML data files
npm run stylelint      # CSS linting
npm run stylelint:fix  # Auto-fix CSS issues
```

### Data Validation
```bash
cd scripts
bash validate.sh       # Validate all YAML files against schema
```

### Python Scripts
```bash
cd scripts
pip install -r requirements.txt
python render_map.py   # Generate README tables from YAML data
python metrics.py      # Process metrics data
```

## Architecture

### Data Structure
- Each project is a YAML file in `/data/` following `data.schema.yml`
- Required fields: name, description, web (site, logo), layer
- Optional: category, ecosystem, target_audience, readiness, metrics, treasury_funded, audit
- Schema validation ensures data consistency

### Frontend Components
- **EcosystemMap.tsx**: Main container with filtering and sorting logic
- **ProjectCards.tsx**: Grid view of project cards  
- **ChipFilterBlock.tsx**: Filter UI components
- **Card.tsx**: Individual project card component
- **MetricsPanel.tsx**: Displays project metrics

### Data Processing Flow
1. YAML files in `/data/` → validated against schema
2. `combineYAMLs.ts` → merges into single JSON structure
3. `transform-data.js` → processes for frontend consumption
4. React app → renders interactive interface

### Build System
- **Development**: esbuild with hot reload via `build.dev.js`
- **Production**: Minified build via `build.prod.js`
- **Assets**: Static files in `public/` copied to output

## Data Schema Key Points

Projects must include:
- Ecosystem (Polkadot, Kusama, etc.)
- Layer (Layer-0 through Layer-4, None)
- Category (API, DeFi, Tools, etc.)
- Technology readiness (research → testnet → production → parachain)
- Business readiness (concept → market validation → scaling)

## Contributing Process
1. New projects: Create YAML file from template in `/data/`
2. Validation: Run `npm run lint:yaml` from ecosystem-map/
3. The project maintains historical data including discontinued projects
4. Images go in `/img/` with same name as YAML file

## Development Tips
- Always validate YAML changes before committing
- Frontend uses TypeScript with strict type checking
- CSS follows standard guidelines with Stylelint
- Python scripts use Black formatter
- The schema is strictly enforced - follow existing patterns