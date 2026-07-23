// Shared DataGrid styling for the vault grids (main list + trash): divider
// border, vertically-centred cells, and no focus outline on cells.
export const gridBaseSx = {
  borderColor: "divider",
  "& .MuiDataGrid-cell": { display: "flex", alignItems: "center" },
  "& .MuiDataGrid-cell:focus": { outline: "none" },
  "& .MuiDataGrid-cell:focus-within": { outline: "none" },
};
