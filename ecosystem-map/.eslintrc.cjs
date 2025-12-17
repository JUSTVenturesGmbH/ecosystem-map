module.exports = {
  parser: "@typescript-eslint/parser",
  parserOptions: {
    project: "./tsconfig.json",
    tsconfigRootDir: __dirname,
  },
  extends: ["airbnb", "airbnb-typescript", "prettier"],
  env: {
    browser: true,
    node: true,
  },
  plugins: ["@typescript-eslint", "import", "prettier", "react", "react-hooks"],
  rules: {
    "no-param-reassign": ["error", { props: false }],
  },
  settings: {
    "import/parsers": {
      "@typescript-eslint/parser": [".ts", ".tsx"],
    },
    "import/resolver": {
      typescript: {
        alwaysTryTypes: true,
      },
    },
  }
};
