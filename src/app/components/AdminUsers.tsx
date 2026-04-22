import { useState, useEffect } from "react";
import { useAuth } from "./AuthContext";
import {
  Users, Zap, Plus, Trash2, CheckCircle2, XCircle,
  UserCheck, UserX, X, AlertTriangle,
} from "lucide-react";

export default function AdminUsers() {
  const { users, fetchUsers, updateUser, addQuota, deleteUser, deleteUsers } = useAuth();
  const normalUsers = users.filter((u) => u.role === "user");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadUsers = async () => {
      setLoading(true);
      await fetchUsers();
      setLoading(false);
    };
    loadUsers();
  }, [fetchUsers]);

  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [quotaModal, setQuotaModal] = useState<{ userId: number; username: string } | null>(null);
  const [quotaAmount, setQuotaAmount] = useState("10");
  const [confirmDelete, setConfirmDelete] = useState<{ ids: number[]; names: string[] } | null>(null);

  const allSelected = normalUsers.length > 0 && normalUsers.every((u) => selected.has(u.id));

  const toggleAll = () => {
    if (allSelected) setSelected(new Set());
    else setSelected(new Set(normalUsers.map((u) => u.id)));
  };
  const toggle = (id: number) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const selectedUsers = normalUsers.filter((u) => selected.has(u.id));

  const batchEnable = async () => {
    setLoading(true);
    for (const u of selectedUsers) {
      await updateUser(u.id, { status: "active" });
    }
    setLoading(false);
  };
  const batchDisable = async () => {
    setLoading(true);
    for (const u of selectedUsers) {
      await updateUser(u.id, { status: "disabled" });
    }
    setLoading(false);
  };
  const batchDeleteConfirm = () => {
    if (selectedUsers.length === 0) return;
    setConfirmDelete({ ids: selectedUsers.map((u) => u.id), names: selectedUsers.map((u) => u.username) });
  };
  const singleDeleteConfirm = (u: { id: number; username: string }) => {
    setConfirmDelete({ ids: [u.id], names: [u.username] });
  };

  const doDelete = async () => {
    if (!confirmDelete) return;
    setLoading(true);
    if (confirmDelete.ids.length === 1) {
      await deleteUser(confirmDelete.ids[0]);
    } else {
      await deleteUsers(confirmDelete.ids);
    }
    setSelected((prev) => {
      const next = new Set(prev);
      confirmDelete.ids.forEach((id) => next.delete(id));
      return next;
    });
    setConfirmDelete(null);
    setLoading(false);
  };

  const doAddQuota = async () => {
    if (!quotaModal) return;
    const amt = parseInt(quotaAmount);
    if (isNaN(amt) || amt <= 0) return;
    setLoading(true);
    await addQuota(quotaModal.userId, amt);
    setQuotaModal(null);
    setQuotaAmount("10");
    setLoading(false);
  };

  const activeCount = normalUsers.filter((u) => u.status === "active").length;
  const totalRemaining = normalUsers.reduce((s, u) => s + u.remainingQuota, 0);
  const totalUsed = normalUsers.reduce((s, u) => s + u.usedQuota, 0);

  return (
    <div className="h-full flex flex-col">
      {/* Summary cards */}
      <div className="px-6 pt-5 pb-2 grid grid-cols-4 gap-3">
        {[
          { label: "总用户", value: normalUsers.length, icon: Users, color: "text-blue-600 bg-blue-50 dark:bg-blue-500/10 dark:text-blue-400" },
          { label: "已启用", value: activeCount, icon: CheckCircle2, color: "text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 dark:text-emerald-400" },
          { label: "剩余总额度", value: totalRemaining, icon: Zap, color: "text-amber-600 bg-amber-50 dark:bg-amber-500/10 dark:text-amber-400" },
          { label: "已消耗总额度", value: totalUsed, icon: Zap, color: "text-rose-600 bg-rose-50 dark:bg-rose-500/10 dark:text-rose-400" },
        ].map((c) => (
          <div key={c.label} className="bg-card rounded-xl border border-border p-4 flex items-center gap-3">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${c.color}`}>
              <c.icon className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[12px] text-muted-foreground">{c.label}</p>
              <p className="text-[20px] tabular-nums">{c.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Batch toolbar */}
      <div className="px-6 py-3 flex items-center gap-2">
        <span className="text-[13px] text-muted-foreground flex-1">
          {selected.size > 0 ? `已选 ${selected.size} 个用户` : `共 ${normalUsers.length} 个用户`}
        </span>
        {selected.size > 0 && (
          <>
            <button onClick={batchEnable}
              className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400 rounded-lg hover:shadow-sm transition-all">
              <UserCheck className="w-3.5 h-3.5" /> 批量启用
            </button>
            <button onClick={batchDisable}
              className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400 rounded-lg hover:shadow-sm transition-all">
              <UserX className="w-3.5 h-3.5" /> 批量禁用
            </button>
            <button onClick={batchDeleteConfirm}
              className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400 rounded-lg hover:shadow-sm transition-all">
              <Trash2 className="w-3.5 h-3.5" /> 批量删除
            </button>
          </>
        )}
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto px-6 pb-4">
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <table className="w-full text-[14px]">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left px-4 py-3 w-10">
                  <input type="checkbox" checked={allSelected} onChange={toggleAll}
                    className="w-4 h-4 rounded border-border accent-primary cursor-pointer" />
                </th>
                {["账号", "状态", "剩余额度", "已用额度", "注册时间", "最近登录", "操作"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-[13px] text-muted-foreground whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {normalUsers.map((u) => (
                <tr key={u.id} className={`hover:bg-accent/30 transition-colors ${selected.has(u.id) ? "bg-primary/5" : ""}`}>
                  <td className="px-4 py-3">
                    <input type="checkbox" checked={selected.has(u.id)} onChange={() => toggle(u.id)}
                      className="w-4 h-4 rounded border-border accent-primary cursor-pointer" />
                  </td>
                  <td className="px-4 py-3">{u.username}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-lg text-[12px] ${
                      u.status === "active"
                        ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400"
                        : "bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400"
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${u.status === "active" ? "bg-emerald-500" : "bg-red-500"}`} />
                      {u.status === "active" ? "启用" : "禁用"}
                    </span>
                  </td>
                  <td className="px-4 py-3 tabular-nums">{u.remainingQuota}</td>
                  <td className="px-4 py-3 tabular-nums text-muted-foreground">{u.usedQuota}</td>
                  <td className="px-4 py-3 text-[13px] text-muted-foreground">{u.registeredAt}</td>
                  <td className="px-4 py-3 text-[13px] text-muted-foreground">{u.lastLoginAt}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => setQuotaModal({ userId: u.id, username: u.username })}
                        title="加额度"
                        className="p-1.5 hover:bg-primary/10 rounded-lg transition-all text-primary">
                        <Plus className="w-4 h-4" />
                      </button>
                      {u.status === "active" ? (
                        <button onClick={async () => {
                            setLoading(true);
                            await updateUser(u.id, { status: "disabled" });
                            setLoading(false);
                          }}
                          title="禁用"
                          className="p-1.5 hover:bg-amber-500/10 rounded-lg transition-all text-amber-500">
                          <UserX className="w-4 h-4" />
                        </button>
                      ) : (
                        <button onClick={async () => {
                            setLoading(true);
                            await updateUser(u.id, { status: "active" });
                            setLoading(false);
                          }}
                          title="启用"
                          className="p-1.5 hover:bg-emerald-500/10 rounded-lg transition-all text-emerald-500">
                          <UserCheck className="w-4 h-4" />
                        </button>
                      )}
                      <button onClick={() => singleDeleteConfirm(u)}
                        title="删除"
                        className="p-1.5 hover:bg-red-500/10 rounded-lg transition-all text-red-500">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {loading && normalUsers.length === 0 && (
                <tr><td colSpan={8} className="text-center py-16 text-[14px] text-muted-foreground">
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                    加载中...
                  </div>
                </td></tr>
              )}
              {!loading && normalUsers.length === 0 && (
                <tr><td colSpan={8} className="text-center py-16 text-[14px] text-muted-foreground">暂无用户数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Quota Modal */}
      {quotaModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setQuotaModal(null)}>
          <div className="bg-card rounded-2xl border border-border shadow-2xl w-[400px]" onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-5 border-b border-border flex items-center justify-between">
              <h3 className="text-[17px]">增加额度</h3>
              <button onClick={() => setQuotaModal(null)} className="p-1.5 hover:bg-accent rounded-lg"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-[14px] text-muted-foreground">
                为用户 <span className="text-foreground">{quotaModal.username}</span> 增加识别额度
              </p>
              <div className="flex gap-2">
                {[5, 10, 20, 50, 100].map((n) => (
                  <button key={n} onClick={() => setQuotaAmount(String(n))}
                    className={`px-3 py-1.5 text-[13px] rounded-lg border transition-all ${
                      quotaAmount === String(n) ? "bg-primary text-primary-foreground border-primary" : "border-border hover:bg-accent"
                    }`}>+{n}</button>
                ))}
              </div>
              <div>
                <label className="text-[13px] text-muted-foreground block mb-1.5">自定义数量</label>
                <input type="number" value={quotaAmount} onChange={(e) => setQuotaAmount(e.target.value)} min={1}
                  className="w-full bg-muted/60 border border-border rounded-lg px-3 py-2 text-[14px] focus:ring-2 focus:ring-primary/20 focus:border-primary/50" />
              </div>
            </div>
            <div className="px-6 py-5 border-t border-border flex justify-end gap-3">
              <button onClick={() => setQuotaModal(null)} className="px-4 py-2 text-[14px] border border-border rounded-xl hover:bg-accent transition-all">取消</button>
              <button onClick={doAddQuota}
                className="px-4 py-2 text-[14px] bg-primary text-primary-foreground rounded-xl hover:shadow-md transition-all">
                确认添加 +{quotaAmount || 0}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Modal */}
      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setConfirmDelete(null)}>
          <div className="bg-card rounded-2xl border border-border shadow-2xl w-[420px]" onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-5 border-b border-border flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-red-50 dark:bg-red-500/10 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-500" />
              </div>
              <h3 className="text-[17px]">确认删除</h3>
            </div>
            <div className="p-6">
              <p className="text-[14px] text-muted-foreground">
                确定要删除以下 <span className="text-foreground">{confirmDelete.ids.length}</span> 个用户吗？此操作不可撤销。
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {confirmDelete.names.map((n) => (
                  <span key={n} className="text-[12px] px-2 py-0.5 rounded-lg bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400">{n}</span>
                ))}
              </div>
            </div>
            <div className="px-6 py-5 border-t border-border flex justify-end gap-3">
              <button onClick={() => setConfirmDelete(null)} className="px-4 py-2 text-[14px] border border-border rounded-xl hover:bg-accent transition-all">取消</button>
              <button onClick={doDelete}
                className="px-4 py-2 text-[14px] bg-red-500 text-white rounded-xl hover:bg-red-600 hover:shadow-md transition-all">
                确认删除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
