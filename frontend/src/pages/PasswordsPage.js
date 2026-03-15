import { useCallback, useEffect, useRef, useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  IconButton,
  InputAdornment,
  Radio,
  RadioGroup,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import AddIcon from "@mui/icons-material/Add";
import GppBadIcon from "@mui/icons-material/GppBad";
import GppGoodIcon from "@mui/icons-material/GppGood";
import GppMaybeIcon from "@mui/icons-material/GppMaybe";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DeleteIcon from "@mui/icons-material/Delete";
import DownloadIcon from "@mui/icons-material/Download";
import EditIcon from "@mui/icons-material/Edit";
import SearchIcon from "@mui/icons-material/Search";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

import { formatDuration, getPasswordStrength } from "../utils";

const EMPTY_FORM = { password_name: "", username: "", password_value: "", description: "" };

const PasswordsPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  const { get, create, update, remove, backup, importPasswords } = useStoreActions(
    (actions) => actions.dinopassModels.passwords
  );
  const { error, loading, passwords } = useStoreState((state) => state.dinopassModels.passwords);
  const clipboardClearMs = useStoreState(
    (s) => s.dinopassModels.settings.settings.clipboard_clear_ms
  );

  const clipboardClearAtRef = useRef(null);

  const [visibleRows, setVisibleRows] = useState(new Set());

  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [editTarget, setEditTarget] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [showFormValue, setShowFormValue] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [backupDialogOpen, setBackupDialogOpen] = useState(false);
  const [backupPassword, setBackupPassword] = useState("");
  const [backupPasswordError, setBackupPasswordError] = useState("");
  const [showBackupPassword, setShowBackupPassword] = useState(false);
  const [backupLoading, setBackupLoading] = useState(false);

  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importPassword, setImportPassword] = useState("");
  const [importPasswordError, setImportPasswordError] = useState("");
  const [showImportPassword, setShowImportPassword] = useState(false);
  const [importOnConflict, setImportOnConflict] = useState("skip");
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState(null);

  const [search, setSearch] = useState("");

  useEffect(() => {
    get();
  }, [get]);

  useEffect(() => {
    if (error) enqueueSnackbar(error, { variant: "error" });
  }, [error, enqueueSnackbar]);

  useEffect(() => {
    const handleFocus = () => {
      const clearAt = clipboardClearAtRef.current;
      if (clearAt && Date.now() >= clearAt - 5_000) {
        clipboardClearAtRef.current = null;
        navigator.clipboard.writeText("").catch(() => {});
      }
    };
    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, []);

  const toggleVisibility = useCallback((name) => {
    setVisibleRows((prev) => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  }, []);

  const copyToClipboard = useCallback(
    (value) => {
      navigator.clipboard.writeText(value).then(() => {
        enqueueSnackbar(`Copied! Clipboard clears in ${formatDuration(clipboardClearMs)}.`, {
          variant: "success",
        });
        const clearAt = Date.now() + clipboardClearMs;
        clipboardClearAtRef.current = clearAt;
        setTimeout(() => {
          if (clipboardClearAtRef.current === clearAt && document.hasFocus()) {
            clipboardClearAtRef.current = null;
            navigator.clipboard.writeText("").catch(() => {});
          }
        }, clipboardClearMs);
      });
    },
    [enqueueSnackbar, clipboardClearMs]
  );

  const openAddDialog = () => {
    setEditTarget(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setShowFormValue(false);
    setDialogOpen(true);
  };

  const openEditDialog = (row) => {
    setEditTarget(row);
    setForm({
      password_name: row.password_name,
      username: row.username ?? "",
      password_value: row.password_value,
      description: row.description ?? "",
    });
    setFormError("");
    setShowFormValue(false);
    setDialogOpen(true);
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setEditTarget(null);
  };

  const handleFormChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setFormError("");
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
      const entry = {
        password_name: form.password_name.trim(),
        username: form.username.trim() || null,
        password_value: form.password_value,
        description: form.description.trim() || null,
      };
      if (editTarget) {
        await update({
          password: {
            password_name: editTarget.password_name,
            username: editTarget.username ?? null,
            password_value: editTarget.password_value,
            description: editTarget.description ?? null,
          },
          new_password: entry,
        });
        enqueueSnackbar("Password updated.", { variant: "success" });
      } else {
        await create(entry);
        enqueueSnackbar("Password created.", { variant: "success" });
      }
      closeDialog();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await remove(deleteTarget);
      enqueueSnackbar("Password deleted.", { variant: "success" });
    } catch (err) {
      enqueueSnackbar(err.message, { variant: "error" });
    } finally {
      setDeleteTarget(null);
    }
  };

  const openBackupDialog = () => {
    setBackupPassword("");
    setBackupPasswordError("");
    setShowBackupPassword(false);
    setBackupDialogOpen(true);
  };

  const closeBackupDialog = () => {
    if (backupLoading) return;
    setBackupDialogOpen(false);
  };

  const handleBackup = async () => {
    if (!backupPassword.trim()) {
      setBackupPasswordError("Master password is required.");
      return;
    }
    setBackupLoading(true);
    try {
      await backup(backupPassword);
      setBackupDialogOpen(false);
      enqueueSnackbar("Backup created: keep this file safe.", { variant: "success" });
    } catch (err) {
      setBackupPasswordError(err.message);
    } finally {
      setBackupLoading(false);
    }
  };

  const openImportDialog = () => {
    setImportFile(null);
    setImportPassword("");
    setImportPasswordError("");
    setShowImportPassword(false);
    setImportOnConflict("skip");
    setImportResult(null);
    setImportDialogOpen(true);
  };

  const closeImportDialog = () => {
    if (importLoading) return;
    setImportDialogOpen(false);
  };

  const handleImport = async () => {
    if (!importFile) {
      setImportPasswordError("Please select a backup file.");
      return;
    }
    if (!importPassword.trim()) {
      setImportPasswordError("Master password is required.");
      return;
    }
    setImportLoading(true);
    try {
      const result = await importPasswords({
        file: importFile,
        masterPassword: importPassword,
        onConflict: importOnConflict,
      });
      setImportResult(result);
    } catch (err) {
      setImportPasswordError(err.message);
    } finally {
      setImportLoading(false);
    }
  };

  const subtitle = (() => {
    if (loading) return "Loading…";
    if (passwords.length === 0) return "Nothing here yet. Your dino is hungry for passwords.";
    const n = passwords.length;
    const word = n === 1 ? "password" : "passwords";
    if (passwords.every((p) => p.backed_up)) return `${n} ${word}, all backed up and locked tight.`;
    if (passwords.some((p) => p.backed_up)) return `${n} ${word} - backup is outdated.`;
    return `${n} ${word} stored: no backup yet.`;
  })();

  const columns = [
    {
      field: "password_name",
      headerName: "Name",
      flex: 1,
      minWidth: 140,
    },
    {
      field: "username",
      headerName: "Username / email",
      flex: 1,
      minWidth: 140,
      renderCell: (params) => (
        <Typography
          variant="body2"
          color={params.value ? "text.primary" : "text.disabled"}
          sx={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
        >
          {params.value || "-"}
        </Typography>
      ),
    },
    {
      field: "password_value",
      headerName: "Password",
      flex: 1,
      minWidth: 140,
      sortable: false,
      renderCell: (params) => {
        const visible = visibleRows.has(params.row.password_name);
        return (
          <Typography
            variant="body2"
            sx={{
              fontFamily: "monospace",
              letterSpacing: visible ? 0 : 2,
              color: "text.secondary",
            }}
          >
            {visible ? params.value : "••••••••••••"}
          </Typography>
        );
      },
    },
    {
      field: "description",
      headerName: "Description",
      flex: 1.2,
      minWidth: 140,
      renderCell: (params) => (
        <Typography
          variant="body2"
          color={params.value ? "text.primary" : "text.disabled"}
          sx={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
        >
          {params.value || "-"}
        </Typography>
      ),
    },
    {
      field: "actions",
      headerName: "Actions",
      width: 250,
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: (params) => {
        const visible = visibleRows.has(params.row.password_name);
        const strength = getPasswordStrength(params.row.password_value);
        const StrengthIcon = strength
          ? strength.level <= 1
            ? GppBadIcon
            : strength.level === 2
            ? GppMaybeIcon
            : GppGoodIcon
          : null;
        return (
          <Stack direction="row" alignItems="center" spacing={0} height="100%">
            <Tooltip title={visible ? "Hide password" : "Reveal password"}>
              <IconButton size="small" onClick={() => toggleVisibility(params.row.password_name)}>
                {visible ? (
                  <VisibilityOffIcon fontSize="small" />
                ) : (
                  <VisibilityIcon fontSize="small" />
                )}
              </IconButton>
            </Tooltip>
            <Tooltip title="Copy password">
              <IconButton size="small" onClick={() => copyToClipboard(params.row.password_value)}>
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Divider orientation="vertical" flexItem sx={{ mx: 0.5, my: 1 }} />

            <Tooltip title="Edit">
              <IconButton size="small" onClick={() => openEditDialog(params.row)}>
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton
                size="small"
                color="error"
                onClick={() => setDeleteTarget(params.row.password_name)}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Divider orientation="vertical" flexItem sx={{ mx: 0.5, my: 1 }} />
            {strength && StrengthIcon && (
              <Tooltip
                title={
                  <Box>
                    <Typography variant="caption" fontWeight={700} sx={{ color: strength.color }}>
                      {strength.label}
                    </Typography>
                    <Typography variant="caption" display="block">
                      {strength.recommend
                        ? "We recommend updating this password."
                        : "This password looks good."}
                    </Typography>
                  </Box>
                }
              >
                <Box display="flex" alignItems="center">
                  <StrengthIcon fontSize="small" sx={{ color: strength.color }} />
                </Box>
              </Tooltip>
            )}
            <Tooltip title={params.row.backed_up ? "Password backed up" : "Password not backed up"}>
              <Box display="flex" alignItems="center">
                {params.row.backed_up ? (
                  <CheckCircleOutlineIcon fontSize="small" sx={{ color: "success.main" }} />
                ) : (
                  <HighlightOffIcon fontSize="small" sx={{ color: "warning.main" }} />
                )}
              </Box>
            </Tooltip>
          </Stack>
        );
      },
    },
  ];

  const isEmpty = !loading && passwords.length === 0;

  const query = search.trim().toLowerCase();
  const filteredPasswords = query
    ? passwords.filter(
        (p) =>
          p.password_name.toLowerCase().includes(query) ||
          (p.username && p.username.toLowerCase().includes(query)) ||
          (p.description && p.description.toLowerCase().includes(query))
      )
    : passwords;

  return (
    <Box>
      {/* Page header */}
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={700} lineHeight={1.2}>
            Dino Vault
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            {subtitle}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={openBackupDialog}
            disabled={passwords.length === 0}
          >
            Backup
          </Button>
          <Button variant="outlined" startIcon={<UploadFileIcon />} onClick={openImportDialog}>
            Import
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openAddDialog}>
            Add Password
          </Button>
        </Stack>
      </Stack>

      {/* Search */}
      {!isEmpty && (
        <TextField
          size="small"
          placeholder="Search by name, username or description…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ mb: 2, width: 320 }}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" sx={{ color: "text.disabled" }} />
                </InputAdornment>
              ),
            },
          }}
        />
      )}

      {/* Loading */}
      {loading && (
        <Box display="flex" justifyContent="center" mt={8}>
          <CircularProgress />
        </Box>
      )}

      {/* Empty state */}
      {isEmpty && (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          py={10}
          gap={2}
          sx={{
            bgcolor: "background.paper",
            borderRadius: 3,
            border: "1px dashed",
            borderColor: "divider",
          }}
        >
          <Box component="img" src="/dino.svg" alt="dino" sx={{ width: 96, height: 96, mb: 1 }} />
          <Typography variant="h6" fontWeight={600}>
            The vault is empty
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center" maxWidth={320}>
            Your prehistoric password guardian is standing by. Add your first password to get
            started.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={openAddDialog}
            sx={{ mt: 1 }}
          >
            Add First Password
          </Button>
        </Box>
      )}

      {/* Table */}
      {!loading && !isEmpty && (
        <DataGrid
          rows={filteredPasswords}
          slots={{
            noRowsOverlay: () => (
              <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                <Typography variant="body2" color="text.secondary">
                  No passwords match &ldquo;{search.trim()}&rdquo;.
                </Typography>
              </Box>
            ),
          }}
          columns={columns}
          getRowId={(row) => row.password_name}
          disableRowSelectionOnClick
          getRowHeight={() => 52}
          pageSizeOptions={[10, 25, 50]}
          initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
          sx={{
            bgcolor: "background.paper",
            borderRadius: 2,
            "& .MuiDataGrid-cell": { display: "flex", alignItems: "center" },
            "& .MuiDataGrid-columnHeader": { bgcolor: "grey.50" },
            "& .MuiDataGrid-cell:focus": { outline: "none" },
            "& .MuiDataGrid-cell:focus-within": { outline: "none" },
          }}
        />
      )}

      {/* Add / Edit Dialog */}
      <Dialog open={dialogOpen} onClose={closeDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editTarget ? "Edit Password" : "Add Password"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Name"
              value={form.password_name}
              onChange={handleFormChange("password_name")}
              disabled={!!editTarget}
              required
              fullWidth
              autoFocus
              helperText={editTarget ? "Name cannot be changed" : "e.g. GitHub, Gmail, Netflix"}
            />
            <TextField
              label="Username / email (optional)"
              value={form.username}
              onChange={handleFormChange("username")}
              fullWidth
              placeholder="e.g. john@example.com"
              slotProps={{
                htmlInput: { spellCheck: false, autoCorrect: "off", autoCapitalize: "none" },
              }}
            />
            <TextField
              label="Password"
              type={showFormValue ? "text" : "password"}
              value={form.password_value}
              onChange={handleFormChange("password_value")}
              required
              fullWidth
              autoComplete="new-password"
              slotProps={{
                htmlInput: { spellCheck: false, autoCorrect: "off", autoCapitalize: "none" },
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowFormValue((v) => !v)} edge="end">
                        {showFormValue ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />
            {form.password_value && (() => {
              const s = getPasswordStrength(form.password_value);
              return (
                <Box>
                  <Stack direction="row" spacing={0.5} mb={0.75}>
                    {[0, 1, 2, 3, 4].map((i) => (
                      <Box
                        key={i}
                        sx={{
                          flex: 1,
                          height: 4,
                          borderRadius: 2,
                          bgcolor: i <= s.level ? s.color : "grey.200",
                          transition: "background-color 0.2s",
                        }}
                      />
                    ))}
                  </Stack>
                  <Typography variant="caption" sx={{ color: s.color, fontWeight: 600 }}>
                    {s.label}
                    {s.recommend && " - consider a longer or more complex password"}
                  </Typography>
                </Box>
              );
            })()}
            <TextField
              label="Description (optional)"
              value={form.description}
              onChange={handleFormChange("description")}
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
          <Button onClick={closeDialog} disabled={submitting}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={
              submitting ||
              (!!editTarget &&
                form.username === (editTarget.username ?? "") &&
                form.password_value === editTarget.password_value &&
                form.description === (editTarget.description ?? ""))
            }
          >
            {submitting ? <CircularProgress size={20} /> : editTarget ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Backup Dialog */}
      <Dialog open={backupDialogOpen} onClose={closeBackupDialog} maxWidth="xs" fullWidth>
        <DialogTitle>Create Backup</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <Typography variant="body2" color="text.secondary">
              Your passwords will be exported as an AES-256 encrypted ZIP file. Open it with your
              master password.
            </Typography>
            <TextField
              label="Master Password"
              type={showBackupPassword ? "text" : "password"}
              value={backupPassword}
              onChange={(e) => {
                setBackupPassword(e.target.value);
                setBackupPasswordError("");
              }}
              error={!!backupPasswordError}
              helperText={backupPasswordError}
              required
              fullWidth
              autoFocus
              autoComplete="current-password"
              onKeyDown={(e) => {
                if (e.key === "Enter") handleBackup();
              }}
              slotProps={{
                htmlInput: { spellCheck: false, autoCorrect: "off", autoCapitalize: "none" },
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowBackupPassword((v) => !v)} edge="end">
                        {showBackupPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeBackupDialog} disabled={backupLoading}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleBackup} disabled={backupLoading}>
            {backupLoading ? <CircularProgress size={20} /> : "Create Backup"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={importDialogOpen} onClose={closeImportDialog} maxWidth="xs" fullWidth>
        <DialogTitle>{importResult ? "Import Complete" : "Import Backup"}</DialogTitle>
        <DialogContent>
          {importResult ? (
            <Stack spacing={1} mt={1}>
              {importResult.total === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No passwords found in the backup file.
                </Typography>
              ) : (
                <>
                  {importResult.imported > 0 && (
                    <Typography variant="body2">
                      <strong>{importResult.imported}</strong> password
                      {importResult.imported !== 1 ? "s" : ""} added.
                    </Typography>
                  )}
                  {importResult.overwritten > 0 && (
                    <Typography variant="body2">
                      <strong>{importResult.overwritten}</strong> password
                      {importResult.overwritten !== 1 ? "s" : ""} overwritten.
                    </Typography>
                  )}
                  {importResult.skipped > 0 && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>{importResult.skipped}</strong> password
                      {importResult.skipped !== 1 ? "s" : ""} skipped (already exist).
                    </Typography>
                  )}
                </>
              )}
            </Stack>
          ) : (
            <Stack spacing={2} mt={1}>
              <Typography variant="body2" color="text.secondary">
                Upload a dinopass backup ZIP and enter your master password to restore passwords.
              </Typography>
              <Button
                component="label"
                variant="outlined"
                startIcon={<UploadFileIcon />}
                fullWidth
                sx={{ justifyContent: "flex-start", textTransform: "none" }}
              >
                {importFile ? importFile.name : "Choose backup file (.zip)"}
                <input
                  type="file"
                  hidden
                  accept=".zip"
                  onChange={(e) => {
                    setImportFile(e.target.files[0] ?? null);
                    setImportPasswordError("");
                  }}
                />
              </Button>
              <TextField
                label="Master Password"
                type={showImportPassword ? "text" : "password"}
                value={importPassword}
                onChange={(e) => {
                  setImportPassword(e.target.value);
                  setImportPasswordError("");
                }}
                error={!!importPasswordError}
                helperText={importPasswordError}
                required
                fullWidth
                autoFocus
                autoComplete="current-password"
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleImport();
                }}
                slotProps={{
                  htmlInput: { spellCheck: false, autoCorrect: "off", autoCapitalize: "none" },
                  input: {
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowImportPassword((v) => !v)} edge="end">
                          {showImportPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  },
                }}
              />
              <FormControl>
                <FormLabel sx={{ fontSize: "0.875rem" }}>If a password already exists</FormLabel>
                <RadioGroup
                  value={importOnConflict}
                  onChange={(e) => setImportOnConflict(e.target.value)}
                >
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
          {importResult ? (
            <Button variant="contained" onClick={closeImportDialog}>
              Done
            </Button>
          ) : (
            <>
              <Button onClick={closeImportDialog} disabled={importLoading}>
                Cancel
              </Button>
              <Button variant="contained" onClick={handleImport} disabled={importLoading}>
                {importLoading ? <CircularProgress size={20} /> : "Import"}
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>

      <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} maxWidth="xs" fullWidth>
        <DialogTitle>Delete Password</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete <strong>{deleteTarget}</strong>? This cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleDelete}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PasswordsPage;
