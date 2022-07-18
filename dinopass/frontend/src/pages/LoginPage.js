import { useStoreActions, useStoreState } from "easy-peasy";
import { Box, Stack, TextField } from "@mui/material";
import DinoLoadingButton from "../components/DinoLoadingButton";
import { useSnackbar } from "notistack";

const LoginPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  const { check, create, setValue } = useStoreActions(
    (actions) => actions.dinopassModels.masterPassword
  );

  const { error, value, loading } = useStoreState(
    (state) => state.dinopassModels.masterPassword
  );

  const handleClickLogin = () => {
    check({ master_password: value });
    if (error) {
      enqueueSnackbar(error, { variant: "error" });
    }
  };
  const handleClickSignup = () => {
    create({ master_password: value });
    if (error) {
      enqueueSnackbar(error, { variant: "error" });
    }
  };

  return (
    <>
      <Box
        textAlign="center"
        component="form"
        sx={{ "& .MuiTextField-root": { m: 1, width: "25ch" } }}
        autoComplete="off"
      >
        <TextField
          required
          type="password"
          label="Master Password"
          variant="outlined"
          onChange={(e) => setValue(e.target.value)}
        />

        <Stack direction="row" spacing={2} justifyContent="center">
          <DinoLoadingButton
            buttonText="Login"
            handleClickLogin={handleClickLogin}
            loading={loading}
          />
          <DinoLoadingButton
            buttonText="Signup"
            handleClickLogin={handleClickSignup}
            loading={loading}
          />
        </Stack>
      </Box>
    </>
  );
};

export default LoginPage;
