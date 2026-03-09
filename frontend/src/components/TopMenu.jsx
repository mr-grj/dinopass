import { Link, useLocation } from "react-router-dom";
import { AppBar, Button, Toolbar, Typography } from "@mui/material";

import { isAuth, removeKeyDerivation } from "../utils";

const TopMenu = () => {
  const userIsAuth = isAuth();
  const { pathname } = useLocation();

  return (
    <AppBar position="absolute">
      <Toolbar sx={{ pr: "24px" }}>
        <Typography component="h1" variant="h6" color="inherit" noWrap sx={{ flexGrow: 1 }}>
          Dinopass 🦖
        </Typography>

        {userIsAuth ? (
          <Button component={Link} to="/login" color="inherit" onClick={removeKeyDerivation}>
            Log out
          </Button>
        ) : (
          pathname !== "/login" && (
            <Button component={Link} to="/login" color="inherit">
              Log in
            </Button>
          )
        )}
      </Toolbar>
    </AppBar>
  );
};

export default TopMenu;
