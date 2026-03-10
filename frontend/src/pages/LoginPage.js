import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  CircularProgress,
  IconButton,
  InputAdornment,
  LinearProgress,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

import DinoLoadingButton from "../components/DinoLoadingButton";

const getStrength = (password) => {
  if (!password) return null;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);
  const variety = [hasUpper, hasLower, hasNumber, hasSpecial].filter(Boolean).length;
  if (password.length < 8) return { label: "Too short", value: 20, color: "error" };
  if (password.length < 12 || variety < 2) return { label: "Weak", value: 40, color: "error" };
  if (password.length < 16 || variety < 3) return { label: "Fair", value: 70, color: "warning" };
  return { label: "Strong", value: 100, color: "success" };
};

const PasswordField = ({ label, value, onChange, onKeyDown, autoFocus }) => {
  const [show, setShow] = useState(false);
  return (
    <TextField
      fullWidth
      required
      label={label}
      type={show ? "text" : "password"}
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      autoFocus={autoFocus}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <Tooltip title={show ? "Hide" : "Show"}>
              <IconButton onClick={() => setShow((v) => !v)} edge="end" size="small">
                {show ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </InputAdornment>
        ),
      }}
    />
  );
};

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

  const strength = initialized === false ? getStrength(value) : null;

  const handleLogin = () => {
    if (!value.trim()) { enqueueSnackbar("Please enter your master password.", { variant: "error" }); return; }
    check({ master_password: value });
  };

  const handleCreate = () => {
    if (!value) { setError("Please enter a master password."); return; }
    if (value !== confirm) { setError("Passwords don't match."); return; }
    if (strength && strength.value < 70) { setError("Password is too weak. Use at least 12 characters with mixed types."); return; }
    create({ master_password: value });
  };

  // Still checking status
  if (initialized === null) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="70vh"
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
        {/* Icon + heading */}
        <Box display="flex" flexDirection="column" alignItems="center" gap={1} mb={0.5}>
          <Box component="img" src="/dino.svg" alt="dino" sx={{ width: 64, height: 64 }} />
          <Typography variant="h6" fontWeight={700}>
            {initialized ? "Welcome back" : "Set up your vault"}
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            {initialized
              ? "Enter your master password to unlock your vault."
              : "Create a master password to protect all your passwords."}
          </Typography>
        </Box>

        {/* Password field */}
        <PasswordField
          label="Master Password"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && initialized) handleLogin(); }}
          autoFocus
        />

        {!initialized && value && strength && (
          <Box>
            <LinearProgress
              variant="determinate"
              value={strength.value}
              color={strength.color}
              sx={{ borderRadius: 1, height: 6 }}
            />
            <Typography variant="caption" color={`${strength.color}.main`} mt={0.5} display="block">
              {strength.label}
            </Typography>
          </Box>
        )}

        {!initialized && (
          <PasswordField
            label="Confirm Master Password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleCreate(); }}
          />
        )}

        {!initialized && (
          <Alert severity="warning" variant="outlined" sx={{ py: 0.5 }}>
            <Typography variant="caption">
              There is no "Forgot password". Losing your master password means losing access to your vault permanently.
            </Typography>
          </Alert>
        )}

        {/* Submit */}
        <DinoLoadingButton
          fullWidth
          buttonText={initialized ? "Unlock Vault" : "Create Vault"}
          loading={loading}
          onClick={initialized ? handleLogin : handleCreate}
        />
      </Box>
    </Box>
  );
};

export default LoginPage;
