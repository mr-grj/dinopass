import React from "react";
import ReactDOM from "react-dom/client";
import { StoreProvider } from "easy-peasy";
import { SnackbarProvider } from "notistack";

import App from "./App";
import { store } from "./store";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <StoreProvider store={store}>
    <SnackbarProvider
      preventDuplicate
      maxSnack={3}
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "right",
      }}
    >
      <App />
    </SnackbarProvider>
  </StoreProvider>
);
