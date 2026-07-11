import { useEffect, useState } from "react";
import { Box, CircularProgress, Tooltip, Typography } from "@mui/material";

import { generateTotp, totpRemaining } from "../../lib/totp";

const PERIOD = 30;

const TotpCell = ({ secret, onCopy }) => {
  const [code, setCode] = useState("");
  const [remaining, setRemaining] = useState(PERIOD);
  const [invalid, setInvalid] = useState(false);

  useEffect(() => {
    let active = true;
    const tick = async () => {
      try {
        const next = await generateTotp(secret);
        if (!active) return;
        setCode(next);
        setInvalid(false);
      } catch {
        if (active) setInvalid(true);
      }
      if (active) setRemaining(totpRemaining(PERIOD));
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [secret]);

  if (invalid) {
    return (
      <Typography variant="caption" sx={{ color: "error.main" }}>
        invalid
      </Typography>
    );
  }
  if (!code) return null;

  return (
    <Tooltip title="Copy 2FA code">
      <Box
        onClick={() => onCopy?.(code)}
        sx={{ display: "flex", alignItems: "center", gap: 0.75, cursor: "pointer" }}
      >
        <Typography
          variant="body2"
          sx={{ fontFamily: "'Space Mono', monospace", fontWeight: 700, color: "#1f7a68" }}
        >
          {code.slice(0, 3)} {code.slice(3)}
        </Typography>
        <CircularProgress
          variant="determinate"
          value={(remaining / PERIOD) * 100}
          size={16}
          thickness={5}
          sx={{ color: remaining <= 5 ? "warning.main" : "text.disabled" }}
        />
      </Box>
    </Tooltip>
  );
};

export default TotpCell;
