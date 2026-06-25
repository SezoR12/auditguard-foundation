import { ReactNode } from "react";
import { useAuth } from "../auth";

export default function RoleLayout({ title, children }: { title: string; children?: ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-full">
      <header className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="text-lg font-bold">AuditCore — {title}</div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-600">{user?.email}</span>
            <button onClick={logout} className="text-red-600 hover:underline">خروج</button>
          </div>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-6 py-8 text-right">
        <h1 className="text-2xl font-bold mb-2">مرحباً {user?.full_name}</h1>
        {children}
      </main>
    </div>
  );
}