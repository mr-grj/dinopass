import { action, thunk } from "easy-peasy";

import apiClient from "../api/client";

const Passwords = {
  error: null,
  loading: false,
  passwords: [],
  trash: [],

  setError: action((state, error) => {
    state.error = error;
  }),
  setLoading: action((state, loading) => {
    state.loading = loading;
  }),
  setPasswords: action((state, passwords) => {
    state.passwords = passwords;
  }),
  setTrash: action((state, trash) => {
    state.trash = trash;
  }),

  get: thunk(async (actions) => {
    actions.setLoading(true);
    actions.setError(null);
    try {
      const { data } = await apiClient.get("/passwords");
      actions.setPasswords(data);
    } catch (err) {
      actions.setError(err.response?.data?.detail ?? "Failed to load passwords.");
    } finally {
      actions.setLoading(false);
    }
  }),

  create: thunk(async (actions, payload) => {
    try {
      await apiClient.post("/passwords/create", payload);
      await actions.get();
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to create password.");
    }
  }),

  update: thunk(async (actions, payload) => {
    try {
      await apiClient.patch("/passwords/update", payload);
      await actions.get();
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to update password.");
    }
  }),

  remove: thunk(async (actions, passwordName) => {
    try {
      await apiClient.delete(`/passwords/${encodeURIComponent(passwordName)}`);
      await actions.get();
      await actions.getTrash();
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to delete password.");
    }
  }),

  getTrash: thunk(async (actions) => {
    try {
      const { data } = await apiClient.get("/passwords/trash");
      actions.setTrash(data);
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to load trash.");
    }
  }),

  restore: thunk(async (actions, passwordName) => {
    try {
      await apiClient.post(`/passwords/${encodeURIComponent(passwordName)}/restore`);
      await actions.get();
      await actions.getTrash();
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to restore password.");
    }
  }),

  purge: thunk(async (actions, passwordName) => {
    try {
      await apiClient.delete(`/passwords/${encodeURIComponent(passwordName)}/purge`);
      await actions.getTrash();
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to delete password.");
    }
  }),

  toggleFavorite: thunk(async (actions, { passwordName, favorite }) => {
    try {
      await apiClient.patch(`/passwords/${encodeURIComponent(passwordName)}/favorite`, {
        favorite,
      });
      await actions.get();
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to update favorite.");
    }
  }),

  fetchAttachments: thunk(async (actions, passwordName) => {
    try {
      const { data } = await apiClient.get(
        `/passwords/${encodeURIComponent(passwordName)}/attachments`
      );
      return data;
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to load attachments.");
    }
  }),

  uploadAttachment: thunk(async (actions, { passwordName, file }) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await apiClient.post(
        `/passwords/${encodeURIComponent(passwordName)}/attachments`,
        formData
      );
      await actions.get();
      return data;
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to upload attachment.");
    }
  }),

  downloadAttachment: thunk(async (actions, { passwordName, attachmentId, filename }) => {
    try {
      const response = await apiClient.get(
        `/passwords/${encodeURIComponent(passwordName)}/attachments/${attachmentId}`,
        { responseType: "blob" }
      );
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename || "attachment";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      let detail = "Failed to download attachment.";
      if (err.response?.data instanceof Blob) {
        try {
          detail = JSON.parse(await err.response.data.text()).detail ?? detail;
        } catch {
          // Blob wasn't JSON; fall back to the generic message.
        }
      } else {
        detail = err.response?.data?.detail ?? detail;
      }
      throw new Error(detail);
    }
  }),

  deleteAttachment: thunk(async (actions, { passwordName, attachmentId }) => {
    try {
      await apiClient.delete(
        `/passwords/${encodeURIComponent(passwordName)}/attachments/${attachmentId}`
      );
      await actions.get();
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to delete attachment.");
    }
  }),

  importPasswords: thunk(async (actions, { file, masterPassword, onConflict }) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("master_password", masterPassword);
      formData.append("on_conflict", onConflict);
      const { data } = await apiClient.post("/passwords/import", formData);
      await actions.get();
      return data;
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Import failed.");
    }
  }),

  importCsv: thunk(async (actions, { file, onConflict }) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("on_conflict", onConflict);
      const { data } = await apiClient.post("/passwords/import/csv", formData);
      await actions.get();
      return data;
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Import failed.");
    }
  }),

  backup: thunk(async (actions, masterPassword) => {
    try {
      const response = await apiClient.post(
        "/passwords/backup",
        { master_password: masterPassword },
        { responseType: "blob" }
      );
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = `ciphermoth_backup_${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.zip`;
      link.click();
      URL.revokeObjectURL(url);
      await actions.get();
    } catch (err) {
      let detail = "Backup failed.";
      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          detail = JSON.parse(text).detail ?? detail;
        } catch {
          // Blob wasn't JSON; fall back to the generic message.
        }
      } else {
        detail = err.response?.data?.detail ?? detail;
      }
      throw new Error(detail);
    }
  }),
};

export default Passwords;
