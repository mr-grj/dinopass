import { Navigate } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import PasswordsPage from "./pages/PasswordsPage";
import SettingsPage from "./pages/SettingsPage";
import { isAuth } from "./utils";

const ProtectedRoute = ({ children }) => {
  if (!isAuth()) return <Navigate to="/login" replace />;
  return children;
};

const routes = [
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/passwords",
    element: (
      <ProtectedRoute>
        <PasswordsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/settings",
    element: (
      <ProtectedRoute>
        <SettingsPage />
      </ProtectedRoute>
    ),
  },
];

export default routes;
