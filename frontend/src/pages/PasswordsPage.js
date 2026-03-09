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
  IconButton,
  InputAdornment,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import AddIcon from "@mui/icons-material/Add";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

const EMPTY_FORM = { password_name: "", password_value: "", description: "" };
const CLIPBOARD_CLEAR_MS = 30_000;

const PasswordsPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  const { get, create, update, remove } = useStoreActions(
    (actions) => actions.dinopassModels.passwords
  );
  const { error, loading, passwords } = useStoreState(
    (state) => state.dinopassModels.passwords
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

  useEffect(() => { get(); }, [get]);

  useEffect(() => {
    if (error) enqueueSnackbar(error, { variant: "error" });
  }, [error, enqueueSnackbar]);


  const toggleVisibility = useCallback((name) => {
    setVisibleRows((prev) => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  }, []);

  const copyToClipboard = useCallback((value) => {
    navigator.clipboard.writeText(value).then(() => {
      enqueueSnackbar("Copied! Clipboard clears in 30s 🦖", { variant: "success" });
      const clearAt = Date.now() + CLIPBOARD_CLEAR_MS;
      clipboardClearAtRef.current = clearAt;
      setTimeout(() => {
        if (clipboardClearAtRef.current === clearAt && document.hasFocus()) {
          clipboardClearAtRef.current = null;
          navigator.clipboard.writeText("").catch(() => {});
        }
      }, CLIPBOARD_CLEAR_MS);
    });
  }, [enqueueSnackbar]);

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
      password_value: row.password_value,
      description: row.description ?? "",
    });
    setFormError("");
    setShowFormValue(false);
    setDialogOpen(true);
  };

  const closeDialog = () => { setDialogOpen(false); setEditTarget(null); };

  const handleFormChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setFormError("");
  };

  const handleSubmit = async () => {
    if (!form.password_name.trim()) { setFormError("Name is required."); return; }
    if (!form.password_value.trim()) { setFormError("Password value is required."); return; }
    setSubmitting(true);
    try {
      const entry = {
        password_name: form.password_name.trim(),
        password_value: form.password_value,
        description: form.description.trim() || null,
      };
      if (editTarget) {
        await update({
          password: {
            password_name: editTarget.password_name,
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

  const columns = [
    {
      field: "password_name",
      headerName: "Name",
      flex: 1,
      minWidth: 140,
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
            sx={{ fontFamily: "monospace", letterSpacing: visible ? 0 : 2, color: "text.secondary" }}
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
          {params.value || "—"}
        </Typography>
      ),
    },
    {
      field: "actions",
      headerName: "Actions",
      width: 180,
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: (params) => {
        const visible = visibleRows.has(params.row.password_name);
        return (
          <Stack direction="row" alignItems="center" spacing={0} height="100%">
            <Tooltip title={visible ? "Hide password" : "Reveal password"}>
              <IconButton size="small" onClick={() => toggleVisibility(params.row.password_name)}>
                {visible
                  ? <VisibilityOffIcon fontSize="small" />
                  : <VisibilityIcon fontSize="small" />}
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
              <IconButton size="small" color="error" onClick={() => setDeleteTarget(params.row.password_name)}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        );
      },
    },
  ];

  const isEmpty = !loading && passwords.length === 0;

  return (
    <Box>
      {/* Page header */}
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={700} lineHeight={1.2}>
            Your Vault
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            {loading
              ? "Loading…"
              : passwords.length === 0
              ? "Nothing here yet. Your dino is hungry for passwords."
              : `${passwords.length} password${passwords.length === 1 ? "" : "s"}, all locked up tight.`}
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={openAddDialog}>
          Add Password
        </Button>
      </Stack>

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
          <Typography fontSize={64} lineHeight={1} role="img" aria-label="dino">
            🦕
          </Typography>
          <Typography variant="h6" fontWeight={600}>
            The vault is empty
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center" maxWidth={320}>
            Your prehistoric password guardian is standing by. Add your first password to get started.
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openAddDialog} sx={{ mt: 1 }}>
            Add First Password
          </Button>
        </Box>
      )}

      {/* Table */}
      {!loading && !isEmpty && (
        <DataGrid
          rows={passwords}
          columns={columns}
          getRowId={(row) => row.password_name}
          disableRowSelectionOnClick
          autoHeight
          rowHeight={52}
          pageSizeOptions={[10, 25, 50]}
          initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
          sx={{
            bgcolor: "background.paper",
            borderRadius: 2,
            "& .MuiDataGrid-cell": {
              display: "flex",
              alignItems: "center",
            },
            "& .MuiDataGrid-columnHeader": {
              bgcolor: "grey.50",
            },
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
              label="Password"
              type={showFormValue ? "text" : "password"}
              value={form.password_value}
              onChange={handleFormChange("password_value")}
              required
              fullWidth
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowFormValue((v) => !v)} edge="end">
                      {showFormValue ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
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
          <Button onClick={closeDialog} disabled={submitting}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <CircularProgress size={20} /> : editTarget ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation */}
      <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} maxWidth="xs" fullWidth>
        <DialogTitle>Delete Password</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete <strong>{deleteTarget}</strong>? This cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleDelete}>Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PasswordsPage;
