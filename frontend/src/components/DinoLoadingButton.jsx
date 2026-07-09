import Button from "@mui/material/Button";

const DinoLoadingButton = ({
  buttonText,
  loading,
  onClick,
  variant = "contained",
  fullWidth = false,
}) => (
  <Button fullWidth={fullWidth} loading={loading} onClick={onClick} variant={variant} size="large">
    {buttonText}
  </Button>
);

export default DinoLoadingButton;
