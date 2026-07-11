import { useEffect, useState } from "react";
import { Box, Button, Checkbox, FormControlLabel, LinearProgress, Typography } from "@mui/material";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

import LoadingScreen from "../components/LoadingScreen";
import MothIcon from "../components/MothIcon";
import PasswordField from "../components/PasswordField";
import { getMasterPasswordStrength } from "../lib/passwordStrength";
import {
  GLOW,
  GLOW_SOFT,
  INK,
  PAPER_DARK,
  TEXT_ON_DARK,
  TEXT_ON_DARK_MUTED,
  WARN,
} from "../lib/brand";

const darkFieldSx = {
  "& .MuiOutlinedInput-root": {
    color: TEXT_ON_DARK,
    "& fieldset": { borderColor: "rgba(255,255,255,0.16)" },
    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.3)" },
    "&.Mui-focused fieldset": { borderColor: GLOW, borderWidth: 2 },
  },
  "& .MuiInputLabel-root": { color: TEXT_ON_DARK_MUTED },
  "& .MuiInputLabel-root.Mui-focused": { color: GLOW },
  "& .MuiIconButton-root": { color: TEXT_ON_DARK_MUTED },
};

const unlockButtonSx = {
  bgcolor: GLOW,
  color: INK,
  fontWeight: 700,
  letterSpacing: "0.06em",
  py: 1.6,
  "&:hover": { bgcolor: GLOW_SOFT },
};

const LoginPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  const { fetchStatus, check, create, setValue, setConfirm, setError } = useStoreActions(
    (a) => a.ciphermothModels.masterPassword
  );
  const { initialized, error, value, confirm, loading } = useStoreState(
    (s) => s.ciphermothModels.masterPassword
  );

  useEffect(() => {
    fetchStatus();
    const notice = sessionStorage.getItem("logout_notice");
    if (notice) {
      sessionStorage.removeItem("logout_notice");
      enqueueSnackbar(notice, { variant: "info" });
    }
  }, [fetchStatus, enqueueSnackbar]);

  useEffect(() => {
    if (error) enqueueSnackbar(error, { variant: "error" });
  }, [error, enqueueSnackbar]);

  const [acknowledged, setAcknowledged] = useState(false);

  const strength = initialized === false ? getMasterPasswordStrength(value) : null;

  const handleLogin = () => {
    if (!value.trim()) {
      enqueueSnackbar("Please enter your master password.", { variant: "error" });
      return;
    }
    check({ master_password: value });
  };

  const handleCreate = () => {
    if (!value) {
      setError("Please enter a master password.");
      return;
    }
    if (value !== confirm) {
      setError("Passwords don't match.");
      return;
    }
    if (strength && strength.value < 70) {
      setError("Password is too weak. Use at least 12 characters with mixed types.");
      return;
    }
    if (!acknowledged) {
      setError("Please confirm you understand there is no password recovery.");
      return;
    }
    create({ master_password: value });
  };

  if (initialized === null) {
    return <LoadingScreen />;
  }

  return (
    <Box
      sx={{
        position: "fixed",
        inset: 0,
        bgcolor: INK,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 3,
        overflow: "auto",
        zIndex: (t) => t.zIndex.modal,
      }}
    >
      <Box
        component="form"
        onSubmit={(e) => e.preventDefault()}
        sx={{
          width: "100%",
          maxWidth: initialized ? 400 : 440,
          bgcolor: PAPER_DARK,
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 2,
          px: { xs: 3, sm: 4.25 },
          py: 5,
          textAlign: "center",
        }}
      >
        <Box
          sx={{
            width: 56,
            mx: "auto",
            mb: 2.25,
            color: TEXT_ON_DARK,
            filter: `drop-shadow(0 0 18px color-mix(in srgb, ${GLOW} 50%, transparent))`,
          }}
        >
          <MothIcon width="100%" height="100%" style={{ display: "block", overflow: "visible" }} />
        </Box>

        {initialized ? (
          <>
            <Typography sx={{ fontSize: 24, fontWeight: 700, color: TEXT_ON_DARK }}>
              Cipher
              <Box component="span" sx={{ color: GLOW }}>
                Moth
              </Box>
            </Typography>
            <Typography
              sx={{
                mt: 1,
                mb: 3.25,
                fontFamily: "'Space Mono', monospace",
                fontSize: 12,
                color: TEXT_ON_DARK_MUTED,
              }}
            >
              Your secrets stay in the dark.
            </Typography>
          </>
        ) : (
          <>
            <Typography sx={{ fontSize: 23, fontWeight: 700, color: TEXT_ON_DARK }}>
              Set up your vault
            </Typography>
            <Typography
              sx={{ mt: 1, mb: 3, fontSize: 13, color: TEXT_ON_DARK_MUTED, lineHeight: 1.5 }}
            >
              One master password protects everything. Choose it well. It is the only key.
            </Typography>
          </>
        )}

        <PasswordField
          label="Master Password"
          required
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && initialized) handleLogin();
          }}
          autoFocus
          autoComplete={initialized ? "current-password" : "new-password"}
          sx={darkFieldSx}
        />

        {!initialized && value && strength && (
          <Box sx={{ mt: 2, textAlign: "left" }}>
            <LinearProgress
              variant="determinate"
              value={strength.value}
              color={strength.color}
              sx={{ borderRadius: 1, height: 6, bgcolor: "rgba(255,255,255,0.1)" }}
            />
            <Typography
              variant="caption"
              color={`${strength.color}.main`}
              sx={{ mt: 0.5, display: "block" }}
            >
              {strength.label}
            </Typography>
          </Box>
        )}

        {!initialized && (
          <Box sx={{ mt: 2 }}>
            <PasswordField
              label="Confirm Master Password"
              required
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleCreate();
              }}
              autoComplete="new-password"
              sx={darkFieldSx}
            />
            <Box
              sx={{
                mt: 2,
                display: "flex",
                gap: 1.25,
                textAlign: "left",
                border: `1px solid ${WARN}`,
                bgcolor: "rgba(224,152,47,0.08)",
                borderRadius: 1.5,
                p: 1.6,
              }}
            >
              <Box component="span" sx={{ color: WARN, lineHeight: 1.4 }}>
                ⚠
              </Box>
              <Typography variant="caption" sx={{ color: WARN, lineHeight: 1.5 }}>
                There is no &ldquo;Forgot password&rdquo;. Lose your master password and the vault
                is gone, permanently. That is the trade for nobody-but-you holding the key.
              </Typography>
            </Box>
            <FormControlLabel
              sx={{ mt: 1, ml: 0, alignItems: "center" }}
              control={
                <Checkbox
                  size="small"
                  checked={acknowledged}
                  onChange={(e) => {
                    setAcknowledged(e.target.checked);
                    setError(null);
                  }}
                  sx={{ color: GLOW, "&.Mui-checked": { color: GLOW }, py: 0.25 }}
                />
              }
              label={
                <Typography variant="caption" sx={{ color: "#cfd2d4" }}>
                  I understand my master password cannot be recovered.
                </Typography>
              }
            />
          </Box>
        )}

        <Button
          fullWidth
          size="large"
          variant="contained"
          loading={loading}
          disabled={!initialized && !acknowledged}
          onClick={initialized ? handleLogin : handleCreate}
          sx={{ mt: 3, ...unlockButtonSx }}
        >
          {initialized ? "Unlock Vault" : "Create Vault"}
        </Button>

        <Typography sx={{ mt: 2.75, fontSize: 11, color: "#56585b" }}>
          Closing this tab locks your vault. That is by design.
        </Typography>
      </Box>
    </Box>
  );
};

export default LoginPage;
