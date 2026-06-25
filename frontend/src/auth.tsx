import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { api } from "./api";

export type Role = "owner" | "gm" | "manager" | "auditor" | "admin" | "appowner";
export interface User { id: string; email: string; full_name: string; role: Role; company_id: string; branch_id?: string | null; is_active: boolean; }

interface Ctx {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
}

const AuthCtx = createContext<Ctx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { setLoading(false); return; }
    api.get<User>("/auth/me").then(r => setUser(r.data)).catch(() => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }).finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const { data } = await api.post("/auth/login-json", { email, password });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    const me = await api.get<User>("/auth/me");
    setUser(me.data);
    return me.data;
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  }

  return <AuthCtx.Provider value={{ user, loading, login, logout }}>{children}</AuthCtx.Provider>;
}

export function useAuth() {
  const v = useContext(AuthCtx);
  if (!v) throw new Error("useAuth outside AuthProvider");
  return v;
}

export function ProtectedRoute({ roles, children }: { roles?: Role[]; children: ReactNode }) {
  const { user, loading } = useAuth();
  const loc = useLocation();
  if (loading) return <div className="p-6 text-center">جارٍ التحميل...</div>;
  if (!user) return <Navigate to="/login" state={{ from: loc }} replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export function roleHome(role: Role): string {
  switch (role) {
    case "owner": return "/owner";
    case "auditor": return "/auditor";
    case "manager": return "/manager";
    case "gm": return "/gm";
    default: return "/";
  }
}