import {useStoreActions, useStoreState} from "easy-peasy";
import {useEffect, useState} from "react";
import {getKeyDerivation, isAuth} from "../utils";
import {Snackbar} from "@mui/material";
import {DataGrid} from '@mui/x-data-grid';

const PasswordsPage = () => {
  const [snackOpen, setSnackOpen] = useState({
    open: false,
    vertical: 'bottom',
    horizontal: 'right',
  });
  const {vertical, horizontal, open} = snackOpen;

  const {get} = useStoreActions((actions) => actions.dinopassModels.Passwords);

  const {
    error,
    passwords,
    loading
  } = useStoreState((state) => state.dinopassModels.Passwords)

  const handleClose = () => {
    setSnackOpen({...snackOpen, open: false});
  };

  useEffect(() => {
    if (isAuth()) {
      get(getKeyDerivation());
    } else {
      setSnackOpen({...snackOpen, open: true});
    }
  }, [get, setSnackOpen, snackOpen])

  const columns = [
    {field: 'password_name', headerName: 'Password Name', width: 180, editable: true, flex: 1},
    {field: 'password_value', headerName: 'Password Value', type: 'string', editable: true, flex: 1},
    {
      field: 'description',
      headerName: 'Description',
      type: 'string',
      width: 180,
      editable: true,
      flex: 1
    }
  ]

  return (
    <>
      <div>
        <div style={{height: 300, width: '100%'}}>
          <DataGrid
            rows={passwords}
            columns={columns}
            experimentalFeatures={{newEditingApi: true}}
            getRowId={(row) => row.password_name}
          />
        </div>
      </div>

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

export default PasswordsPage;