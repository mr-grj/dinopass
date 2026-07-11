import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import {
  AppBar,
  Box,
  Button,
  Chip,
  Container,
  IconButton,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import UpgradeIcon from "@mui/icons-material/Upgrade";
import { useStoreActions, useStoreState } from "easy-peasy";

import { isAuth, removeKeyDerivation } from "../utils";
import { DEV_ACCENT, IS_DEV } from "../lib/appEnv";
import { GLOW } from "../lib/brand";
import EnvBadge from "./EnvBadge";
import MothIcon from "./MothIcon";
import SettingsModal from "./SettingsModal";
import UpdateDialog from "./UpdateDialog";

const TopMenu = () => {
  const userIsAuth = isAuth();
  const { pathname } = useLocation();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [updateOpen, setUpdateOpen] = useState(false);

  const updateCheckEnabled = useStoreState(
    (s) => s.ciphermothModels.settings.settings.update_check_enabled
  );
  const updateAvailable = useStoreState((s) => s.ciphermothModels.updates.updateAvailable);
  const checkForUpdates = useStoreActions((a) => a.ciphermothModels.updates.checkForUpdates);

  // Browser-side check, only when authenticated and the user hasn't opted out.
  useEffect(() => {
    if (userIsAuth && updateCheckEnabled) checkForUpdates();
  }, [userIsAuth, updateCheckEnabled, checkForUpdates]);

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
            <Box sx={{ width: 24, height: 24, display: "flex", color: "inherit" }}>
              <MothIcon
                width="100%"
                height="100%"
                style={{ display: "block", overflow: "visible" }}
              />
            </Box>
            <Typography
              component="h1"
              variant="h6"
              noWrap
              sx={{ color: "inherit", fontWeight: 600 }}
            >
              Cipher
              <Box component="span" sx={{ color: GLOW }}>
                Moth
              </Box>
            </Typography>
            <EnvBadge />
          </Box>

          {userIsAuth ? (
            <>
              {updateAvailable && (
                <Tooltip title="A new CipherMoth release is available">
                  <Chip
                    icon={<UpgradeIcon sx={{ fontSize: 18 }} />}
                    label="Update"
                    size="small"
                    onClick={() => setUpdateOpen(true)}
                    sx={{
                      mr: 1,
                      bgcolor: GLOW,
                      color: "#0b0b0c",
                      fontWeight: 700,
                      cursor: "pointer",
                      "& .MuiChip-icon": { color: "#0b0b0c" },
                    }}
                  />
                </Tooltip>
              )}
              <Tooltip title="Settings">
                <IconButton color="inherit" onClick={() => setSettingsOpen(true)} sx={{ mr: 0.5 }}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Button color="inherit" onClick={handleLogout}>
                Log out
              </Button>
              <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
              <UpdateDialog open={updateOpen} onClose={() => setUpdateOpen(false)} />
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
