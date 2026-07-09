import { Box, Divider, IconButton, Stack, Tooltip, Typography } from "@mui/material";
import GppBadIcon from "@mui/icons-material/GppBad";
import GppGoodIcon from "@mui/icons-material/GppGood";
import GppMaybeIcon from "@mui/icons-material/GppMaybe";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";

import { getPasswordStrength } from "../../lib/passwordStrength";

const renderOptionalCell = (params) => (
  <Typography
    variant="body2"
    color={params.value ? "text.primary" : "text.disabled"}
    sx={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
  >
    {params.value || "-"}
  </Typography>
);

const strengthIconFor = (level) => {
  if (level <= 1) return GppBadIcon;
  if (level === 2) return GppMaybeIcon;
  return GppGoodIcon;
};

const StrengthIndicator = ({ password }) => {
  const strength = getPasswordStrength(password);
  if (!strength) return null;
  const Icon = strengthIconFor(strength.level);
  return (
    <Tooltip
      title={
        <Box>
          <Typography variant="caption" sx={{ fontWeight: 700, color: strength.color }}>
            {strength.label}
          </Typography>
          <Typography variant="caption" sx={{ display: "block" }}>
            {strength.recommend
              ? "We recommend updating this password."
              : "This password looks good."}
          </Typography>
        </Box>
      }
    >
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Icon fontSize="small" sx={{ color: strength.color }} />
      </Box>
    </Tooltip>
  );
};

export const createColumns = ({ visibleRows, onToggleVisibility, onCopy, onEdit, onDelete }) => [
  { field: "password_name", headerName: "Name", flex: 1, minWidth: 140 },
  {
    field: "username",
    headerName: "Username / email",
    flex: 1,
    minWidth: 140,
    renderCell: renderOptionalCell,
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
    renderCell: renderOptionalCell,
  },
  {
    field: "actions",
    headerName: "Actions",
    width: 250,
    sortable: false,
    align: "center",
    headerAlign: "center",
    renderCell: (params) => {
      const { password_name, password_value, backed_up } = params.row;
      const visible = visibleRows.has(password_name);
      return (
        <Stack direction="row" spacing={0} sx={{ alignItems: "center", height: "100%" }}>
          <Tooltip title={visible ? "Hide password" : "Reveal password"}>
            <IconButton size="small" onClick={() => onToggleVisibility(password_name)}>
              {visible ? (
                <VisibilityOffIcon fontSize="small" />
              ) : (
                <VisibilityIcon fontSize="small" />
              )}
            </IconButton>
          </Tooltip>
          <Tooltip title="Copy password">
            <IconButton size="small" onClick={() => onCopy(password_value)}>
              <ContentCopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Divider orientation="vertical" flexItem sx={{ mx: 0.5, my: 1 }} />
          <Tooltip title="Edit">
            <IconButton size="small" onClick={() => onEdit(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" color="error" onClick={() => onDelete(password_name)}>
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Divider orientation="vertical" flexItem sx={{ mx: 0.5, my: 1 }} />
          <StrengthIndicator password={password_value} />
          <Tooltip title={backed_up ? "Password backed up" : "Password not backed up"}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              {backed_up ? (
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
