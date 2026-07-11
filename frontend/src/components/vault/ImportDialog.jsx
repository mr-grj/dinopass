import { useEffect, useState } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";

import PasswordField from "../PasswordField";

const plural = (n) => (n !== 1 ? "s" : "");

const ImportResult = ({ result }) => {
  if (result.total === 0) {
    return (
      <Typography variant="body2" sx={{ color: "text.secondary" }}>
        No passwords found in the file.
      </Typography>
    );
  }
  return (
    <>
      {result.imported > 0 && (
        <Typography variant="body2">
          <strong>{result.imported}</strong> password{plural(result.imported)} added.
        </Typography>
      )}
      {result.overwritten > 0 && (
        <Typography variant="body2">
          <strong>{result.overwritten}</strong> password{plural(result.overwritten)} overwritten.
        </Typography>
      )}
      {result.skipped > 0 && (
        <Typography variant="body2" sx={{ color: "text.secondary" }}>
          <strong>{result.skipped}</strong> password{plural(result.skipped)} skipped (already
          exist).
        </Typography>
      )}
    </>
  );
};

const ImportDialog = ({ open, onClose, onImport, onImportCsv }) => {
  const [mode, setMode] = useState("ciphermoth");
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [onConflict, setOnConflict] = useState("skip");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (open) {
      setMode("ciphermoth");
      setFile(null);
      setPassword("");
      setError("");
      setOnConflict("skip");
      setResult(null);
    }
  }, [open]);

  const isCsv = mode === "csv";

  const changeMode = (_, next) => {
    if (!next) return;
    setMode(next);
    setFile(null);
    setError("");
  };

  const handleImport = async () => {
    if (!file) {
      setError(`Please select a ${isCsv ? "CSV" : "backup"} file.`);
      return;
    }
    if (!isCsv && !password.trim()) {
      setError("Master password is required.");
      return;
    }
    setLoading(true);
    try {
      const data = isCsv
        ? await onImportCsv({ file, onConflict })
        : await onImport({ file, masterPassword: password, onConflict });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={loading ? undefined : onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{result ? "Import Complete" : "Import Passwords"}</DialogTitle>
      <DialogContent>
        {result ? (
          <Stack spacing={1} sx={{ mt: 1 }}>
            <ImportResult result={result} />
          </Stack>
        ) : (
          <Stack spacing={2} sx={{ mt: 1 }}>
            <ToggleButtonGroup value={mode} exclusive onChange={changeMode} size="small" fullWidth>
              <ToggleButton value="ciphermoth" sx={{ textTransform: "none" }}>
                CipherMoth backup
              </ToggleButton>
              <ToggleButton value="csv" sx={{ textTransform: "none" }}>
                CSV from another app
              </ToggleButton>
            </ToggleButtonGroup>

            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              {isCsv
                ? "Upload a CSV exported from Chrome, Bitwarden, KeePass, Proton Pass and similar. Columns are matched automatically."
                : "Upload a CipherMoth backup ZIP and enter your master password to restore passwords."}
            </Typography>

            <Button
              component="label"
              variant="outlined"
              startIcon={<UploadFileIcon />}
              fullWidth
              sx={{ justifyContent: "flex-start", textTransform: "none" }}
            >
              {file ? file.name : isCsv ? "Choose CSV file (.csv)" : "Choose backup file (.zip)"}
              <input
                type="file"
                hidden
                accept={isCsv ? ".csv" : ".zip"}
                onChange={(e) => {
                  setFile(e.target.files[0] ?? null);
                  setError("");
                }}
              />
            </Button>

            {!isCsv && (
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
                  if (e.key === "Enter") handleImport();
                }}
              />
            )}

            {isCsv && error && (
              <Typography variant="body2" color="error">
                {error}
              </Typography>
            )}

            <FormControl>
              <FormLabel sx={{ fontSize: "0.875rem" }}>If a password already exists</FormLabel>
              <RadioGroup value={onConflict} onChange={(e) => setOnConflict(e.target.value)}>
                <FormControlLabel
                  value="skip"
                  control={<Radio size="small" />}
                  label="Keep existing (skip)"
                />
                <FormControlLabel
                  value="overwrite"
                  control={<Radio size="small" />}
                  label="Overwrite with imported value"
                />
              </RadioGroup>
            </FormControl>
          </Stack>
        )}
      </DialogContent>
      <DialogActions>
        {result ? (
          <Button variant="contained" onClick={onClose}>
            Done
          </Button>
        ) : (
          <>
            <Button onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button variant="contained" onClick={handleImport} loading={loading}>
              Import
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ImportDialog;
