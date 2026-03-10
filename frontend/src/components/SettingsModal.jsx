import { useEffect, useState } from "react";
import {
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  InputAdornment,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

const FIELDS = [
  {
    key: "inactivity_ms",
    label: "Inactivity timeout",
    tooltip: "How long the app waits without any user activity before logging you out automatically.",
    min: 30,
    max: 3600,
  },
  {
    key: "warn_before_ms",
    label: "Warning before logout",
    tooltip: "How far in advance of the inactivity timeout a warning is shown. Must be less than the inactivity timeout.",
    min: 5,
    max: 600,
  },
  {
    key: "hidden_ms",
    label: "Hidden tab timeout",
    tooltip: "How long the tab can stay in the background (minimised or switched away) before you are logged out.",
    min: 10,
    max: 3600,
  },
  {
    key: "debounce_ms",
    label: "Activity debounce",
    tooltip: "Minimum interval between activity detections. Prevents the inactivity timer from being reset too aggressively.",
    min: 1,
    max: 10,
  },
  {
    key: "clipboard_clear_ms",
    label: "Clipboard clear delay",
    tooltip: "How long after copying a password the clipboard is automatically wiped.",
    min: 5,
    max: 600,
  },
];

const toSec = (ms) => Math.round(ms / 1000);
const toMs = (sec) => Math.round(Number(sec)) * 1000;

const toForm = (settings) =>
  Object.fromEntries(FIELDS.map(({ key }) => [key, toSec(settings[key])]));

const isDirty = (form, settings) =>
  FIELDS.some(({ key }) => Number(form[key]) !== toSec(settings[key]));

const SettingsModal = ({ open, onClose }) => {
  const { enqueueSnackbar } = useSnackbar();

  const { update } = useStoreActions((a) => a.dinopassModels.settings);
  const settings = useStoreState((s) => s.dinopassModels.settings.settings);

  const [form, setForm] = useState(() => toForm(settings));
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      setForm(toForm(settings));
      setFormError("");
    }
  }, [open, settings]);

  const handleChange = (key) => (e) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }));
    setFormError("");
  };

  const handleSave = async () => {
    if (Number(form.warn_before_ms) >= Number(form.inactivity_ms)) {
      setFormError("Warning before logout must be less than the inactivity timeout.");
      return;
    }
    setSaving(true);
    try {
      await update(Object.fromEntries(FIELDS.map(({ key }) => [key, toMs(form[key])])));
      enqueueSnackbar("Settings saved.", { variant: "success" });
      onClose();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const dirty = isDirty(form, settings);

  return (
    <Dialog open={open} onClose={saving ? undefined : onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Settings</DialogTitle>
      <DialogContent>
        <Stack spacing={2} mt={1}>
          {FIELDS.map(({ key, label, tooltip, min, max }) => (
            <TextField
              key={key}
              label={label}
              type="number"
              value={form[key]}
              onChange={handleChange(key)}
              fullWidth
              inputProps={{ min, max, step: 1 }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Tooltip title={tooltip} arrow placement="top">
                      <HelpOutlineIcon fontSize="small" sx={{ color: "text.disabled", cursor: "help" }} />
                    </Tooltip>
                  </InputAdornment>
                ),
              }}
              helperText="seconds"
            />
          ))}
          {formError && (
            <Typography variant="body2" color="error">{formError}</Typography>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={saving}>Cancel</Button>
        <Button variant="contained" onClick={handleSave} disabled={saving || !dirty}>
          {saving ? <CircularProgress size={20} /> : "Save"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SettingsModal;
