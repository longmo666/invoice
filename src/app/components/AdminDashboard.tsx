import { useNavigate } from "react-router";
import { useAuth } from "./AuthContext";
import {
  Users, FileText, TrainFront, FolderSync, Zap, Activity,
  ArrowUpRight,
} from "lucide-react";

const allInvoiceCount = 7;
const allTrainCount = 5;
const allCleanCount = 5;
const allCleanDone = 3;
const totalInvoiceAmount = 110371.35;
const totalTrainAmount = 2426.5;

export default function AdminDashboard() {
  const { users } = useAuth();
  const navigate = useNavigate();
  const normalUsers = users.filter((u) => u.role === "user");
  const activeUsers = normalUsers.filter((u) => u.status === "active").length;
  const totalQuotaUsed = normalUsers.reduce((s, u) => s + u.usedQuota, 0);
  const totalQuotaRemaining = normalUsers.reduce((s, u) => s + u.remainingQuota, 0);

  const statCards = [
    { label: "注册用户", value: normalUsers.length, sub: `${activeUsers} 启用`, icon: Users, gradient: "from-blue-500 to-indigo-600", bg: "bg-blue-50 dark:bg-blue-500/10", path: "/admin/users" },
    { label: "发票识别", value: allInvoiceCount, sub: `¥${totalInvoiceAmount.toLocaleString()}`, icon: FileText, gradient: "from-emerald-500 to-teal-600", bg: "bg-emerald-50 dark:bg-emerald-500/10", path: "/admin/invoices" },
    { label: "高铁票识别", value: allTrainCount, sub: `¥${totalTrainAmount.toLocaleString()}`, icon: TrainFront, gradient: "from-violet-500 to-purple-600", bg: "bg-violet-50 dark:bg-violet-500/10", path: "/admin/trains" },
    { label: "文件清洗", value: allCleanCount, sub: `${allCleanDone} 完成`, icon: FolderSync, gradient: "from-amber-500 to-orange-600", bg: "bg-amber-50 dark:bg-amber-500/10", path: "/admin/cleaning" },
    { label: "总消耗次数", value: totalQuotaUsed, sub: `剩余 ${totalQuotaRemaining}`, icon: Zap, gradient: "from-rose-500 to-pink-600", bg: "bg-rose-50 dark:bg-rose-500/10", path: "/admin/users" },
    { label: "今日活跃", value: activeUsers, sub: "过去24小时", icon: Activity, gradient: "from-cyan-500 to-blue-600", bg: "bg-cyan-50 dark:bg-cyan-500/10", path: "/admin/users" },
  ];

  return (
    <div className="p-6 max-w-[1200px] mx-auto">
      <div className="mb-6">
        <h3 className="text-[15px] text-muted-foreground mb-1">欢迎回来，管理员</h3>
        <p className="text-[13px] text-muted-foreground/60">点击卡片可查看详细数据</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {statCards.map((card) => (
          <button
            key={card.label}
            onClick={() => navigate(card.path)}
            className="group bg-card rounded-2xl border border-border p-5 hover:shadow-lg hover:shadow-black/5 hover:-translate-y-0.5 transition-all duration-200 text-left relative overflow-hidden"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className={`w-10 h-10 rounded-xl ${card.bg} flex items-center justify-center`}>
                <card.icon className="w-5 h-5 text-primary" />
              </div>
              <span className="text-[13px] text-muted-foreground">{card.label}</span>
              <ArrowUpRight className="w-4 h-4 text-muted-foreground/0 group-hover:text-primary ml-auto transition-all duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </div>
            <p className="text-[28px] tabular-nums tracking-tight">{card.value.toLocaleString()}</p>
            <p className="text-[12px] text-muted-foreground mt-1">{card.sub}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
