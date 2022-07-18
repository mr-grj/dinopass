import InputIcon from "@mui/icons-material/Input";
import LoadingButton from "@mui/lab/LoadingButton";

const DinoLoadingButton = (props) => {
  const { buttonText, handleClickLogin, loading } = props;

  return (
    <LoadingButton
      loading={loading}
      loadingPosition="start"
      onClick={handleClickLogin}
      startIcon={<InputIcon />}
      type="submit"
      variant="contained"
    >
      {buttonText}
    </LoadingButton>
  );
};

export default DinoLoadingButton;
