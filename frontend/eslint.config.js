import js from "@eslint/js";
import globals from "globals";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";

export default [
  { ignores: ["dist", "build", "node_modules"] },
  js.configs.recommended,
  react.configs.flat.recommended,
  react.configs.flat["jsx-runtime"],
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    settings: { react: { version: "detect" } },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      // Classic, stable hooks rules. I intentionally don't enable the newer
      // React Compiler ruleset (set-state-in-effect, etc.) -> this app isn't
      // compiled and those rules flag idiomatic MUI dialog/render patterns.
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
      // The app uses runtime prop shapes, not PropTypes.
      "react/prop-types": "off",
    },
  },
  {
    // Build/tooling config files run in Node, not the browser.
    files: ["*.config.js"],
    languageOptions: { globals: globals.node },
  },
];
