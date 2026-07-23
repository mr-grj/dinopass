import { action, thunk } from "easy-peasy";

import apiClient from "../api/client";
import { errorDetail } from "../lib/http";
import { getUpdateStatus } from "../lib/updateCheck";

const Updates = {
  current: null,
  latest: null,
  releaseUrl: null,
  updateAvailable: false,
  checking: false,
  apply: { state: "idle", detail: null, updater_present: false },

  setStatus: action((state, status) => {
    if (!status) return;
    state.current = status.current;
    state.latest = status.latest;
    state.releaseUrl = status.releaseUrl;
    state.updateAvailable = status.updateAvailable;
  }),
  setVersion: action((state, version) => {
    state.current = version;
  }),
  setChecking: action((state, checking) => {
    state.checking = checking;
  }),
  setApply: action((state, apply) => {
    state.apply = { ...state.apply, ...apply };
  }),

  fetchVersion: thunk(async (actions) => {
    try {
      const { data } = await apiClient.get("/meta");
      actions.setVersion(data.version);
    } catch {
      // version just won't show if the backend can't be reached
    }
  }),

  checkForUpdates: thunk(async (actions) => {
    actions.setChecking(true);
    try {
      actions.setStatus(await getUpdateStatus());
    } finally {
      actions.setChecking(false);
    }
  }),

  fetchApplyStatus: thunk(async (actions) => {
    try {
      const { data } = await apiClient.get("/updates/apply/status", { timeout: 5000 });
      actions.setApply(data);
      return data;
    } catch {
      return null;
    }
  }),

  applyUpdate: thunk(async (actions, target) => {
    try {
      const { data } = await apiClient.post("/updates/apply", { target });
      actions.setApply(data);
      return data;
    } catch (err) {
      throw new Error(await errorDetail(err, "Failed to start the update."));
    }
  }),
};

export default Updates;
