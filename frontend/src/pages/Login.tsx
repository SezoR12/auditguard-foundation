import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, roleHome } from "../auth";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null); setLoading(true);
    try {
      const u = await login(email, password);
      nav(roleHome(u.role), { replace: true });
    } catch (e: any) {
      setErr(e?.response?.data?.detail ?? "حدث خطأ غير متوقع");
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-full flex items-center justify-center p-6">
      <form onSubmit={onSubmit} className="w-full max-w-md bg-white shadow rounded-xl p-8 text-right space-y-4">
        <h1 className="text-2xl font-bold">تسجيل الدخول</h1>
        <p className="text-slate-500 text-sm">منصة AuditCore — لوحة التدقيق</p>
        <div>
          <label className="block mb-1 text-sm">البريد الإلكتروني</label>
          <input type="email" required value={email} onChange={e=>setEmail(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-right" dir="ltr" />
        </div>
        <div>
          <label className="block mb-1 text-sm">كلمة المرور</label>
          <input type="password" required value={password} onChange={e=>setPassword(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-right" dir="ltr" />
        </div>
        {err && <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded p-2">{err}</div>}
        <button disabled={loading} className="w-full bg-slate-900 text-white rounded-lg py-2 hover:bg-slate-800 disabled:opacity-50">
          {loading ? "جارٍ تسجيل الدخول..." : "دخول"}
        </button>
      </form>
    </div>
  );
}