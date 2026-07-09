import { useCallback, useEffect, useRef } from "react";
import { useSnackbar } from "notistack";
import { useStoreState } from "easy-peasy";

import { formatDuration } from "../utils";

const wipe = () => navigator.clipboard.writeText("").catch(() => {});

const useClipboard = () => {
  const { enqueueSnackbar } = useSnackbar();
  const clearMs = useStoreState((s) => s.dinopassModels.settings.settings.clipboard_clear_ms);
  const clearAtRef = useRef(null);

  useEffect(() => {
    const onFocus = () => {
      const clearAt = clearAtRef.current;
      if (clearAt && Date.now() >= clearAt - 5_000) {
        clearAtRef.current = null;
        wipe();
      }
    };
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, []);

  return useCallback(
    (value) => {
      navigator.clipboard.writeText(value).then(() => {
        enqueueSnackbar(`Copied! Clipboard clears in ${formatDuration(clearMs)}.`, {
          variant: "success",
        });
        const clearAt = Date.now() + clearMs;
        clearAtRef.current = clearAt;
        setTimeout(() => {
          if (clearAtRef.current === clearAt && document.hasFocus()) {
            clearAtRef.current = null;
            wipe();
          }
        }, clearMs);
      });
    },
    [enqueueSnackbar, clearMs]
  );
};

export default useClipboard;
