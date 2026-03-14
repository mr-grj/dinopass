import LoadingButton from "@mui/lab/LoadingButton";

const DinoLoadingButton = ({
  buttonText,
  loading,
  onClick,
  variant = "contained",
  fullWidth = false,
}) => (
  <LoadingButton
    fullWidth={fullWidth}
    loading={loading}
    onClick={onClick}
    variant={variant}
    size="large"
  >
    {buttonText}
  </LoadingButton>
);

export default DinoLoadingButton;
