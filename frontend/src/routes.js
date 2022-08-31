import LoginPage from "./pages/LoginPage";
import PasswordsPage from "./pages/PasswordsPage";
import { isAuth } from "./utils";

const userIsAuth = isAuth();

const routes = [
  {
    path: "/login",
    main: () => <LoginPage />,
  },
  {
    path: "/passwords",
    main: () =>
      userIsAuth ? <PasswordsPage /> : (window.location.href = "/login"),
  },
];

export default routes;