import { useEffect, useState } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";

import PasswordField from "../PasswordField";
import PasswordGenerator, { CHAR_KEYS } from "./PasswordGenerator";
import StrengthBar from "./StrengthBar";
import { generatePassword } from "../../lib/passwordGenerator";

const EMPTY_FORM = { password_name: "", username: "", password_value: "", description: "" };
const GEN_DEFAULTS = { length: 16, uppercase: true, lowercase: true, numbers: true, symbols: true };

const toForm = (target) =>
  target
    ? {
        password_name: target.password_name,
        username: target.username ?? "",
        password_value: target.password_value,
        description: target.description ?? "",
      }
    : EMPTY_FORM;

const PasswordFormDialog = ({ open, editTarget, onClose, onSubmit }) => {
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [showValue, setShowValue] = useState(false);
  const [showGenerator, setShowGenerator] = useState(false);
  const [genOpts, setGenOpts] = useState(GEN_DEFAULTS);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setForm(toForm(editTarget));
    setFormError("");
    setShowValue(false);
    setShowGenerator(false);
  }, [open, editTarget]);

  const setField = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setFormError("");
  };

  const applyGenerated = (opts) => {
    setForm((prev) => ({ ...prev, password_value: generatePassword(opts) }));
    setShowValue(true);
  };

  const toggleGenerator = () => {
    if (!showGenerator) applyGenerated(genOpts);
    setShowGenerator((v) => !v);
  };

  const changeGenLength = (length) => {
    const next = { ...genOpts, length };
    setGenOpts(next);
    applyGenerated(next);
  };

  const toggleGenClass = (key) => {
    setGenOpts((prev) => {
      const wouldHaveNone = CHAR_KEYS.every((k) => (k === key ? prev[k] : !prev[k]));
      if (wouldHaveNone) return prev;
      const next = { ...prev, [key]: !prev[key] };
      applyGenerated(next);
      return next;
    });
  };

  const handleSubmit = async () => {
    if (!form.password_name.trim()) {
      setFormError("Name is required.");
      return;
    }
    if (!form.password_value.trim()) {
      setFormError("Password value is required.");
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit({
        password_name: form.password_name.trim(),
        username: form.username.trim() || null,
        password_value: form.password_value,
        description: form.description.trim() || null,
      });
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const unchanged =
    !!editTarget &&
    form.username === (editTarget.username ?? "") &&
    form.password_value === editTarget.password_value &&
    form.description === (editTarget.description ?? "");

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{editTarget ? "Edit Password" : "Add Password"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            label="Name"
            value={form.password_name}
            onChange={setField("password_name")}
            disabled={!!editTarget}
            required
            fullWidth
            autoFocus
            helperText={editTarget ? "Name cannot be changed" : "e.g. GitHub, Gmail, Netflix"}
          />
          <TextField
            label="Username / email (optional)"
            value={form.username}
            onChange={setField("username")}
            fullWidth
            placeholder="e.g. john@example.com"
            slotProps={{
              htmlInput: { spellCheck: false, autoCorrect: "off", autoCapitalize: "none" },
            }}
          />
          <PasswordField
            label="Password"
            value={form.password_value}
            onChange={(e) => {
              setField("password_value")(e);
              if (showGenerator) setShowGenerator(false);
            }}
            required
            autoComplete="new-password"
            show={showValue}
            onToggleShow={() => setShowValue((v) => !v)}
            adornment={
              <Tooltip title={showGenerator ? "Close generator" : "Generate password"}>
                <IconButton
                  onClick={toggleGenerator}
                  size="small"
                  color={showGenerator ? "primary" : "default"}
                >
                  <AutoFixHighIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            }
          />
          {showGenerator && (
            <PasswordGenerator
              options={genOpts}
              onChangeLength={changeGenLength}
              onToggleClass={toggleGenClass}
              onRegenerate={() => applyGenerated(genOpts)}
            />
          )}
          <StrengthBar password={form.password_value} />
          <TextField
            label="Description (optional)"
            value={form.description}
            onChange={setField("description")}
            fullWidth
            multiline
            rows={2}
            placeholder="e.g. Personal account, work email…"
          />
          {formError && (
            <Typography variant="body2" color="error">
              {formError}
            </Typography>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={submitting}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          loading={submitting}
          disabled={unchanged}
        >
          {editTarget ? "Update" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PasswordFormDialog;
