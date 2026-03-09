import { action, thunk } from "easy-peasy";

import apiClient from "../api/client";

const Passwords = {
  error: null,
  loading: false,
  passwords: [],

  setError: action((state, error) => {
    state.error = error;
  }),
  setLoading: action((state, loading) => {
    state.loading = loading;
  }),
  setPasswords: action((state, passwords) => {
    state.passwords = passwords;
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
    } catch (err) {
      throw new Error(err.response?.data?.detail ?? "Failed to delete password.");
    }
  }),
};

export default Passwords;
