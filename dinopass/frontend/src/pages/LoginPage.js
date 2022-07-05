import {useStoreActions, useStoreState} from 'easy-peasy'
import {
  Box,
  TextField,
  Stack,
} from '@mui/material';
import LoadingButton from '@mui/lab/LoadingButton';
import InputIcon from '@mui/icons-material/Input';

const LoginPage = () => {
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
  console.log(value);
  return (
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
          onClick={() => check({master_password: value})}
        >
          Login
        </LoadingButton>
        <LoadingButton
          loading={loading}
          loadingPosition="start"
          variant="outlined"
          startIcon={<InputIcon/>}
          onClick={() => {
            console.log("CUR")
            create({master_password: value})
          }}
        >
          Signup
        </LoadingButton>
      </Stack>
    </Box>
  )

}

export default LoginPage;