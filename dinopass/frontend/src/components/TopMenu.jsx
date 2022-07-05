import * as React from "react";

import {styled} from "@mui/material/styles";
import MuiAppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import Badge from "@mui/material/Badge";
import NotificationsIcon from "@mui/icons-material/Notifications";
import Typography from "@mui/material/Typography/Typography";

import {useStoreActions, useStoreState} from 'easy-peasy'

const drawerWidth = 240;

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({theme, open}) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const TopMenu = () => {
  const {open} = useStoreState(
    state => state.dinopassModels.menu
  )
  const {setOpen} = useStoreActions(
    actions => actions.dinopassModels.menu
  )

  const toggleDrawer = () => {
    setOpen();
  };

  return (
    <AppBar position="absolute" open={open}>
      <Toolbar sx={{pr: '24px',}}>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="open drawer"
          onClick={toggleDrawer}
          sx={{marginRight: '36px', ...(open && {display: 'none'}),}}
        >
          <MenuIcon/>
        </IconButton>
        <Typography
          component="h1"
          variant="h6"
          color="inherit"
          noWrap
          sx={{flexGrow: 1}}
        >
          Dinopass 🦖
        </Typography>
        <IconButton color="inherit" sx={{marginLeft: '2px!important'}}>
          <Badge badgeContent={4} color="secondary">
            <NotificationsIcon/>
          </Badge>
        </IconButton>
      </Toolbar>
    </AppBar>
  )
}

export default TopMenu;