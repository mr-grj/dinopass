import { useEffect, useState } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
} from "@mui/material";

import PasswordField from "../PasswordField";

const BackupDialog = ({ open, onClose, onBackup }) => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      setPassword("");
      setError("");
    }
  }, [open]);

  const handleBackup = async () => {
    if (!password.trim()) {
      setError("Master password is required.");
      return;
    }
    setLoading(true);
    try {
      await onBackup(password);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={loading ? undefined : onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Create Backup</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Typography variant="body2" sx={{ color: "text.secondary" }}>
            Your passwords will be exported as an AES-256 encrypted ZIP file. Open it with your
            master password.
          </Typography>
          <PasswordField
            label="Master Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setError("");
            }}
            error={!!error}
            helperText={error}
            required
            autoFocus
            autoComplete="current-password"
            onKeyDown={(e) => {
              if (e.key === "Enter") handleBackup();
            }}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button variant="contained" onClick={handleBackup} loading={loading}>
          Create Backup
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BackupDialog;
