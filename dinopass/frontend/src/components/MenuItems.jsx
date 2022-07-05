import * as React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";

import HomeIcon from '@mui/icons-material/Home';
import LoginIcon from '@mui/icons-material/Login';
import PasswordIcon from '@mui/icons-material/Password';

import {Link} from "react-router-dom";

export const mainListItems = (
  <div>
    <ListItemButton component={Link} to="/">
      <ListItemIcon>
        <HomeIcon/>
      </ListItemIcon>
      <ListItemText primary="Home"/>
    </ListItemButton>

    <ListItemButton component={Link} to="/passwords">
      <ListItemIcon>
        <PasswordIcon/>
      </ListItemIcon>
      <ListItemText primary="Passwords"/>
    </ListItemButton>
  </div>
);

export const secondaryListItems = (
  <div>
    <ListSubheader inset>Other sections</ListSubheader>
    <ListItemButton component={Link} to="/login">
      <ListItemIcon>
        <LoginIcon/>
      </ListItemIcon>
      <ListItemText primary="Login"/>
    </ListItemButton>
  </div>
);