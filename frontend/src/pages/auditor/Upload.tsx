import { useState, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { api } from "../../api";

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

export default function AuditorUpload() {
  const [category, setCategory] = useState("invoice");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [myUploads, setMyUploads] = useState<DocumentItem[]>([]);
  const [pendingDocs, setPendingDocs] = useState<DocumentItem[]>([]);
  const [activeTab, setActiveTab] = useState<"my" | "pending">("my");

  const fetchDocuments = useCallback(async () => {
    try {
      const [myRes, pendingRes] = await Promise.all([
        api.get<DocumentItem[]>("/documents/my-uploads"),
        api.get<DocumentItem[]>("/documents/pending-certification"),
      ]);
      setMyUploads(myRes.data);
      setPendingDocs(pendingRes.data);
    } catch (err) {
      console.error("فشل في جلب المستندات", err);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;
      const file = acceptedFiles[0];

      setUploading(true);
      setProgress(0);
      setSuccessMsg(null);
      setErrorMsg(null);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_category", category);

      try {
        await api.post("/documents/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setProgress(percent);
            }
          },
        });
        setSuccessMsg("تم الرفع بنجاح");
        await fetchDocuments();
      } catch (err: any) {
        setErrorMsg(err.response?.data?.detail || "فشل في رفع الملف");
      } finally {
        setUploading(false);
      }
    },
    [category, fetchDocuments]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
  });

  const displayedDocs = activeTab === "my" ? myUploads : pendingDocs;

  return (
    <div className="space-y-8 text-right">
      <div className="bg-white p-6 rounded-xl shadow border border-slate-100 space-y-6">
        <h2 className="text-xl font-bold text-slate-800">رفع مستند جديد</h2>
        
        {/* Category Selector */}
        <div className="max-w-md">
          <label className="block text-sm font-medium text-slate-700 mb-2">تصنيف المستند</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-right bg-white shadow-sm focus:ring-2 focus:ring-slate-900"
          >
            {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? "border-slate-900 bg-slate-50" : "border-slate-300 hover:border-slate-400 bg-slate-50/50"
          }`}
        >
          <input {...getInputProps()} />
          <div className="space-y-2">
            <svg className="mx-auto h-12 w-12 text-slate-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="text-slate-700 font-medium">
              {isDragActive ? "أفلت الملف هنا..." : "اسحب وأفلت الملف هنا، أو انقر للاختيار"}
            </p>
            <p className="text-slate-400 text-xs">
              الملفات المدعومة: Excel, CSV, Word, الصور, PDF, تقارير JSON المشفرة (الحد الأقصى 50 ميغابايت)
            </p>
          </div>
        </div>

        {/* Progress & Messages */}
        {uploading && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-slate-600">
              <span>جارٍ الرفع...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div className="bg-slate-900 h-full transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}

        {successMsg && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 p-4 rounded-lg text-sm font-medium">
            {successMsg}
          </div>
        )}

        {errorMsg && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg text-sm font-medium">
            {errorMsg}
          </div>
        )}
      </div>

      {/* Tables Section */}
      <div className="bg-white p-6 rounded-xl shadow border border-slate-100 space-y-6">
        <div className="flex justify-between items-center border-b border-slate-100 pb-4">
          <h2 className="text-xl font-bold text-slate-800">قائمة المستندات</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab("my")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === "my" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              مستنداتي المرفوعة
            </button>
            <button
              onClick={() => setActiveTab("pending")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === "pending" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              مستندات بانتظار الاعتماد
            </button>
          </div>
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
              {displayedDocs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-slate-400">
                    لا توجد مستندات في هذه القائمة
                  </td>
                </tr>
              ) : (
                displayedDocs.map((doc) => (
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
  );
}
