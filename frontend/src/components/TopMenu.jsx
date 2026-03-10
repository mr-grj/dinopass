import { useState } from "react";
import { useLocation } from "react-router-dom";
import { AppBar, Box, Button, IconButton, Toolbar, Tooltip, Typography } from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";

import { isAuth, removeKeyDerivation } from "../utils";
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
    <AppBar position="absolute">
      <Toolbar sx={{ pr: "24px" }}>
        <Typography
          component="h1"
          variant="h6"
          color="inherit"
          noWrap
          sx={{ flexGrow: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <Box
            component="img"
            src="/dino.svg"
            alt="dino"
            sx={{ height: 26, filter: "invert(1)", display: "block" }}
          />
          Dinopass
        </Typography>

        {userIsAuth ? (
          <>
            <Tooltip title="Settings">
              <IconButton
                color="inherit"
                onClick={() => setSettingsOpen(true)}
                sx={{ mr: 0.5 }}
              >
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
    </AppBar>
  );
};

export default TopMenu;
