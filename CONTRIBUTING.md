# 🤝 How To Contribute & Guidelines

We welcome you to independently verify the information and contribute to the dataset.

- Error reporting channels: GitHub Issue, PRs
- Listing new project: GitHub Issue, PRs
- Suggestions or questions: GitHub Issue

## Adding a new entity consists of two simple steps:

1. Fork the repository. Create a new markdown file in the directory with the copy of the template, filled with your details. 
2. Once you're done, create a pull request in the main repo. The pull request should only contain the Markdown file created from the template.

### Below is an example submission for Acala
```

name: Acala / Karura
category:
  - DeFi
description: DeFi platform that offers a suite of financial products and
  services, including lending, borrowing, staking, and trading, in a secure and
  scalable way. Acala is also Ethereum-compatible, making it easy for developers
  to bring their existing applications to the Polkadot ecosystem.
readiness:
  business: Scaling/Alliance
  technology: Connected to Relay chain
target_audience:
  - Dev teams
  - Startup
  - Personal investors
  - Institutional investors
  - Community DAO
ecosystem:
  - Polkadot
  - Acala Network
layer:
  - Layer-3
  - Layer-2
web:
  site: https://acala.network/
  twitter: AcalaNetwork
  discord: https://discord.com/invite/amxDHYvy
  contact: hello@acala.network
  github: https://github.com/AcalaNetwork/Acala
  documentation: https://wiki.acala.network
treasury_funded: false
audit: true

```

## Below are the available markdown headers for adding entities with guidelines for each header. 
Only input what is applicable for what you are adding.

- `name`: The project  name (will also be used as page name), cen be several names for different chains or products
- `category`: List of categories describing the project, each starts by dash and on the new line. 

        - API
        - Aggregator
        - Alerts
        - Analytics
        - Bridge
        - DAO
        - Dapp
        - Data
        - DeFi
        - DePIN
        - Education
        - EVM
        - Exchange
        - Game
        - Governance
        - Identity
        - Indexer
        - Infra
        - Linrary
        - Marketplace
        - Newsletter
        - NFT
        - Oracle
        - Privacy
        - Smart Contracts
        - Social
        - Staking
        - Tools
        - Validator provider
        - Wallet
        - XCM


- `description`: The short project description

- `Business readiness`: 

       - Business concept/low adoption
       - Verified in market/high adoption
       - Scaling/Alliance

- `Technology readiness`: 

       - In research
       - Validated POC / testnet
       - In development
       - In production
       - Connected to Relay chain
       - Connected to Parachain
       - Discontinued

- `Target audience`: A list of provisional users, each starts by dash and on the new line. 

| Commercial business unit | Non-commercial business unit |
| ------------------------ | ---------------------------- |
| Startup | Research Institute |
| Established corporation | Governmental organization |
| Institutional investor | Community DAO |
| Personal investor | Individuals|
| | Dev team |
  
- `ecosystem`: List of ecosystems. To add more, please reach out to the team.

       - Polkadot
       - Kusama
       - Acala Network
       - Moonbeam
       - Astar Network
       - Aleph Zero
       - Sora

- `Layer`: List of layers, each starts by dash and on the new line. [^1]

       - Layer-0 
       - Layer-1
       - Layer-2
       - Layer-3
       - Layer-4
       - None

[^1]: Layer definitions.
Layer 0 : protocol. 
Layer 1 : consensus (consensus, node operators, parachains).
Layer 2 : scaling (off-chain computing, messages, governance, bridges).
Layer 3 : smart contracts, dApps.
Layer 4 : identity, keys.

- `logo`: WIP
- `website`: URL to the project website
- `twitter`: Twitter handle without @
- `youtube`: Outdated
- `blog`: Outdated
- `documentation`: URL to the project documentation
- `github`: URL to the GitHub repo (in order to collect the number of stars the link should be to a specific repo)
- `discord`: Link to discord room
- `appstore`/`playstore`/`webstore`: links to the relevant stores
- `treasury_funded`: if was funded by Kusama/Polkadot treasury (true or false)
- `audit`: if security audited (true or false)

### The entry must contain at least:

- `name`
- `category`
- `description`
- `layer`
- `web`
  - `logo: default.png`
  - `site`


# Please don't change the README.md file, it is created automatically.
