# 🤝 How To Contribute & Guidelines

We welcome you to independently verify the information and contribute to the dataset.

- Error reporting channels: GitHub Issue, PRs
- Listing new project: GitHub Issue, PRs
- Suggestions or questions: GitHub Issue

Adding a new entity consists of two simple steps:

1. Fork the repository. Create a new markdown file in the directory with the copy of the template, filled with your details. 
2. Once you're done, create a pull request in the main repo. The pull request should only contain the Markdown file created from the template.

Below is an example submission for Acala
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
layer:
  - Layer-3
web:
  site: https://acala.network/
  twitter: AcalaNetwork
  discord: https://discord.com/invite/amxDHYvy
  contact: hello@acala.network
  github: https://github.com/AcalaNetwork/Acala
  documentation: https://wiki.acala.network
treasury_funded: false
audit: true
metrics:

```

Below are the available markdown headers for adding entities with guidelines for each header (only input what is applicable for what you are adding):

- `name`: The project  name (will also be used as page name), cen be several names for different chains or products
- `category`: List of categories describing the project, each starts by dash and on the new line. [See the list](https://github.com/JUSTVenturesGmbH/ecosystem-map/tree/main?tab=readme-ov-file#category)
- `description`: The short project description
- `Business readiness`: Choose one from the [list](https://github.com/JUSTVenturesGmbH/ecosystem-map/tree/main?tab=readme-ov-file#business-readiness)
- `Technology readiness`: Choose one from the [list](https://github.com/JUSTVenturesGmbH/ecosystem-map/tree/main?tab=readme-ov-file#technology-readiness)
- `Target audience`: A list of provisional users, each starts by dash and on the new line. [See the list](https://github.com/JUSTVenturesGmbH/ecosystem-map/tree/main?tab=readme-ov-file#target-audience)
- `Layer`: List of layers, each starts by dash and on the new line. [See the list](https://github.com/JUSTVenturesGmbH/ecosystem-map/tree/main?tab=readme-ov-file#typelayer)
- `logo`: Outdated
- `website`: URL to the project website
- `twitter`: Twitter handle without @
- `youtube`: Outdated
- `blog`: Outdated
- `documentation`: URL to the project documentation
- `github`: URL to the GitHub page
- `discord`: Link to discord room
- `appstore`/`playstore`/`webstore`: links to the relevant stores
- `treasury_funded`: if was funded by Kusama/Polkadot treasury (true or false)
- `audit`: if security audited (true or false)


# Please don't change the README.md file, it is created automatically.
