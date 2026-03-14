import { action, thunk } from "easy-peasy";

import apiClient from "../api/client";
import { setKeyDerivation } from "../utils";

const MasterPassword = {
  initialized: null,
  error: null,
  loading: false,
  value: "",
  confirm: "",

  setInitialized: action((state, val) => {
    state.initialized = val;
  }),
  setValue: action((state, value) => {
    state.value = value;
  }),
  setConfirm: action((state, value) => {
    state.confirm = value;
  }),
  setError: action((state, error) => {
    state.error = error;
  }),
  setLoading: action((state, loading) => {
    state.loading = loading;
  }),

  fetchStatus: thunk(async (actions) => {
    try {
      const { data } = await apiClient.get("/master_password/status");
      actions.setInitialized(data.initialized);
    } catch {
      actions.setInitialized(true);
    }
  }),

  check: thunk(async (actions, masterPasswordPayload) => {
    actions.setError(null);
    actions.setLoading(true);
    try {
      const { data } = await apiClient.post("/master_password/check", masterPasswordPayload);
      if (data.valid && data.key_derivation) {
        setKeyDerivation(data.key_derivation);
        window.location.replace("/passwords");
      } else {
        actions.setError("Invalid master password.");
      }
    } catch (err) {
      const msg =
        err.response?.status === 429
          ? "Too many attempts. Please try again in an hour."
          : (err.response?.data?.detail ?? "An error occurred.");
      actions.setError(msg);
    } finally {
      actions.setLoading(false);
    }
  }),

  create: thunk(async (actions, masterPasswordPayload) => {
    actions.setError(null);
    actions.setLoading(true);
    try {
      const { data } = await apiClient.post("/master_password/create", masterPasswordPayload);
      setKeyDerivation(data.key_derivation);
      window.location.replace("/passwords");
    } catch (err) {
      actions.setError(err.response?.data?.detail ?? "An error occurred.");
    } finally {
      actions.setLoading(false);
    }
  }),
};

export default MasterPassword;
