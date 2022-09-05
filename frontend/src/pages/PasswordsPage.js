import { useEffect } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { useStoreActions, useStoreState } from "easy-peasy";
import { useSnackbar } from "notistack";
import {Button} from "@mui/material";

import { getKeyDerivation, isAuth } from "../utils";

const PasswordsPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  const { get } = useStoreActions(
    (actions) => actions.dinopassModels.Passwords
  );

  const { error, passwords } = useStoreState(
    (state) => state.dinopassModels.Passwords
  );

  useEffect(() => {
    if (isAuth()) {
      get(getKeyDerivation());
    } else {
      enqueueSnackbar(error, { variant: "error" });
    }
  }, [enqueueSnackbar, error, get]);

  const columns = [
    {
      field: "password_name",
      headerName: "PasswordModel Name",
      width: 180,
      editable: true,
      flex: 1,
    },
    {
      field: "password_value",
      headerName: "PasswordModel Value",
      type: "string",
      editable: true,
      flex: 1,
      // renderCell: (params) => {
      //    console.log(params.row["password_value"]);
      //    return <Button>Show</Button>
      // }
    },
    {
      field: "description",
      headerName: "Description",
      type: "string",
      width: 180,
      editable: true,
      flex: 1,
    },
  ];

  return (
    <>
      <div>
        <div style={{ height: 300, width: "100%" }}>
          <DataGrid
            rows={passwords}
            columns={columns}
            experimentalFeatures={{ newEditingApi: true }}
            getRowId={(row) => row.password_name}
          />
        </div>
      </div>
    </>
  );
};

export default PasswordsPage;
