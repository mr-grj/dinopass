import { Box, Typography, useTheme } from "@mui/material";

import MothIcon from "./MothIcon";
import { GLOW, TOTP } from "../lib/brand";

const LoadingScreen = ({ label = "UNLOCKING" }) => {
  const theme = useTheme();
  const dark = theme.palette.mode === "dark";

  return (
    <Box
      sx={{
        position: "fixed",
        inset: 0,
        bgcolor: "background.default",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 3.25,
        zIndex: (t) => t.zIndex.modal + 1,
        "@keyframes cmPulse": {
          "0%, 100%": { opacity: 0.3, transform: "scale(0.9)" },
          "50%": { opacity: 0.75, transform: "scale(1.08)" },
        },
        "@keyframes cmOrbit": {
          from: { transform: "rotate(0deg) translateX(52px) rotate(0deg)" },
          to: { transform: "rotate(360deg) translateX(52px) rotate(-360deg)" },
        },
        "@keyframes cmFlutter": {
          "0%, 100%": { transform: "scaleX(1)" },
          "50%": { transform: "scaleX(0.82)" },
        },
        "@keyframes cmBlink": {
          "0%, 45%, 55%, 100%": { opacity: 1 },
          "50%": { opacity: 0.15 },
        },
      }}
    >
      <Box
        sx={{
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Box
          sx={{
            position: "absolute",
            width: 150,
            height: 150,
            borderRadius: "50%",
            background: `radial-gradient(circle, color-mix(in srgb, ${GLOW} 40%, transparent), transparent 62%)`,
            animation: "cmPulse 3s ease-in-out infinite",
          }}
        />
        <Box
          sx={{
            position: "absolute",
            width: 6,
            height: 6,
            borderRadius: "50%",
            bgcolor: GLOW,
            boxShadow: `0 0 10px ${GLOW}`,
            animation: "cmOrbit 4.5s linear infinite",
          }}
        />
        <Box
          sx={{
            width: 78,
            color: "text.primary",
            position: "relative",
            filter: `drop-shadow(0 0 14px color-mix(in srgb, ${GLOW} 55%, transparent))`,
            "& > svg": {
              animation: "cmFlutter 1.6s ease-in-out infinite",
              transformOrigin: "50% 40%",
            },
          }}
        >
          <MothIcon
            withAntennae={false}
            width="100%"
            height="100%"
            style={{ display: "block", overflow: "visible" }}
          />
        </Box>
      </Box>
      <Typography
        sx={{
          fontFamily: "'Space Mono', monospace",
          fontSize: 13,
          letterSpacing: "0.16em",
          color: dark ? GLOW : TOTP,
        }}
      >
        {label}
        <Box component="span" sx={{ animation: "cmBlink 1.4s steps(1) infinite" }}>
          …
        </Box>
      </Typography>
    </Box>
  );
};

export default LoadingScreen;
