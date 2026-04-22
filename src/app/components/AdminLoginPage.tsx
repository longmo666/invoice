import { useState } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "./AuthContext";
import { Zap, Eye, EyeOff, LogIn, Shield } from "lucide-react";

export default function AdminLoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!username.trim()) { setError("请输入管理员账号"); return; }
    if (!password) { setError("请输入密码"); return; }

    setLoading(true);
    const result = await login(username.trim(), password, true);
    setLoading(false);
    if (result.success) {
      navigate("/admin");
    } else {
      setError(result.error || "登录失败");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center shadow-xl shadow-red-500/25 mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-[24px] tracking-tight">管理员登录</h1>
          <p className="text-[14px] text-muted-foreground mt-1">Admin Login Portal</p>
        </div>

        {/* Card */}
        <div className="bg-card rounded-2xl border border-border shadow-xl shadow-black/5 p-8">
          <h2 className="text-[18px] mb-6">管理员入口</h2>

          {error && (
            <div className="mb-4 px-4 py-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-[13px] flex items-center gap-2">
              <Shield className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[13px] text-muted-foreground mb-1.5">管理员账号</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="请输入管理员账号"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background text-[14px] placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 transition-all"
              />
            </div>
            <div>
              <label className="block text-[13px] text-muted-foreground mb-1.5">密码</label>
              <div className="relative">
                <input
                  type={showPw ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="请输入密码"
                  className="w-full px-4 py-2.5 pr-11 rounded-xl border border-border bg-background text-[14px] placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 transition-all"
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-red-500 to-orange-600 text-white text-[14px] hover:shadow-lg hover:shadow-red-500/25 transition-all duration-200 disabled:opacity-60"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <><LogIn className="w-4 h-4" /> 管理员登录</>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate("/login")}
              className="text-[13px] text-muted-foreground hover:text-foreground hover:underline"
            >
              返回用户登录
            </button>
          </div>
        </div>

        {/* Security notice */}
        <div className="mt-4 text-center text-[12px] text-muted-foreground/60">
          <p>⚠️ 仅限管理员访问</p>
        </div>
      </div>
    </div>
  );
}
