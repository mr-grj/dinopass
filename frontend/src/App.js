import { useEffect } from "react";
import { BrowserRouter as Router, Navigate, Route, Routes } from "react-router-dom";
import { Box, Container, CssBaseline, GlobalStyles, Toolbar } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { useStoreActions } from "easy-peasy";

import TopMenu from "./components/TopMenu";
import useAutoLogout from "./hooks/useAutoLogout";
import routes from "./routes";
import { isAuth } from "./utils";

const theme = createTheme({
  palette: {
    primary: {
      main: "#000000",
      contrastText: "#ffffff",
    },
  },
});

const AppContent = () => {
  useAutoLogout();

  const getSettings = useStoreActions((a) => a.dinopassModels.settings.get);
  useEffect(() => {
    if (isAuth()) getSettings();
  }, [getSettings]);

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <TopMenu />
      <Box
        component="main"
        sx={{
          backgroundColor: (t) =>
            t.palette.mode === "light" ? t.palette.grey[100] : t.palette.grey[900],
          flexGrow: 1,
          height: "100vh",
          overflow: "auto",
        }}
      >
        <Toolbar />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            {routes.map((route) => (
              <Route key={route.path} path={route.path} element={route.element} />
            ))}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

const snackbarStyles = (
  <GlobalStyles
    styles={{
      ".notistack-MuiContent-success, .notistack-MuiContent-warning, .notistack-MuiContent-info": {
        backgroundColor: "#000000 !important",
        color: "#ffffff !important",
      },
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
