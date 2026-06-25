import { useState, useEffect } from "react";
import RoleLayout from "./_layout";
import AuditorUpload from "./auditor/Upload";
import { api } from "../api";

interface AuditorDashboardData {
  company: { id: string; name: string; sector: string; tier: string };
  branches: { id: string; name: string; location: string }[];
  stats: { assigned_tasks: number; my_uploads: number; pending_certification: number };
  tasks: { id: string; title: string; task_type: string; status: string; demerit_points: number }[];
}

const TASK_STATUS_LABELS: Record<string, string> = {
  pending: "قيد الانتظار",
  in_progress: "قيد التنفيذ",
  completed: "مكتمل",
  overdue: "متأخر",
};

export default function Auditor() {
  const [dash, setDash] = useState<AuditorDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState<"tasks" | "upload">("upload");

  useEffect(() => {
    api.get<AuditorDashboardData>("/dashboard/auditor")
      .then(res => setDash(res.data))
      .catch(err => console.error("فشل في جلب بيانات المدقق", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <RoleLayout title="لوحة المدقق"><div className="p-12 text-center text-slate-500 font-medium">جارٍ تحميل بيانات المدقق...</div></RoleLayout>;
  }

  return (
    <RoleLayout title="لوحة المدقق">
      <div className="space-y-8">
        {/* Company Info Banner */}
        {dash && (
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-extrabold text-slate-900">{dash.company.name}</h2>
              <div className="flex items-center gap-3 text-slate-500 text-sm mt-1">
                <span>القطاع: <strong className="text-slate-700">{dash.company.sector}</strong></span>
                <span>•</span>
                <span>الفئة (Tier): <strong className="text-indigo-600 font-bold uppercase">{dash.company.tier}</strong></span>
              </div>
            </div>
            <div className="flex gap-2">
              {dash.branches.map(b => (
                <span key={b.id} className="bg-slate-100 border border-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-lg font-medium">
                  📍 {b.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Real Data Metrics Stats Grid */}
        {dash && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
              <div className="text-slate-500 text-sm font-medium">مهام التدقيق المسندة لي</div>
              <div className="text-3xl font-extrabold text-indigo-600 mt-2">{dash.stats.assigned_tasks}</div>
              <div className="text-indigo-700 text-xs font-bold bg-indigo-50 border border-indigo-200 py-1 px-2 rounded mt-3 text-center">
                جدول الأعمال الحالي
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
              <div className="text-slate-500 text-sm font-medium">مستنداتي المرفوعة</div>
              <div className="text-3xl font-extrabold text-emerald-600 mt-2">{dash.stats.my_uploads}</div>
              <div className="text-emerald-700 text-xs font-bold bg-emerald-50 border border-emerald-200 py-1 px-2 rounded mt-3 text-center">
                مشفرة بـ AES-256-GCM
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
              <div className="text-slate-500 text-sm font-medium">مستندات بانتظار الاعتماد</div>
              <div className="text-3xl font-extrabold text-amber-600 mt-2">{dash.stats.pending_certification}</div>
              <div className="text-amber-700 text-xs font-bold bg-amber-50 border border-amber-200 py-1 px-2 rounded mt-3 text-center">
                تتطلب مراجعة المدقق
              </div>
            </div>
          </div>
        )}

        {/* RLS Informational Banner */}
        <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-amber-900 text-sm font-medium flex items-center justify-between gap-4">
          <div>
            🔒 <strong>تطبيق فوري لـ Row-Level Security:</strong> كمدقق، يتم حجب جداول <code>analytics_outputs</code>، <code>waste_map_items</code>، و <code>risk_alerts</code> عنك تلقائياً على مستوى قاعدة البيانات (PostgreSQL RLS).
          </div>
        </div>

        {/* Role-based Navigation Tabs */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <h3 className="text-xl font-extrabold text-slate-900">نظام إدارة التدقيق والمستندات</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveView("upload")}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  activeView === "upload" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                بوابة رفع وإدارة المستندات
              </button>
              <button
                onClick={() => setActiveView("tasks")}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  activeView === "tasks" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                مهام التدقيق المسندة ({dash?.tasks.length || 0})
              </button>
            </div>
          </div>

          {activeView === "upload" && <AuditorUpload />}

          {activeView === "tasks" && dash && (
            <div className="overflow-x-auto">
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-sm text-slate-500 font-medium">
                    <th className="py-3 px-4">عنوان المهمة</th>
                    <th className="py-3 px-4">التكرار</th>
                    <th className="py-3 px-4">الحالة</th>
                    <th className="py-3 px-4">نقاط المخالفة</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {dash.tasks.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-slate-400 font-medium">
                        لا توجد مهام تدقيق مسندة إليك حالياً
                      </td>
                    </tr>
                  ) : (
                    dash.tasks.map(t => (
                      <tr key={t.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-bold text-slate-900">{t.title}</td>
                        <td className="py-3 px-4 text-slate-600 uppercase">{t.task_type}</td>
                        <td className="py-3 px-4">
                          <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2.5 py-1 rounded-full">
                            {TASK_STATUS_LABELS[t.status] || t.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-600 font-bold">{t.demerit_points}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </RoleLayout>
  );
}
