import { useState, useEffect } from "react";
import RoleLayout from "./_layout";
import { api } from "../api";

interface DocumentItem {
  id: string;
  original_filename: string;
  doc_category: string;
  status: string;
  created_at: string;
}

interface DashboardData {
  company: { id: string; name: string; sector: string; tier: string };
  branches: { id: string; name: string; location: string }[];
  stats: { total_users: number; total_waste_iqd: number; total_risk_impact_iqd: number; trust_index: number };
  analytics: { id: string; output_type: string; data: any; trust_index: number }[];
  waste_items: { id: string; category: string; amount_iqd: number; department: string; description: string; status: string }[];
  risk_alerts: { id: string; severity: string; title: string; description: string; financial_impact: number; status: string }[];
  recent_tasks: { id: string; title: string; task_type: string; status: string; demerit_points: number }[];
}

const CATEGORY_LABELS: Record<string, string> = {
  invoice: "فاتورة",
  bank_statement: "كشف حساب بنكي",
  contract: "عقد",
  inventory_report: "تقرير جرد",
  encrypted_report: "تقرير محاسبي مشفر",
  report: "تقرير",
  receipt: "إيصال",
  other: "أخرى",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "قيد الانتظار",
  ocr_processing: "قيد معالجة OCR",
  certified: "معتمد",
};

const SEVERITY_LABELS: Record<string, string> = {
  low: "منخفض",
  medium: "متوسط",
  high: "مرتفع",
  critical: "حرج جداً",
};

const TASK_STATUS_LABELS: Record<string, string> = {
  pending: "قيد الانتظار",
  in_progress: "قيد التنفيذ",
  completed: "مكتمل",
  overdue: "متأخر",
};

export default function Owner() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [dash, setDash] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"analytics" | "waste" | "risks" | "tasks" | "documents">("analytics");

  useEffect(() => {
    Promise.all([
      api.get<DashboardData>("/dashboard/owner"),
      api.get<DocumentItem[]>("/documents/company-documents")
    ])
    .then(([dashRes, docsRes]) => {
      setDash(dashRes.data);
      setDocuments(docsRes.data);
    })
    .catch(err => console.error("فشل في جلب بيانات المالك", err))
    .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <RoleLayout title="لوحة المالك"><div className="p-12 text-center text-slate-500 font-medium">جارٍ تحميل بيانات لوحة التحكم...</div></RoleLayout>;
  }

  return (
    <RoleLayout title="لوحة المالك">
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
              <div className="text-slate-500 text-sm font-medium">مؤشر الثقة (Trust Index)</div>
              <div className="text-3xl font-extrabold text-emerald-600 mt-2">{dash.stats.trust_index}%</div>
              <div className="text-emerald-700 text-xs font-bold bg-emerald-50 border border-emerald-200 py-1 px-2 rounded mt-3 text-center">
                محمي بـ Row-Level Security
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
              <div className="text-slate-500 text-sm font-medium">إجمالي الهدر المكتشف</div>
              <div className="text-3xl font-extrabold text-rose-600 mt-2">
                {dash.stats.total_waste_iqd.toLocaleString()} <span className="text-sm text-slate-500 font-bold">د.ع</span>
              </div>
              <div className="text-rose-700 text-xs font-bold bg-rose-50 border border-rose-200 py-1 px-2 rounded mt-3 text-center">
                محجوب عن المدققين
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
              <div className="text-slate-500 text-sm font-medium">الأثر المالي للمخاطر</div>
              <div className="text-3xl font-extrabold text-amber-600 mt-2">
                {dash.stats.total_risk_impact_iqd.toLocaleString()} <span className="text-sm text-slate-500 font-bold">د.ع</span>
              </div>
              <div className="text-amber-700 text-xs font-bold bg-amber-50 border border-amber-200 py-1 px-2 rounded mt-3 text-center">
                تنبيهات فورية الذكاء الاصطناعي
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
              <div className="text-slate-500 text-sm font-medium">مستخدمي الشركة النشطين</div>
              <div className="text-3xl font-extrabold text-indigo-600 mt-2">{dash.stats.total_users}</div>
              <div className="text-indigo-700 text-xs font-bold bg-indigo-50 border border-indigo-200 py-1 px-2 rounded mt-3 text-center">
                صلاحيات RBAC مفعلة
              </div>
            </div>
          </div>
        )}

        {/* Role-based Navigation Tabs */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <h3 className="text-xl font-extrabold text-slate-900">بيانات التحليلات والتدقيق (صلاحيات المالك)</h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setActiveTab("analytics")}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  activeTab === "analytics" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                مخرجات التحليلات (Analytics)
              </button>
              <button
                onClick={() => setActiveTab("waste")}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  activeTab === "waste" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                خريطة الهدر (Waste Map)
              </button>
              <button
                onClick={() => setActiveTab("risks")}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  activeTab === "risks" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                تنبيهات المخاطر (Risk Alerts)
              </button>
              <button
                onClick={() => setActiveTab("tasks")}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  activeTab === "tasks" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                مهام التدقيق الحالية
              </button>
              <button
                onClick={() => setActiveTab("documents")}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  activeTab === "documents" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                المستندات المرفوعة ({documents.length})
              </button>
            </div>
          </div>

          {/* Tab 1: Analytics Outputs */}
          {activeTab === "analytics" && dash && (
            <div className="space-y-4">
              <div className="bg-indigo-50 border border-indigo-200 p-4 rounded-xl text-indigo-900 text-sm font-medium">
                🔒 <strong>معلومة أمان RLS:</strong> هذا الجدول (<code>analytics_outputs</code>) محمي بقواعد Row-Level Security في قاعدة البيانات ومحجوب تماماً عن المدققين.
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dash.analytics.map(a => (
                  <div key={a.id} className="bg-slate-50 border border-slate-200 p-6 rounded-xl space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="bg-indigo-100 text-indigo-800 text-xs font-bold px-2.5 py-1 rounded-full uppercase">
                        {a.output_type}
                      </span>
                      <span className="text-emerald-700 font-bold text-sm">مؤشر الثقة: {a.trust_index}%</span>
                    </div>
                    <pre className="bg-white border border-slate-200 p-4 rounded-lg text-left text-xs text-slate-700 overflow-x-auto" dir="ltr">
                      {JSON.stringify(a.data, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 2: Waste Map Items */}
          {activeTab === "waste" && dash && (
            <div className="space-y-4">
              <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl text-rose-900 text-sm font-medium">
                🔒 <strong>معلومة أمان RLS:</strong> جدول خريطة الهدر (<code>waste_map_items</code>) محجوب بالكامل عن المدققين.
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-right border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-sm text-slate-500 font-medium">
                      <th className="py-3 px-4">الفئة</th>
                      <th className="py-3 px-4">القسم</th>
                      <th className="py-3 px-4">المبلغ (د.ع)</th>
                      <th className="py-3 px-4">الوصف</th>
                      <th className="py-3 px-4">الحالة</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    {dash.waste_items.map(w => (
                      <tr key={w.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-bold text-slate-800 uppercase">{w.category}</td>
                        <td className="py-3 px-4 text-slate-700 font-medium">{w.department}</td>
                        <td className="py-3 px-4 font-extrabold text-rose-600">{w.amount_iqd.toLocaleString()}</td>
                        <td className="py-3 px-4 text-slate-600">{w.description}</td>
                        <td className="py-3 px-4">
                          <span className="bg-rose-100 text-rose-800 text-xs font-bold px-2.5 py-1 rounded-full">{w.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 3: Risk Alerts */}
          {activeTab === "risks" && dash && (
            <div className="space-y-4">
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-amber-900 text-sm font-medium">
                🔒 <strong>معلومة أمان RLS:</strong> جدول التنبيهات (<code>risk_alerts</code>) محمي بقواعد RLS ولا يظهر للمدققين.
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-right border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-sm text-slate-500 font-medium">
                      <th className="py-3 px-4">درجة الخطورة</th>
                      <th className="py-3 px-4">العنوان</th>
                      <th className="py-3 px-4">الوصف</th>
                      <th className="py-3 px-4">الأثر المالي (د.ع)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    {dash.risk_alerts.map(r => (
                      <tr key={r.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                            r.severity === "high" || r.severity === "critical" ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800"
                          }`}>
                            {SEVERITY_LABELS[r.severity] || r.severity}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-bold text-slate-900">{r.title}</td>
                        <td className="py-3 px-4 text-slate-600">{r.description}</td>
                        <td className="py-3 px-4 font-extrabold text-amber-600">{r.financial_impact.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 4: Audit Tasks */}
          {activeTab === "tasks" && dash && (
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
                  {dash.recent_tasks.map(t => (
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
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Tab 5: Documents */}
          {activeTab === "documents" && (
            <div className="space-y-4">
              <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl text-slate-700 text-sm font-medium">
                📂 <strong>ملفات الصندوق الذكي (Smart Box):</strong> جميع الملفات مشفرة على القرص المحلي باستخدام خوارزمية AES-256-GCM.
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-right border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-sm text-slate-500 font-medium">
                      <th className="py-3 px-4">اسم الملف</th>
                      <th className="py-3 px-4">التصنيف</th>
                      <th className="py-3 px-4">الحالة</th>
                      <th className="py-3 px-4">تاريخ الرفع</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    {documents.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-slate-400 font-medium">
                          لا توجد مستندات مرفوعة للشركة حتى الآن
                        </td>
                      </tr>
                    ) : (
                      documents.map((doc) => (
                        <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                          <td className="py-3 px-4 font-bold text-slate-800">{doc.original_filename}</td>
                          <td className="py-3 px-4 text-slate-600">{CATEGORY_LABELS[doc.doc_category] || doc.doc_category}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                              doc.status === "certified" ? "bg-emerald-100 text-emerald-800" :
                              doc.status === "ocr_processing" ? "bg-amber-100 text-amber-800" :
                              "bg-blue-100 text-blue-800"
                            }`}>
                              {STATUS_LABELS[doc.status] || doc.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-500">
                            {new Date(doc.created_at).toLocaleDateString("ar-EG", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </RoleLayout>
  );
}
