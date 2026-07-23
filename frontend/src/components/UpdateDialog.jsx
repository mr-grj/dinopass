import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Link,
  Stack,
  Typography,
} from "@mui/material";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

import { GLOW } from "../lib/brand";

const DONE = new Set(["success", "failed", "rolled_back"]);
const POLL_MS = 3000;
const TIMEOUT_MS = 6 * 60 * 1000;

const STATE_COPY = {
  requested: "Starting…",
  verifying: "Verifying image signatures…",
  applying: "Applying update and restarting…",
  success: "Updated. Reloading…",
  failed: "Update failed, your vault is untouched.",
  rolled_back: "Update failed and was rolled back, you're on the previous version.",
};

const UpdateDialog = ({ open, onClose }) => {
  const { enqueueSnackbar } = useSnackbar();

  const { current, latest, releaseUrl } = useStoreState((s) => s.ciphermothModels.updates);
  const apply = useStoreState((s) => s.ciphermothModels.updates.apply);
  const { applyUpdate, fetchApplyStatus, checkForUpdates } = useStoreActions(
    (a) => a.ciphermothModels.updates
  );

  const [busy, setBusy] = useState(false);

  const updaterPresent = apply?.updater_present;

  useEffect(() => {
    if (open) fetchApplyStatus();
  }, [open, fetchApplyStatus]);

  useEffect(() => {
    if (!busy) return undefined;

    const deadline = Date.now() + TIMEOUT_MS;
    let done = false;
    const finish = (fn) => {
      if (done) return;
      done = true;
      clearInterval(id);
      fn();
    };

    const tick = async () => {
      const status = await fetchApplyStatus();
      const state = status?.state;
      if (state && DONE.has(state)) {
        finish(() => {
          if (state === "success") {
            enqueueSnackbar("Update complete. Reloading…", { variant: "success" });
            setTimeout(() => window.location.reload(), 1500);
          } else {
            setBusy(false);
            enqueueSnackbar(STATE_COPY[state], { variant: "error" });
          }
        });
      } else if (Date.now() > deadline) {
        finish(() => {
          setBusy(false);
          checkForUpdates();
          enqueueSnackbar("Still updating in the background, refresh in a moment.", {
            variant: "info",
          });
        });
      }
    };

    const id = setInterval(tick, POLL_MS);
    tick();
    return () => {
      done = true;
      clearInterval(id);
    };
  }, [busy, fetchApplyStatus, enqueueSnackbar, checkForUpdates]);

  const handleApply = async () => {
    setBusy(true);
    try {
      await applyUpdate(latest);
    } catch (err) {
      setBusy(false);
      enqueueSnackbar(err.message, { variant: "error" });
    }
  };

  const inProgress = busy || (apply?.state && !DONE.has(apply.state) && apply.state !== "idle");

  const manualCommand =
    "docker compose -f docker-compose.prod.yml pull && \\\n" +
    "docker compose -f docker-compose.prod.yml up -d";

  return (
    <Dialog open={open} onClose={inProgress ? undefined : onClose} maxWidth="xs" fullWidth>
      <DialogTitle>A new moult is ready</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 0.5 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip label={current ? `v${String(current).replace(/^v/, "")}` : "-"} size="small" />
            <Typography sx={{ color: "text.disabled" }}>→</Typography>
            <Chip
              label={latest ?? "-"}
              size="small"
              sx={{ bgcolor: GLOW, color: "#0b0b0c", fontWeight: 700 }}
            />
          </Stack>

          {releaseUrl && (
            <Link href={releaseUrl} target="_blank" rel="noopener noreferrer" variant="body2">
              Read the release notes on GitHub
            </Link>
          )}

          {inProgress ? (
            <Alert severity="info">{STATE_COPY[apply?.state] ?? "Working…"}</Alert>
          ) : updaterPresent ? (
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              CipherMoth will verify the new images are signed by the official release, back up your
              database, restart, and roll back automatically if anything looks wrong. Your master
              password is never needed and your vault stays encrypted throughout.
            </Typography>
          ) : (
            <Box>
              <Typography variant="body2" sx={{ color: "text.secondary", mb: 1 }}>
                One-click updates aren&apos;t enabled on this instance. Update from a terminal in
                your CipherMoth folder:
              </Typography>
              <Box
                component="pre"
                sx={{
                  m: 0,
                  p: 1.5,
                  borderRadius: 1,
                  bgcolor: "#141416",
                  color: "#f4f4f2",
                  fontSize: 12,
                  overflowX: "auto",
                  whiteSpace: "pre-wrap",
                }}
              >
                {manualCommand}
              </Box>
            </Box>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={inProgress}>
          {updaterPresent ? "Later" : "Close"}
        </Button>
        {updaterPresent && (
          <Button variant="contained" onClick={handleApply} loading={inProgress}>
            Update now
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default UpdateDialog;
