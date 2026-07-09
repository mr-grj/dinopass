import { useState } from "react";
import { useLocation } from "react-router-dom";
import {
  AppBar,
  Box,
  Button,
  Container,
  IconButton,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";

import { isAuth, removeKeyDerivation } from "../utils";
import { DEV_ACCENT, IS_DEV } from "../lib/appEnv";
import EnvBadge from "./EnvBadge";
import SettingsModal from "./SettingsModal";

const TopMenu = () => {
  const userIsAuth = isAuth();
  const { pathname } = useLocation();
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleLogout = () => {
    removeKeyDerivation();
    window.location.replace("/login");
  };

  return (
    <AppBar
      position="absolute"
      sx={IS_DEV ? { borderBottom: `3px solid ${DEV_ACCENT}` } : undefined}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Box sx={{ flexGrow: 1, display: "flex", alignItems: "center", gap: 1 }}>
            <Box
              component="img"
              src="/dino.svg"
              alt="dino"
              sx={{ height: 26, filter: "invert(1)", display: "block" }}
            />
            <Typography component="h1" variant="h6" noWrap sx={{ color: "inherit" }}>
              Dinopass
            </Typography>
            <EnvBadge />
          </Box>

          {userIsAuth ? (
            <>
              <Tooltip title="Settings">
                <IconButton color="inherit" onClick={() => setSettingsOpen(true)} sx={{ mr: 0.5 }}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Button color="inherit" onClick={handleLogout}>
                Log out
              </Button>
              <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
            </>
          ) : (
            pathname !== "/login" && (
              <Button href="/login" color="inherit">
                Log in
              </Button>
            )
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default TopMenu;
