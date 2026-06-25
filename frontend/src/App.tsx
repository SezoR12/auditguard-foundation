import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import Owner from "./pages/Owner";
import Auditor from "./pages/Auditor";
import Manager from "./pages/Manager";
import GM from "./pages/GM";
import { ProtectedRoute, useAuth, roleHome } from "./auth";

function Root() {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-6 text-center">جارٍ التحميل...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={roleHome(user.role)} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Root />} />
      <Route path="/login" element={<Login />} />
      <Route path="/owner" element={<ProtectedRoute roles={["owner"]}><Owner /></ProtectedRoute>} />
      <Route path="/auditor" element={<ProtectedRoute roles={["auditor"]}><Auditor /></ProtectedRoute>} />
      <Route path="/manager" element={<ProtectedRoute roles={["manager"]}><Manager /></ProtectedRoute>} />
      <Route path="/gm" element={<ProtectedRoute roles={["gm"]}><GM /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}