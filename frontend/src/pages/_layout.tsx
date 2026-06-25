import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { useAuth, roleHome } from "../auth";

const ROLE_NAMES: Record<string, string> = {
  owner: "المالك (Owner)",
  auditor: "المدقق (Auditor)",
  manager: "المدير (Manager)",
  gm: "المدير العام (GM)",
  admin: "مسؤول النظام (Admin)",
  appowner: "مالك التطبيق (App Owner)",
};

export default function RoleLayout({ title, children }: { title: string; children?: ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-full bg-slate-50 text-slate-900">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to={user ? roleHome(user.role) : "/"} className="text-xl font-extrabold text-slate-900 tracking-tight">
              Audit<span className="text-indigo-600">Core</span>
            </Link>
            <span className="text-slate-300">|</span>
            <span className="text-sm font-bold text-slate-700 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
              {title}
            </span>
          </div>

          <div className="flex items-center gap-4 text-sm font-medium">
            {user && (
              <nav className="flex items-center gap-3 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
                <span className="text-xs text-indigo-600 font-bold bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                  {ROLE_NAMES[user.role] || user.role}
                </span>
                <span className="text-slate-600">{user.email}</span>
              </nav>
            )}
            <button
              onClick={logout}
              className="bg-red-50 text-red-600 border border-red-200 px-4 py-1.5 rounded-lg hover:bg-red-100 transition-colors font-bold text-xs"
            >
              تسجيل الخروج
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8 text-right">
        <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white p-8 rounded-2xl shadow-xl mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-extrabold mb-2">مرحباً {user?.full_name}</h1>
            <p className="text-slate-300 text-sm font-medium">
              مرحباً بك في منصة التدقيق الذكية AuditCore — الحماية والامتثال الفوري عبر الصندوق الذكي (Smart Box).
            </p>
          </div>
          <div className="hidden md:block bg-white/10 backdrop-blur border border-white/10 px-6 py-4 rounded-xl text-center">
            <div className="text-xs text-slate-300 mb-1">دور المستخدم الحالي</div>
            <div className="text-lg font-extrabold text-indigo-300">{ROLE_NAMES[user?.role || ""] || user?.role}</div>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}