import { useEffect, useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
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

const SettingsPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  const { get, update } = useStoreActions((a) => a.dinopassModels.settings);
  const { settings, loading } = useStoreState((s) => s.dinopassModels.settings);

  const [form, setForm] = useState(null);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (settings) {
      setForm({
        inactivity_ms: toSec(settings.inactivity_ms),
        warn_before_ms: toSec(settings.warn_before_ms),
        hidden_ms: toSec(settings.hidden_ms),
        debounce_ms: toSec(settings.debounce_ms),
        clipboard_clear_ms: toSec(settings.clipboard_clear_ms),
      });
    }
  }, [settings]);

  useEffect(() => {
    get();
  }, [get]);

  const handleChange = (key) => (e) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }));
    setFormError("");
  };

  const handleSave = async () => {
    const inactivity = Number(form.inactivity_ms);
    const warnBefore = Number(form.warn_before_ms);

    if (warnBefore >= inactivity) {
      setFormError("Warning before logout must be less than the inactivity timeout.");
      return;
    }

    setSaving(true);
    try {
      await update({
        inactivity_ms: toMs(form.inactivity_ms),
        warn_before_ms: toMs(form.warn_before_ms),
        hidden_ms: toMs(form.hidden_ms),
        debounce_ms: toMs(form.debounce_ms),
        clipboard_clear_ms: toMs(form.clipboard_clear_ms),
      });
      enqueueSnackbar("Settings saved.", { variant: "success" });
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !form) {
    return (
      <Box display="flex" justifyContent="center" mt={8}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={700} lineHeight={1.2}>
            Settings
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            Configure security and session behaviour.
          </Typography>
        </Box>
      </Stack>

      <Box
        sx={{
          bgcolor: "background.paper",
          borderRadius: 2,
          p: 3,
        }}
      >
        <Stack spacing={2.5}>
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

          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving}
            sx={{ alignSelf: "flex-start" }}
          >
            {saving ? <CircularProgress size={20} /> : "Save"}
          </Button>
        </Stack>
      </Box>
    </Box>
  );
};

export default SettingsPage;
