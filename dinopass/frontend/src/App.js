import * as React from "react";
import Box from "@mui/material/Box";
import {createTheme} from "@mui/material/styles";
import {ThemeProvider} from "@emotion/react";
import CssBaseline from "@mui/material/CssBaseline";
import TopMenu from "./components/TopMenu";
import LeftMenu from "./components/Drawer";
import Toolbar from "@mui/material/Toolbar";
import Container from "@mui/material/Container";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import routes from "./routes";

const mdTheme = createTheme();

const App = () => (
  <div className="App">
    <Router>
      <ThemeProvider theme={mdTheme}>
        <Box sx={{display: 'flex'}}>
          <CssBaseline/>
          <TopMenu/>
          <LeftMenu/>
          <Box
            component="main"
            sx={{
              backgroundColor: (theme) =>
                theme.palette.mode === 'light'
                  ? theme.palette.grey[100]
                  : theme.palette.grey[900],
              flexGrow: 1,
              height: '100vh',
              overflow: 'auto',
            }}
          >
            <Toolbar/>

            <Container maxWidth="lg" sx={{mt: 4, mb: 4}}>
              <Routes>
                {routes.map((route, index) => (
                  <Route
                    key={index}
                    path={route.path}
                    exact={route.exact}
                    element={<route.main/>}
                  />
                ))}
              </Routes>


            </Container>
          </Box>

        </Box>

      </ThemeProvider>

    </Router>

  </div>
)

export default App;