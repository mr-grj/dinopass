import * as React from "react";

import {styled} from "@mui/material/styles";
import MuiDrawer from "@mui/material/Drawer";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import Divider from "@mui/material/Divider";
import List from "@mui/material/List";
import {useStoreActions, useStoreState} from 'easy-peasy'

import {mainListItems, secondaryListItems} from "./MenuItems";

const drawerWidth = 240;

const Drawer = styled(MuiDrawer, {shouldForwardProp: (prop) => prop !== 'open'})(
  ({theme, open}) => ({
    '& .MuiDrawer-paper': {
      position: 'relative',
      whiteSpace: 'nowrap',
      width: drawerWidth,
      transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
      boxSizing: 'border-box',
      ...(!open && {
        overflowX: 'hidden',
        transition: theme.transitions.create('width', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        width: theme.spacing(7),
        [theme.breakpoints.up('sm')]: {
          width: theme.spacing(9),
        },
      }),
    },
  }),
);

const LeftMenu = () => {
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
    <Drawer variant="permanent" open={open}>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          px: [1],
        }}
      >
        <IconButton onClick={toggleDrawer}>
          <ChevronLeftIcon/>
        </IconButton>
      </Toolbar>
      <Divider/>

      <List>{mainListItems}</List>
      <Divider/>
      <List>{secondaryListItems}</List>
    </Drawer>
  )
}

export default LeftMenu;