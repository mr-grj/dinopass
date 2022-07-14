import * as React from "react";

import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography/Typography";

import {AppBar} from "@mui/material";

const TopMenu = (props) => {
  const {userIsAuth} = props;

  return (
    <AppBar position="absolute">
      <Toolbar sx={{pr: '24px',}}>
        <Typography
          component="h1"
          variant="h6"
          color="inherit"
          noWrap
          sx={{flexGrow: 1}}
        >
          Dinopass 🦖
        </Typography>

        <Typography
          component="h2"
          variant="h6"
          color="inherit"
          noWrap
        >
          {userIsAuth ? 'Logged in': 'You are not logged in'}
        </Typography>
      </Toolbar>
    </AppBar>
  )
}

export default TopMenu;