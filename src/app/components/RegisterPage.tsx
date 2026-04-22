import { useState } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "./AuthContext";
import { Zap, Eye, EyeOff, UserPlus, Shield, LogIn } from "lucide-react";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!username.trim()) { setError("请输入账号"); return; }
    if (password.length < 8) { setError("密码长度至少 8 位"); return; }
    if (password !== confirmPw) { setError("两次密码不一致"); return; }
    setLoading(true);
    const result = await register(username.trim(), password);
    setLoading(false);
    if (result.success) {
      navigate("/recognition/invoice/upload");
    } else {
      setError(result.error || "注册失败");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary to-indigo-600 flex items-center justify-center shadow-xl shadow-primary/25 mb-4">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-[24px] tracking-tight">智能票据平台</h1>
          <p className="text-[14px] text-muted-foreground mt-1">创建新账号</p>
        </div>

        <div className="bg-card rounded-2xl border border-border shadow-xl shadow-black/5 p-8">
          <h2 className="text-[18px] mb-6">注册</h2>

          {error && (
            <div className="mb-4 px-4 py-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-[13px] flex items-center gap-2">
              <Shield className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[13px] text-muted-foreground mb-1.5">账号</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="请输入账号"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background text-[14px] placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>
            <div>
              <label className="block text-[13px] text-muted-foreground mb-1.5">密码</label>
              <div className="relative">
                <input
                  type={showPw ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="至少 8 位"
                  className="w-full px-4 py-2.5 pr-11 rounded-xl border border-border bg-background text-[14px] placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-[13px] text-muted-foreground mb-1.5">确认密码</label>
              <input
                type="password"
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
                placeholder="再次输入密码"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background text-[14px] placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>
            <p className="text-[12px] text-muted-foreground">密码规则：8 位以上，注册后赠送 20 次免费识别额度</p>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-primary to-indigo-600 text-white text-[14px] hover:shadow-lg hover:shadow-primary/25 transition-all duration-200 disabled:opacity-60"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <><UserPlus className="w-4 h-4" /> 注册</>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate("/login")}
              className="text-[13px] text-primary hover:underline inline-flex items-center gap-1"
            >
              <LogIn className="w-3.5 h-3.5" /> 已有账号？去登录
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
