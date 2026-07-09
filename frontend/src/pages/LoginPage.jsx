import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  LinearProgress,
  Typography,
} from "@mui/material";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

import PasswordField from "../components/PasswordField";
import { getMasterPasswordStrength } from "../lib/passwordStrength";

const LoginPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  const { fetchStatus, check, create, setValue, setConfirm, setError } = useStoreActions(
    (a) => a.dinopassModels.masterPassword
  );
  const { initialized, error, value, confirm, loading } = useStoreState(
    (s) => s.dinopassModels.masterPassword
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
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "60vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "70vh",
      }}
    >
      <Box
        component="form"
        onSubmit={(e) => e.preventDefault()}
        sx={{
          width: "100%",
          maxWidth: 400,
          display: "flex",
          flexDirection: "column",
          gap: 2.5,
          p: { xs: 3, sm: 4 },
          bgcolor: "background.paper",
          borderRadius: 3,
          boxShadow: 3,
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 1,
            mb: 0.5,
          }}
        >
          <Box component="img" src="/dino.svg" alt="dino" sx={{ width: 64, height: 64 }} />
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            {initialized ? "Welcome back" : "Set up your vault"}
          </Typography>
          <Typography variant="body2" sx={{ color: "text.secondary", textAlign: "center" }}>
            {initialized
              ? "Enter your master password to unlock your vault."
              : "Create a master password to protect all your passwords."}
          </Typography>
        </Box>

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
        />

        {!initialized && value && strength && (
          <Box>
            <LinearProgress
              variant="determinate"
              value={strength.value}
              color={strength.color}
              sx={{ borderRadius: 1, height: 6 }}
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
          <PasswordField
            label="Confirm Master Password"
            required
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleCreate();
            }}
            autoComplete="new-password"
          />
        )}

        {!initialized && (
          <>
            <Alert severity="warning" variant="outlined" sx={{ py: 0.5 }}>
              <Typography variant="caption">
                There is no &ldquo;Forgot password&rdquo;. Losing your master password means losing
                access to your vault permanently.
              </Typography>
            </Alert>
            <FormControlLabel
              control={
                <Checkbox
                  size="small"
                  checked={acknowledged}
                  onChange={(e) => {
                    setAcknowledged(e.target.checked);
                    setError(null);
                  }}
                />
              }
              label={
                <Typography variant="caption">
                  I understand my master password cannot be recovered.
                </Typography>
              }
            />
          </>
        )}

        <Button
          fullWidth
          size="large"
          variant="contained"
          loading={loading}
          disabled={!initialized && !acknowledged}
          onClick={initialized ? handleLogin : handleCreate}
        >
          {initialized ? "Unlock Vault" : "Create Vault"}
        </Button>

        {!initialized && (
          <Typography variant="caption" sx={{ color: "text.secondary", textAlign: "center" }}>
            Closing this tab locks your vault. That is by design.
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default LoginPage;
