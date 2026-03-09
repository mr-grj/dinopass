import { useCallback, useEffect, useRef } from "react";
import { Button } from "@mui/material";
import { useSnackbar } from "notistack";

import { isAuth, removeKeyDerivation } from "../utils";

const INACTIVITY_MS = 15 * 60 * 1000;   // 15 minutes
const WARN_BEFORE_MS = 2 * 60 * 1000;   // warn 2 minutes before logout
const HIDDEN_MS = 10 * 60 * 1000;       // 10 minutes while tab is hidden
const DEBOUNCE_MS = 1_000;              // only reset timers once per second max

const ACTIVITY_EVENTS = ["mousemove", "mousedown", "keydown", "touchstart", "scroll"];

const useAutoLogout = () => {
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();

  const inactivityRef = useRef(null);
  const warnRef = useRef(null);
  const hiddenRef = useRef(null);
  const warnKeyRef = useRef(null);
  const lastResetRef = useRef(0);
  const resetRef = useRef(null); // stable ref so warning action button can call latest reset

  const logout = useCallback(() => {
    clearTimeout(inactivityRef.current);
    clearTimeout(warnRef.current);
    clearTimeout(hiddenRef.current);
    if (warnKeyRef.current) closeSnackbar(warnKeyRef.current);
    removeKeyDerivation();
    enqueueSnackbar("Logged out due to inactivity. Stay safe 🦖", { variant: "info" });
    window.location.replace("/login");
  }, [enqueueSnackbar, closeSnackbar]);

  const reset = useCallback(() => {
    if (!isAuth()) return;

    const now = Date.now();
    if (now - lastResetRef.current < DEBOUNCE_MS) return;
    lastResetRef.current = now;

    clearTimeout(inactivityRef.current);
    clearTimeout(warnRef.current);

    if (warnKeyRef.current) {
      closeSnackbar(warnKeyRef.current);
      warnKeyRef.current = null;
    }

    warnRef.current = setTimeout(() => {
      warnKeyRef.current = enqueueSnackbar(
        "You'll be logged out in 2 minutes due to inactivity.",
        {
          variant: "warning",
          persist: true,
          action: (key) => (
            <Button
              size="small"
              color="inherit"
              sx={{ fontWeight: 700 }}
              onClick={() => { closeSnackbar(key); resetRef.current?.(); }}
            >
              Stay logged in
            </Button>
          ),
        }
      );
    }, INACTIVITY_MS - WARN_BEFORE_MS);

    inactivityRef.current = setTimeout(logout, INACTIVITY_MS);
  }, [enqueueSnackbar, closeSnackbar, logout]);

  // Keep resetRef pointing at latest reset so the warning action button always works
  useEffect(() => {
    resetRef.current = reset;
  }, [reset]);

  // Activity listeners
  useEffect(() => {
    if (!isAuth()) return;
    reset();
    ACTIVITY_EVENTS.forEach((e) => window.addEventListener(e, reset, { passive: true }));
    return () => {
      ACTIVITY_EVENTS.forEach((e) => window.removeEventListener(e, reset));
      clearTimeout(inactivityRef.current);
      clearTimeout(warnRef.current);
      if (warnKeyRef.current) closeSnackbar(warnKeyRef.current);
    };
  }, [reset, closeSnackbar]);

  // Tab visibility listener
  useEffect(() => {
    if (!isAuth()) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        hiddenRef.current = setTimeout(logout, HIDDEN_MS);
      } else {
        clearTimeout(hiddenRef.current);
        if (!isAuth()) {
          logout();
        } else {
          reset();
        }
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      clearTimeout(hiddenRef.current);
    };
  }, [logout, reset]);
};

export default useAutoLogout;
