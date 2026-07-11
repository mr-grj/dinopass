import { Box, Chip, Divider, IconButton, Stack, Tooltip, Typography } from "@mui/material";
import GppBadIcon from "@mui/icons-material/GppBad";
import GppGoodIcon from "@mui/icons-material/GppGood";
import GppMaybeIcon from "@mui/icons-material/GppMaybe";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import StarIcon from "@mui/icons-material/Star";
import StarBorderIcon from "@mui/icons-material/StarBorder";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";

import TotpCell from "./TotpCell";
import { getPasswordStrength } from "../../lib/passwordStrength";
import { GLOW } from "../../lib/brand";

const ValueCell = ({ text, mono = false, masked = false, color = "text.primary", actions }) => (
  <Box sx={{ display: "flex", alignItems: "center", width: "100%", minWidth: 0 }}>
    <Typography
      variant="body2"
      sx={{
        flex: 1,
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
        fontFamily: mono ? "'Space Mono', monospace" : undefined,
        letterSpacing: masked ? 2 : 0,
        color,
      }}
    >
      {text}
    </Typography>
    {actions && (
      <Box
        className="rowHoverActions"
        sx={{ display: "flex", alignItems: "center", flexShrink: 0, ml: 0.5 }}
      >
        {actions}
      </Box>
    )}
  </Box>
);

const CellActionButton = ({ title, onClick, children }) => (
  <Tooltip title={title}>
    <IconButton size="small" onClick={onClick} sx={{ p: 0.375 }}>
      {children}
    </IconButton>
  </Tooltip>
);

const openUrl = (url) => {
  const safe = /^https?:\/\//i.test(url) ? url : `https://${url}`;
  window.open(safe, "_blank", "noopener,noreferrer");
};

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

export const createColumns = ({
  visibleRows,
  onToggleVisibility,
  onToggleFavorite,
  onCopy,
  onEdit,
  onDelete,
}) => [
  {
    field: "favorite",
    headerName: "",
    width: 48,
    sortable: false,
    align: "center",
    headerAlign: "center",
    renderCell: (params) => (
      <Tooltip title={params.value ? "Remove from favorites" : "Mark as favorite"}>
        <IconButton size="small" onClick={() => onToggleFavorite(params.row)}>
          {params.value ? (
            <StarIcon fontSize="small" sx={{ color: GLOW }} />
          ) : (
            <StarBorderIcon fontSize="small" sx={{ color: "text.disabled" }} />
          )}
        </IconButton>
      </Tooltip>
    ),
  },
  { field: "password_name", headerName: "Name", flex: 1, minWidth: 130 },
  {
    field: "username",
    headerName: "Username / email",
    flex: 1,
    minWidth: 150,
    renderCell: (params) => {
      const value = params.value;
      return (
        <ValueCell
          text={value || "-"}
          color={value ? "text.primary" : "text.disabled"}
          actions={
            value ? (
              <CellActionButton title="Copy username" onClick={() => onCopy(value)}>
                <ContentCopyIcon fontSize="small" />
              </CellActionButton>
            ) : null
          }
        />
      );
    },
  },
  {
    field: "password_value",
    headerName: "Password",
    flex: 1,
    minWidth: 160,
    sortable: false,
    renderCell: (params) => {
      const name = params.row.password_name;
      const visible = visibleRows.has(name);
      return (
        <ValueCell
          mono
          masked={!visible}
          color="text.secondary"
          text={visible ? params.value : "••••••••"}
          actions={
            <>
              <CellActionButton
                title={visible ? "Hide password" : "Reveal password"}
                onClick={() => onToggleVisibility(name)}
              >
                {visible ? (
                  <VisibilityOffIcon fontSize="small" />
                ) : (
                  <VisibilityIcon fontSize="small" />
                )}
              </CellActionButton>
              <CellActionButton title="Copy password" onClick={() => onCopy(params.value)}>
                <ContentCopyIcon fontSize="small" />
              </CellActionButton>
            </>
          }
        />
      );
    },
  },
  {
    field: "tags",
    headerName: "Tags",
    flex: 1,
    minWidth: 120,
    sortable: false,
    renderCell: (params) => {
      const tags = params.value ?? [];
      if (tags.length === 0) {
        return (
          <Typography variant="body2" sx={{ color: "text.disabled" }}>
            -
          </Typography>
        );
      }
      const shown = tags.slice(0, 2);
      const extra = tags.length - shown.length;
      return (
        <Stack direction="row" spacing={0.5} sx={{ alignItems: "center", overflow: "hidden" }}>
          {shown.map((tag) => (
            <Chip key={tag} label={tag} size="small" variant="outlined" />
          ))}
          {extra > 0 && (
            <Tooltip title={tags.join(", ")}>
              <Chip label={`+${extra}`} size="small" />
            </Tooltip>
          )}
        </Stack>
      );
    },
  },
  {
    field: "totp_secret",
    headerName: "2FA",
    width: 118,
    sortable: false,
    renderCell: (params) =>
      params.value ? (
        <TotpCell secret={params.value} onCopy={onCopy} />
      ) : (
        <Typography variant="body2" sx={{ color: "text.disabled" }}>
          -
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
      const { password_name, password_value, url, backed_up } = params.row;
      return (
        <Stack direction="row" spacing={0} sx={{ alignItems: "center", height: "100%" }}>
          <Box sx={{ visibility: url ? "visible" : "hidden" }}>
            <Tooltip title="Open website">
              <IconButton size="small" onClick={() => url && openUrl(url)}>
                <OpenInNewIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
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
