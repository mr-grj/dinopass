import { Box, Chip, Tooltip } from "@mui/material";

import { DEV_ACCENT, IS_DEV } from "../lib/appEnv";
import { GLOW, INK } from "../lib/brand";

const DEV_TOOLTIP =
  "Development sandbox. Throwaway data only. make clean wipes it, and your real " +
  "vault lives on a separate stack.";
const LIVE_TOOLTIP = "Your real vault. These are the passwords that actually matter.";

const baseSx = {
  height: 22,
  fontFamily: "'Space Mono', monospace",
  fontSize: 10,
  letterSpacing: "0.12em",
  borderRadius: 1,
  cursor: "help",
  "& .MuiChip-label": { px: 0.9 },
};

const EnvBadge = () => (
  <Tooltip arrow title={IS_DEV ? DEV_TOOLTIP : LIVE_TOOLTIP}>
    <Chip
      size="small"
      label={
        IS_DEV ? (
          "DEV"
        ) : (
          <Box component="span" sx={{ display: "inline-flex", alignItems: "center", gap: 0.6 }}>
            <Box
              component="span"
              sx={{
                width: 5,
                height: 5,
                borderRadius: "50%",
                bgcolor: GLOW,
                boxShadow: `0 0 5px ${GLOW}`,
              }}
            />
            LIVE
          </Box>
        )
      }
      variant={IS_DEV ? "filled" : "outlined"}
      aria-label={IS_DEV ? "Development environment" : "Live vault"}
      sx={
        IS_DEV
          ? { ...baseSx, fontWeight: 700, bgcolor: DEV_ACCENT, color: INK }
          : {
              ...baseSx,
              color: GLOW,
              borderColor: `color-mix(in srgb, ${GLOW} 45%, transparent)`,
            }
      }
    />
  </Tooltip>
);

export default EnvBadge;
