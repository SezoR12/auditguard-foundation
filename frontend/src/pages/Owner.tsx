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

export default function Owner() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);

  useEffect(() => {
    api.get<DocumentItem[]>("/documents/company-documents")
      .then(res => setDocuments(res.data))
      .catch(err => console.error("فشل في جلب مستندات الشركة", err));
  }, []);

  return (
    <RoleLayout title="لوحة المالك">
      <div className="space-y-8">
        <p className="text-slate-600">صلاحيات المالك مفعّلة — عرض شامل لمستندات الشركة على الصندوق الذكي (Smart Box).</p>
        
        <div className="bg-white p-6 rounded-xl shadow border border-slate-100 space-y-6">
          <h2 className="text-xl font-bold text-slate-800 border-b border-slate-100 pb-4">مستندات الشركة المرفوعة</h2>
          
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
                    <td colSpan={4} className="py-8 text-center text-slate-400">
                      لا توجد مستندات مرفوعة للشركة حتى الآن
                    </td>
                  </tr>
                ) : (
                  documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-medium text-slate-800">{doc.original_filename}</td>
                      <td className="py-3 px-4 text-slate-600">{CATEGORY_LABELS[doc.doc_category] || doc.doc_category}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
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
      </div>
    </RoleLayout>
  );
}