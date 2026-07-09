import { Chip, Tooltip } from "@mui/material";

import { DEV_ACCENT, IS_DEV } from "../lib/appEnv";

const DEV_TOOLTIP =
  "Development sandbox. Throwaway data only. Your dino treats this as a chew toy, " +
  "make clean wipes it, and your real vault lives on a separate stack.";
const LIVE_TOOLTIP = "Your real vault. These are the passwords that actually matter.";

const baseSx = {
  height: 22,
  fontWeight: 800,
  fontSize: 11,
  letterSpacing: "0.09em",
  borderRadius: 1,
  cursor: "help",
  "& .MuiChip-label": { px: 0.9 },
};

const EnvBadge = () => (
  <Tooltip arrow title={IS_DEV ? DEV_TOOLTIP : LIVE_TOOLTIP}>
    <Chip
      size="small"
      label={IS_DEV ? "DEV" : "LIVE"}
      variant={IS_DEV ? "filled" : "outlined"}
      aria-label={IS_DEV ? "Development environment" : "Live vault"}
      sx={
        IS_DEV
          ? { ...baseSx, bgcolor: DEV_ACCENT, color: "#1a1a1a" }
          : {
              ...baseSx,
              fontWeight: 700,
              color: "rgba(255,255,255,0.82)",
              borderColor: "rgba(255,255,255,0.32)",
            }
      }
    />
  </Tooltip>
);

export default EnvBadge;
