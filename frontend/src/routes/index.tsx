import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../components/layout/AppLayout";
import { ProtectedRoute } from "./ProtectedRoute";
import { Login } from "../pages/Login";
import { Register } from "../pages/Register";
import { Dashboard } from "../pages/Dashboard";
import { Websites } from "../pages/Websites";
import { WebsiteDetails } from "../pages/WebsiteDetails";
import { ScanResultsPage } from "../pages/ScanResults";
import { Violations } from "../pages/Violations";
import { Reports } from "../pages/Reports";
import { SettingsPage } from "../pages/Settings";

export const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  {
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { path: "websites", element: <Websites /> },
      { path: "websites/:id", element: <WebsiteDetails /> },
      { path: "scans/:id", element: <ScanResultsPage /> },
      { path: "violations", element: <Violations /> },
      { path: "reports", element: <Reports /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
]);
