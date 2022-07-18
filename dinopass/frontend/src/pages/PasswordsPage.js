import { useStoreActions, useStoreState } from "easy-peasy";
import { useEffect } from "react";
import { getKeyDerivation, isAuth } from "../utils";
import { useSnackbar } from "notistack";
import { DataGrid } from "@mui/x-data-grid";

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
      headerName: "Password Name",
      width: 180,
      editable: true,
      flex: 1,
    },
    {
      field: "password_value",
      headerName: "Password Value",
      type: "string",
      editable: true,
      flex: 1,
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
