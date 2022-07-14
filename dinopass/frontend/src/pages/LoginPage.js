import {useState} from "react";
import {useStoreActions, useStoreState} from 'easy-peasy'
import {
  Box,
  TextField,
  Snackbar,
  Stack,
} from '@mui/material';
import LoadingButton from '@mui/lab/LoadingButton';
import InputIcon from '@mui/icons-material/Input';


const LoginPage = () => {
  const [snackOpen, setSnackOpen] = useState({
    open: false,
    vertical: 'bottom',
    horizontal: 'right',
  });
  const {vertical, horizontal, open} = snackOpen;

  const {
    check,
    create,
    setValue
  } = useStoreActions((actions) => actions.dinopassModels.masterPassword);

  const {
    error,
    value,
    loading
  } = useStoreState((state) => state.dinopassModels.masterPassword)

  const handleClickLogin = () => {
    check({master_password: value});
    setSnackOpen({...snackOpen, open: true});
  };
  const handleClickSignup = () => {
    create({master_password: value});
    setSnackOpen({...snackOpen, open: true});
  };
  const handleClose = () => {
    setSnackOpen({...snackOpen, open: false});
  };

  return (
    <>

      <Box
        textAlign='center'
        component="form"
        sx={{
          '& .MuiTextField-root': {m: 1, width: '25ch'},
        }}
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
          <LoadingButton
            loading={loading}
            loadingPosition="start"
            variant="contained"
            startIcon={<InputIcon/>}
            onClick={handleClickLogin}
          >
            Login
          </LoadingButton>
          <LoadingButton
            loading={loading}
            loadingPosition="start"
            variant="outlined"
            startIcon={<InputIcon/>}
            onClick={handleClickSignup}
          >
            Signup
          </LoadingButton>
        </Stack>
      </Box>

      <Snackbar
        anchorOrigin={{vertical, horizontal}}
        open={open}
        onClose={handleClose}
        message={error}
        key={vertical + horizontal}
      />
    </>
  )

}

export default LoginPage;