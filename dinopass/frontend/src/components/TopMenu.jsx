import * as React from "react";

import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography/Typography";

import { AppBar, Button } from "@mui/material";
import { removeKeyDerivation } from "../utils";

import { Link } from "react-router-dom";

const TopMenu = (props) => {
  const { userIsAuth } = props;

  return (
    <AppBar position="absolute">
      <Toolbar sx={{ pr: "24px" }}>
        <Typography
          component="h1"
          variant="h6"
          color="inherit"
          noWrap
          sx={{ flexGrow: 1 }}
        >
          Dinopass 🦖
        </Typography>

        <Typography component="h2" variant="h6" color="inherit" noWrap>
          {userIsAuth ? (
            <Button
              component={Link}
              to="/login"
              color="inherit"
              onClick={removeKeyDerivation}
            >
              Log out
            </Button>
          ) : (
            <Button component={Link} to="/login" color="inherit">
              Log in
            </Button>
          )}
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default TopMenu;
