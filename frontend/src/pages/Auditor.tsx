import RoleLayout from "./_layout";
import AuditorUpload from "./auditor/Upload";

export default function Auditor() {
  return (
    <RoleLayout title="لوحة المدقق">
      <div className="space-y-6">
        <p className="text-slate-600">لوحة تحكم المدقق — نظام إدارة المستندات الآمن</p>
        <AuditorUpload />
      </div>
    </RoleLayout>
  );
}