import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import AddIcon from "@mui/icons-material/Add";
import DownloadIcon from "@mui/icons-material/Download";
import HealthAndSafetyIcon from "@mui/icons-material/HealthAndSafety";
import SearchIcon from "@mui/icons-material/Search";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";

import BackupDialog from "../components/vault/BackupDialog";
import ConfirmDialog from "../components/ConfirmDialog";
import EmptyVault from "../components/vault/EmptyVault";
import HealthDialog from "../components/vault/HealthDialog";
import ImportDialog from "../components/vault/ImportDialog";
import PasswordFormDialog from "../components/vault/PasswordFormDialog";
import { createColumns } from "../components/vault/columns";
import useClipboard from "../hooks/useClipboard";

const buildSubtitle = (loading, passwords) => {
  if (loading) return "Loading…";
  const n = passwords.length;
  if (n === 0) return "Nothing here yet. Your secrets are waiting for the dark.";
  const word = n === 1 ? "secret" : "secrets";
  if (passwords.every((p) => p.backed_up))
    return `${n} ${word} in the dark · backed up and locked tight.`;
  if (passwords.some((p) => p.backed_up)) return `${n} ${word} in the dark · backup is outdated.`;
  return `${n} ${word} in the dark · no backup yet.`;
};

const PasswordsPage = () => {
  const { enqueueSnackbar } = useSnackbar();
  const copy = useClipboard();

  const { get, create, update, remove, backup, importPasswords, importCsv, toggleFavorite } =
    useStoreActions((actions) => actions.ciphermothModels.passwords);
  const { error, loading, passwords } = useStoreState((state) => state.ciphermothModels.passwords);

  const [visibleRows, setVisibleRows] = useState(new Set());
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [backupOpen, setBackupOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [healthOpen, setHealthOpen] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    get();
  }, [get]);

  useEffect(() => {
    if (error) enqueueSnackbar(error, { variant: "error" });
  }, [error, enqueueSnackbar]);

  const toggleVisibility = useCallback((name) => {
    setVisibleRows((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  }, []);

  const openAdd = () => {
    setEditTarget(null);
    setDialogOpen(true);
  };

  const openEdit = useCallback((row) => {
    setEditTarget(row);
    setDialogOpen(true);
  }, []);

  const handleToggleFavorite = useCallback(
    async (row) => {
      try {
        await toggleFavorite({ passwordName: row.password_name, favorite: !row.favorite });
      } catch (err) {
        enqueueSnackbar(err.message, { variant: "error" });
      }
    },
    [toggleFavorite, enqueueSnackbar]
  );

  const handleSubmit = async (entry) => {
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
    setDialogOpen(false);
  };

  const handleDelete = async () => {
    try {
      await remove(deleteTarget);
      enqueueSnackbar("Password deleted.", { variant: "success" });
    } catch (err) {
      enqueueSnackbar(err.message, { variant: "error" });
    } finally {
      setDeleteTarget(null);
    }
  };

  const handleBackup = async (masterPassword) => {
    await backup(masterPassword);
    enqueueSnackbar("Backup created: keep this file safe.", { variant: "success" });
  };

  const columns = useMemo(
    () =>
      createColumns({
        visibleRows,
        onToggleVisibility: toggleVisibility,
        onToggleFavorite: handleToggleFavorite,
        onCopy: copy,
        onEdit: openEdit,
        onDelete: setDeleteTarget,
      }),
    [visibleRows, toggleVisibility, handleToggleFavorite, copy, openEdit]
  );

  const filteredPasswords = useMemo(() => {
    const query = search.trim().toLowerCase();
    const matches = !query
      ? passwords
      : passwords.filter(
          (p) =>
            p.password_name.toLowerCase().includes(query) ||
            p.username?.toLowerCase().includes(query) ||
            p.description?.toLowerCase().includes(query) ||
            p.url?.toLowerCase().includes(query) ||
            p.tags?.some((tag) => tag.toLowerCase().includes(query))
        );

    return [...matches].sort(
      (a, b) =>
        Number(b.favorite) - Number(a.favorite) || a.password_name.localeCompare(b.password_name)
    );
  }, [passwords, search]);

  const subtitle = useMemo(() => buildSubtitle(loading, passwords), [loading, passwords]);
  const isEmpty = !loading && passwords.length === 0;

  return (
    <Box>
      <Stack
        direction="row"
        sx={{ justifyContent: "space-between", alignItems: "flex-start", mb: 2.5 }}
      >
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
            The Vault
          </Typography>
          <Typography variant="body2" sx={{ color: "text.secondary", mt: 0.5 }}>
            {subtitle}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<HealthAndSafetyIcon />}
            onClick={() => setHealthOpen(true)}
            disabled={passwords.length === 0}
          >
            Health
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => setBackupOpen(true)}
            disabled={passwords.length === 0}
          >
            Backup
          </Button>
          <Button
            variant="outlined"
            startIcon={<UploadFileIcon />}
            onClick={() => setImportOpen(true)}
          >
            Import
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openAdd}>
            Add Password
          </Button>
        </Stack>
      </Stack>

      {!isEmpty && (
        <TextField
          size="small"
          placeholder="Search name, username, website or tag…"
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

      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {isEmpty && <EmptyVault onAdd={openAdd} />}

      {!loading && !isEmpty && (
        <DataGrid
          rows={filteredPasswords}
          columns={columns}
          getRowId={(row) => row.password_name}
          disableRowSelectionOnClick
          density="compact"
          rowHeight={44}
          columnHeaderHeight={42}
          pageSizeOptions={[10, 25, 50]}
          initialState={{
            pagination: { paginationModel: { pageSize: 10 } },
          }}
          slots={{
            noRowsOverlay: () => (
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "100%",
                }}
              >
                <Typography variant="body2" sx={{ color: "text.secondary" }}>
                  No passwords match &ldquo;{search.trim()}&rdquo;.
                </Typography>
              </Box>
            ),
          }}
          sx={{
            bgcolor: "background.paper",
            borderRadius: 2.5,
            borderColor: "divider",
            "& .MuiDataGrid-cell": { display: "flex", alignItems: "center" },
            "& .MuiDataGrid-columnHeaders": { borderColor: "divider" },
            "& .MuiDataGrid-columnHeader": { bgcolor: "background.paper" },
            "& .MuiDataGrid-columnHeaderTitle": {
              fontWeight: 600,
              color: "text.secondary",
            },
            "& .MuiDataGrid-row:hover": { bgcolor: "#fafafa" },
            "& .MuiDataGrid-cell:focus": { outline: "none" },
            "& .MuiDataGrid-cell:focus-within": { outline: "none" },
            "& .rowHoverActions": {
              opacity: 0,
              pointerEvents: "none",
              transition: "opacity 120ms ease",
            },
            "& .MuiDataGrid-row:hover .rowHoverActions, & .MuiDataGrid-row:has(:focus-visible) .rowHoverActions":
              {
                opacity: 1,
                pointerEvents: "auto",
              },
          }}
        />
      )}

      <PasswordFormDialog
        open={dialogOpen}
        editTarget={editTarget}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleSubmit}
        onCopy={copy}
      />
      <BackupDialog
        open={backupOpen}
        onClose={() => setBackupOpen(false)}
        onBackup={handleBackup}
      />
      <ImportDialog
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onImport={importPasswords}
        onImportCsv={importCsv}
      />
      <HealthDialog
        open={healthOpen}
        passwords={passwords}
        onClose={() => setHealthOpen(false)}
        onSelect={(row) => {
          setHealthOpen(false);
          openEdit(row);
        }}
      />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Password"
        confirmText="Delete"
        confirmColor="error"
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
      >
        Are you sure you want to delete <strong>{deleteTarget}</strong>? This cannot be undone.
      </ConfirmDialog>
    </Box>
  );
};

export default PasswordsPage;
