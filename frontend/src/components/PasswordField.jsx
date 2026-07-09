import { useState } from "react";
import { IconButton, InputAdornment, TextField, Tooltip } from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";

const PasswordField = ({ show: showProp, onToggleShow, adornment = null, slotProps, ...props }) => {
  const [showInternal, setShowInternal] = useState(false);
  const controlled = showProp !== undefined;
  const show = controlled ? showProp : showInternal;
  const toggle = controlled ? onToggleShow : () => setShowInternal((v) => !v);

  return (
    <TextField
      fullWidth
      type={show ? "text" : "password"}
      {...props}
      slotProps={{
        ...slotProps,
        htmlInput: {
          spellCheck: false,
          autoCorrect: "off",
          autoCapitalize: "none",
          ...slotProps?.htmlInput,
        },
        input: {
          ...slotProps?.input,
          endAdornment: (
            <InputAdornment position="end">
              {adornment}
              <Tooltip title={show ? "Hide" : "Show"}>
                <IconButton onClick={toggle} edge="end" size="small">
                  {show ? (
                    <VisibilityOffIcon fontSize="small" />
                  ) : (
                    <VisibilityIcon fontSize="small" />
                  )}
                </IconButton>
              </Tooltip>
            </InputAdornment>
          ),
        },
      }}
    />
  );
};

export default PasswordField;
