import { useCallback, useEffect, useRef, useState } from "react";
import { Box, Button, IconButton, Stack, Tooltip, Typography } from "@mui/material";
import AttachFileIcon from "@mui/icons-material/AttachFile";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutlined";
import FileDownloadOutlinedIcon from "@mui/icons-material/FileDownloadOutlined";
import { useSnackbar } from "notistack";
import { useStoreActions } from "easy-peasy";

import ConfirmDialog from "../ConfirmDialog";

const MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024;

const formatBytes = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const AttachmentsSection = ({ passwordName, onChanged }) => {
  const { enqueueSnackbar } = useSnackbar();
  const fetchAttachments = useStoreActions((a) => a.ciphermothModels.passwords.fetchAttachments);
  const uploadAttachment = useStoreActions((a) => a.ciphermothModels.passwords.uploadAttachment);
  const downloadAttachment = useStoreActions(
    (a) => a.ciphermothModels.passwords.downloadAttachment
  );
  const deleteAttachment = useStoreActions((a) => a.ciphermothModels.passwords.deleteAttachment);

  const [attachments, setAttachments] = useState([]);
  const [busy, setBusy] = useState(false);
  const [pendingDelete, setPendingDelete] = useState(null);
  const inputRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      setAttachments(await fetchAttachments(passwordName));
    } catch (err) {
      enqueueSnackbar(err.message, { variant: "error" });
    }
  }, [fetchAttachments, passwordName, enqueueSnackbar]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleFiles = async (files) => {
    setBusy(true);
    try {
      for (const file of files) {
        if (file.size > MAX_ATTACHMENT_BYTES) {
          enqueueSnackbar(`"${file.name}" is larger than 5 MB.`, { variant: "warning" });
          continue;
        }
        await uploadAttachment({ passwordName, file });
        enqueueSnackbar(`Attached "${file.name}".`, { variant: "success" });
        onChanged?.();
      }
      await refresh();
    } catch (err) {
      enqueueSnackbar(err.message, { variant: "error" });
    } finally {
      setBusy(false);
    }
  };

  const onPick = (e) => {
    const files = Array.from(e.target.files ?? []);
    e.target.value = "";
    if (files.length) handleFiles(files);
  };

  const onDownload = async (att) => {
    try {
      await downloadAttachment({
        passwordName,
        attachmentId: att.id,
        filename: att.filename,
      });
    } catch (err) {
      enqueueSnackbar(err.message, { variant: "error" });
    }
  };

  const confirmDelete = async () => {
    const att = pendingDelete;
    setPendingDelete(null);
    try {
      await deleteAttachment({ passwordName, attachmentId: att.id });
      enqueueSnackbar(`Removed "${att.filename}".`, { variant: "success" });
      onChanged?.();
      await refresh();
    } catch (err) {
      enqueueSnackbar(err.message, { variant: "error" });
    }
  };

  return (
    <Stack spacing={1}>
      {attachments.length === 0 ? (
        <Typography variant="body2" sx={{ color: "text.disabled" }}>
          No files attached yet. Files are encrypted with your vault key.
        </Typography>
      ) : (
        attachments.map((att) => (
          <Stack key={att.id} direction="row" spacing={1} sx={{ alignItems: "center" }}>
            <AttachFileIcon fontSize="small" sx={{ color: "text.disabled" }} />
            <Typography
              variant="body2"
              sx={{
                flex: 1,
                minWidth: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {att.filename}
            </Typography>
            <Typography variant="caption" sx={{ color: "text.disabled", flexShrink: 0 }}>
              {formatBytes(att.size_bytes)}
            </Typography>
            <Tooltip title="Download">
              <IconButton size="small" onClick={() => onDownload(att)}>
                <FileDownloadOutlinedIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Remove file">
              <IconButton size="small" color="error" onClick={() => setPendingDelete(att)}>
                <DeleteOutlineIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        ))
      )}

      <Box>
        <input ref={inputRef} type="file" multiple hidden onChange={onPick} />
        <Button
          size="small"
          startIcon={<AttachFileIcon />}
          onClick={() => inputRef.current?.click()}
          loading={busy}
        >
          Attach file
        </Button>
        <Typography variant="caption" sx={{ color: "text.disabled", ml: 1 }}>
          Up to 5 MB each, 25 MB total.
        </Typography>
      </Box>

      <ConfirmDialog
        open={!!pendingDelete}
        title="Remove attachment?"
        onClose={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
        confirmText="Remove"
        confirmColor="error"
      >
        Permanently delete &quot;{pendingDelete?.filename}&quot; from this entry? This cannot be
        undone.
      </ConfirmDialog>
    </Stack>
  );
};

export default AttachmentsSection;
