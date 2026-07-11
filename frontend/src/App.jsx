import { useEffect } from "react";
import { BrowserRouter as Router, Navigate, Route, Routes } from "react-router-dom";
import { Box, Container, CssBaseline, GlobalStyles, Toolbar } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { useStoreActions } from "easy-peasy";

import TopMenu from "./components/TopMenu";
import useAutoLogout from "./hooks/useAutoLogout";
import routes from "./routes";
import { isAuth } from "./utils";
import {
  BORDER,
  BORDER_STRONG,
  GLOW,
  INFO,
  INK,
  OK,
  PAPER_DARK,
  SURFACE,
  TEXT_DISABLED,
  TEXT_ON_DARK,
  TEXT_SECONDARY,
  WARN,
  WEAK,
} from "./lib/brand";

const SANS = "'Space Grotesk Variable', system-ui, sans-serif";
const MONO = "'Space Mono', ui-monospace, monospace";

const theme = createTheme({
  palette: {
    primary: { main: INK, contrastText: SURFACE },
    secondary: { main: GLOW, contrastText: INK },
    success: { main: OK },
    warning: { main: WARN },
    error: { main: WEAK },
    info: { main: INFO },
    background: { default: SURFACE, paper: "#ffffff" },
    text: { primary: INK, secondary: TEXT_SECONDARY, disabled: TEXT_DISABLED },
    divider: BORDER,
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
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 7, fontWeight: 600, letterSpacing: "0.04em" },
        outlined: {
          backgroundColor: "#ffffff",
          borderColor: BORDER_STRONG,
          color: INK,
          "&:hover": { backgroundColor: "#ffffff", borderColor: INK },
        },
      },
    },
    MuiDialog: {
      styleOverrides: { paper: { borderRadius: 14 } },
    },
  },
});

const AppContent = () => {
  useAutoLogout();

  const authed = isAuth();
  const getSettings = useStoreActions((a) => a.ciphermothModels.settings.get);
  useEffect(() => {
    if (authed) getSettings();
  }, [authed, getSettings]);

  const appRoutes = (
    <Routes>
      {routes.map((route) => (
        <Route key={route.path} path={route.path} element={route.element} />
      ))}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );

  if (!authed) {
    return (
      <>
        <CssBaseline />
        {appRoutes}
      </>
    );
  }

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <TopMenu />
      <Box
        component="main"
        sx={{
          bgcolor: "background.default",
          flexGrow: 1,
          minHeight: "100vh",
          overflow: "auto",
        }}
      >
        <Toolbar />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          {appRoutes}
        </Container>
      </Box>
    </Box>
  );
};

const snackbarStyles = (
  <GlobalStyles
    styles={{
      // Toasts share a single dark surface with a coloured accent stripe so the
      // outcome reads at a glance without breaking the black-and-glow palette.
      ".notistack-MuiContent": {
        backgroundColor: `${PAPER_DARK} !important`,
        color: `${TEXT_ON_DARK} !important`,
        fontFamily: `${SANS} !important`,
        borderRadius: "10px !important",
        border: "1px solid rgba(255,255,255,0.12)",
      },
      ".notistack-MuiContent-success": { borderLeft: `3px solid ${GLOW} !important` },
      ".notistack-MuiContent-error": { borderLeft: `3px solid ${WEAK} !important` },
      ".notistack-MuiContent-warning": { borderLeft: `3px solid ${WARN} !important` },
      ".notistack-MuiContent-info": { borderLeft: `3px solid ${INFO} !important` },
    }}
  />
);

const App = () => (
  <Router>
    <ThemeProvider theme={theme}>
      {snackbarStyles}
      <AppContent />
    </ThemeProvider>
  </Router>
);

export default App;
