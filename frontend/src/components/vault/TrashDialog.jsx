import { useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Tooltip,
  Typography,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import RestoreFromTrashIcon from "@mui/icons-material/RestoreFromTrash";

import ConfirmDialog from "../ConfirmDialog";
import { gridBaseSx } from "./gridStyles";

const formatDeleted = (iso) => {
  if (!iso) return "-";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "-" : date.toLocaleString();
};

const buildColumns = ({ onRestore, onPurge }) => [
  { field: "password_name", headerName: "Name", flex: 1, minWidth: 140 },
  {
    field: "username",
    headerName: "Username / email",
    flex: 1,
    minWidth: 150,
    renderCell: (params) => (
      <Typography variant="body2" sx={{ color: params.value ? "text.primary" : "text.disabled" }}>
        {params.value || "-"}
      </Typography>
    ),
  },
  {
    field: "deleted",
    headerName: "Deleted",
    flex: 1,
    minWidth: 170,
    renderCell: (params) => (
      <Typography variant="body2" sx={{ color: "text.secondary" }}>
        {formatDeleted(params.value)}
      </Typography>
    ),
  },
  {
    field: "actions",
    headerName: "Actions",
    width: 110,
    sortable: false,
    align: "center",
    headerAlign: "center",
    renderCell: (params) => (
      <Box sx={{ display: "flex", alignItems: "center", height: "100%" }}>
        <Tooltip title="Restore">
          <IconButton
            size="small"
            color="primary"
            onClick={() => onRestore(params.row.password_name)}
          >
            <RestoreFromTrashIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete forever">
          <IconButton size="small" color="error" onClick={() => onPurge(params.row.password_name)}>
            <DeleteForeverIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    ),
  },
];

const TrashDialog = ({ open, trash, onClose, onRestore, onPurge }) => {
  const [purgeTarget, setPurgeTarget] = useState(null);

  const columns = buildColumns({ onRestore, onPurge: setPurgeTarget });

  const handlePurge = async () => {
    await onPurge(purgeTarget);
    setPurgeTarget(null);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Trash</DialogTitle>
      <DialogContent>
        {trash.length === 0 ? (
          <Typography variant="body2" sx={{ color: "text.secondary", py: 4, textAlign: "center" }}>
            Trash is empty. Deleted secrets rest here until you restore or purge them.
          </Typography>
        ) : (
          <DataGrid
            rows={trash}
            columns={columns}
            getRowId={(row) => row.password_name}
            disableRowSelectionOnClick
            density="compact"
            rowHeight={44}
            columnHeaderHeight={42}
            autoHeight
            pageSizeOptions={[10, 25]}
            initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
            sx={gridBaseSx}
          />
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

      <ConfirmDialog
        open={!!purgeTarget}
        title="Delete Forever"
        confirmText="Delete Forever"
        confirmColor="error"
        onClose={() => setPurgeTarget(null)}
        onConfirm={handlePurge}
      >
        Permanently delete <strong>{purgeTarget}</strong>? This cannot be undone.
      </ConfirmDialog>
    </Dialog>
  );
};

export default TrashDialog;
