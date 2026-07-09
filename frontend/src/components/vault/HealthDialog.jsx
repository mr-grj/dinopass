import { useMemo } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  List,
  ListItemButton,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import CheckCircleOutlinedIcon from "@mui/icons-material/CheckCircleOutlined";

import { analyzeVault } from "../../lib/vaultHealth";

const scoreColor = (score) => {
  if (score >= 80) return "success";
  if (score >= 50) return "warning";
  return "error";
};

const Section = ({ title, hint, entries, onSelect }) => {
  if (entries.length === 0) return null;
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
        {title} ({entries.length})
      </Typography>
      <Typography variant="caption" sx={{ color: "text.secondary" }}>
        {hint}
      </Typography>
      <List dense disablePadding sx={{ mt: 0.5 }}>
        {entries.map((entry) => (
          <ListItemButton
            key={entry.password_name}
            onClick={() => onSelect(entry)}
            sx={{ borderRadius: 1 }}
          >
            <ListItemText primary={entry.password_name} secondary={entry.username || undefined} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
};

const HealthDialog = ({ open, onClose, passwords, onSelect }) => {
  const report = useMemo(() => analyzeVault(passwords), [passwords]);
  const allClear =
    report.weak.length === 0 && report.reused.length === 0 && report.stale.length === 0;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Vault Health</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Box>
            <Stack direction="row" sx={{ justifyContent: "space-between", mb: 0.5 }}>
              <Typography variant="body2" sx={{ color: "text.secondary" }}>
                Health score
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 700 }}>
                {report.score}%
              </Typography>
            </Stack>
            <LinearProgress
              variant="determinate"
              value={report.score}
              color={scoreColor(report.score)}
              sx={{ height: 8, borderRadius: 1 }}
            />
          </Box>

          <Typography variant="caption" sx={{ color: "text.secondary" }}>
            This check runs entirely on your device. Nothing is sent anywhere.
          </Typography>

          {allClear ? (
            <Stack direction="row" spacing={1} sx={{ alignItems: "center", py: 1 }}>
              <CheckCircleOutlinedIcon sx={{ color: "success.main" }} />
              <Typography variant="body2">Everything looks healthy. Nice work.</Typography>
            </Stack>
          ) : (
            <>
              <Section
                title="Weak"
                hint="Short or simple passwords worth strengthening."
                entries={report.weak}
                onSelect={onSelect}
              />
              <Section
                title="Reused"
                hint="The same password is used on more than one entry."
                entries={report.reused}
                onSelect={onSelect}
              />
              <Section
                title="Old"
                hint="Not changed in over a year."
                entries={report.stale}
                onSelect={onSelect}
              />
            </>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" onClick={onClose}>
          Done
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default HealthDialog;
