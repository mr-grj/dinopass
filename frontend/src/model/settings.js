import { action, thunk } from "easy-peasy";

import apiClient from "../api/client";

const DEFAULTS = {
  inactivity_ms: 120_000,
  warn_before_ms: 60_000,
  hidden_ms: 60_000,
  debounce_ms: 1_000,
  clipboard_clear_ms: 30_000,
};

const Settings = {
  loading: false,
  error: null,
  settings: DEFAULTS,

  setSettings: action((state, settings) => { state.settings = settings; }),
  setLoading: action((state, loading) => { state.loading = loading; }),
  setError: action((state, error) => { state.error = error; }),

  get: thunk(async (actions) => {
    actions.setLoading(true);
    try {
      const { data } = await apiClient.get("/settings");
      actions.setSettings(data);
    } catch {
      // keep defaults on failure
    } finally {
      actions.setLoading(false);
    }
  }),

  update: thunk(async (actions, payload) => {
    try {
      const { data } = await apiClient.patch("/settings", payload);
      actions.setSettings(data);
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to save settings.");
    }
  }),
};

export default Settings;
