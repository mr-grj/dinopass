import { createTheme } from "@mui/material/styles";

import {
  BORDER,
  BORDER_DARK,
  BORDER_STRONG,
  GLOW,
  GLOW_SOFT,
  INFO,
  INK,
  OK,
  PAPER_DARK,
  SURFACE,
  TEXT_DISABLED,
  TEXT_ON_DARK,
  TEXT_ON_DARK_FAINT,
  TEXT_ON_DARK_MUTED,
  TEXT_SECONDARY,
  WARN,
  WEAK,
} from "./brand";

const SANS = "'Space Grotesk Variable', system-ui, sans-serif";
const MONO = "'Space Mono', ui-monospace, monospace";

export const createAppTheme = (mode) => {
  const dark = mode === "dark";

  const palette = dark
    ? {
        mode: "dark",
        primary: { main: GLOW, contrastText: INK },
        secondary: { main: GLOW, contrastText: INK },
        background: { default: INK, paper: PAPER_DARK },
        text: {
          primary: TEXT_ON_DARK,
          secondary: TEXT_ON_DARK_MUTED,
          disabled: TEXT_ON_DARK_FAINT,
        },
        divider: BORDER_DARK,
      }
    : {
        mode: "light",
        primary: { main: INK, contrastText: SURFACE },
        secondary: { main: GLOW, contrastText: INK },
        background: { default: SURFACE, paper: "#ffffff" },
        text: { primary: INK, secondary: TEXT_SECONDARY, disabled: TEXT_DISABLED },
        divider: BORDER,
      };

  return createTheme({
    palette: {
      ...palette,
      success: { main: OK },
      warning: { main: WARN },
      error: { main: WEAK },
      info: { main: INFO },
    },
    shape: { borderRadius: 8 },
    typography: {
      fontFamily: SANS,
      fontFamilyMonospace: MONO,
      h4: { fontWeight: 700, letterSpacing: "-0.01em" },
      h5: { fontWeight: 700, letterSpacing: "-0.01em" },
      h6: { fontWeight: 700 },
    },
    components: {
      MuiTooltip: {
        defaultProps: { disableInteractive: true, enterDelay: 400, enterNextDelay: 400 },
      },
      MuiButtonBase: {
        defaultProps: { disableRipple: true },
      },
      MuiAppBar: {
        styleOverrides: {
          root: { backgroundColor: INK, backgroundImage: "none", color: TEXT_ON_DARK },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 7,
            fontWeight: 600,
            letterSpacing: "0.04em",
            "&.Mui-focusVisible": { outline: `2px solid ${GLOW}`, outlineOffset: "2px" },
          },
          outlined: dark
            ? {
                backgroundColor: "transparent",
                borderColor: "rgba(255,255,255,0.22)",
                color: TEXT_ON_DARK,
                "&:hover": {
                  backgroundColor: "rgba(255,255,255,0.05)",
                  borderColor: TEXT_ON_DARK,
                },
              }
            : {
                backgroundColor: "#ffffff",
                borderColor: BORDER_STRONG,
                color: INK,
                "&:hover": { backgroundColor: "#ffffff", borderColor: INK },
              },
          contained: dark
            ? {
                "&:hover": { backgroundColor: GLOW_SOFT },
                "&.Mui-disabled": {
                  backgroundColor: "rgba(125,211,192,0.22)",
                  color: "rgba(11,11,12,0.5)",
                },
              }
            : undefined,
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            "&.Mui-focusVisible": { outline: `2px solid ${GLOW}`, outlineOffset: "2px" },
          },
        },
      },
      MuiDialog: {
        styleOverrides: { paper: { borderRadius: 14 } },
      },
    },
  });
};
