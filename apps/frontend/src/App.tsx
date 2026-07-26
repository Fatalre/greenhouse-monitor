import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";
import { isAuthenticated } from "./api/client";
import { AppLayout } from "./layouts/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { ExperimentsPage } from "./pages/ExperimentsPage";
import { LoginPage } from "./pages/LoginPage";
import { MeasurementsPage } from "./pages/MeasurementsPage";
import { SystemPage } from "./pages/SystemPage";

function ProtectedRoute() {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="measurements" element={<MeasurementsPage />} />
            <Route path="experiments" element={<ExperimentsPage />} />
            <Route path="devices" element={<DevicesPage />} />
            <Route path="system" element={<SystemPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}