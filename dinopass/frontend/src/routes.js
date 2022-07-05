import LoginPage from './pages/LoginPage'
import PasswordsPage from './pages/PasswordsPage'
import WelcomePage from "./pages/WelcomePage";

const routes = [
  {
    exact: true,
    path: "/",
    main: () => <WelcomePage/>
  },
  {
    path: "/login",
    main: () => <LoginPage/>
  },
  {
    path: "/passwords",
    main: () => <PasswordsPage/>
  },
];

export default routes;
