import { Outlet, useNavigate, useLocation } from "react-router";
import { useAuth } from "./AuthContext";
import { useState, useEffect, useRef } from "react";
import {
  Shield, Sun, Moon, LogOut, BarChart3,
  Users, FileText, FolderSync, Lock, Settings,
} from "lucide-react";
import ChangePasswordDialog from "./ChangePasswordDialog";

interface NavGroup {
  label: string;
  items: { path: string; label: string; icon: typeof BarChart3; exact?: boolean; matchPrefix?: string }[];
}

const navGroups: NavGroup[] = [
  {
    label: "总览",
    items: [
      { path: "/admin", label: "数据概览", icon: BarChart3, exact: true },
    ],
  },
  {
    label: "用户与识别",
    items: [
      { path: "/admin/users", label: "用户管理", icon: Users },
      { path: "/admin/recognition/invoice", label: "识别记录", icon: FileText, matchPrefix: "/admin/recognition" },
    ],
  },
  {
    label: "文件处理",
    items: [
      { path: "/admin/cleaning", label: "文件清洗", icon: FolderSync },
    ],
  },
  {
    label: "AI 基础设施",
    items: [
      { path: "/admin/ai-config", label: "AI 配置", icon: Settings },
    ],
  },
];

const allNavItems = navGroups.flatMap(g => g.items);

export default function AdminLayout() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved === 'dark';
  });
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!loading && (!user || user.role !== "admin")) {
      navigate("/admin/login");
    }
  }, [user, loading, navigate]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, [dark]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) setUserMenuOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 border-4 border-rose-500/30 border-t-rose-500 rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">加载中...</p>
        </div>
      </div>
    );
  }

  if (!user || user.role !== "admin") return null;

  const isItemActive = (item: typeof allNavItems[0]) => {
    if (item.matchPrefix) return location.pathname.startsWith(item.matchPrefix);
    if (item.exact) return location.pathname === item.path;
    return location.pathname.startsWith(item.path) && location.pathname !== "/admin";
  };

  const currentNav = [...allNavItems].reverse().find(isItemActive) || allNavItems[0];

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <aside className="w-[240px] shrink-0 border-r border-border bg-sidebar flex flex-col">
        <div className="px-5 py-5 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-pink-600 flex items-center justify-center shadow-lg shadow-rose-500/25">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-[16px] tracking-tight">管理后台</h1>
              <p className="text-[11px] text-muted-foreground mt-0.5">Admin Console</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-4 overflow-auto">
          {navGroups.map(group => (
            <div key={group.label}>
              <p className="px-3 pb-2 text-[11px] text-muted-foreground tracking-wider uppercase">{group.label}</p>
              <div className="space-y-1">
                {group.items.map(item => {
                  const active = isItemActive(item);
                  return (
                    <button
                      key={item.path}
                      onClick={() => navigate(item.path)}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 ${
                        active
                          ? "bg-gradient-to-r from-primary/10 to-primary/5 shadow-sm ring-1 ring-primary/10"
                          : "hover:bg-accent text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        active ? "bg-gradient-to-br from-primary to-indigo-600" : "bg-muted"
                      }`}>
                        <item.icon className={`w-4 h-4 ${active ? "text-white" : "text-muted-foreground"}`} />
                      </div>
                      <span className={`text-[13px] ${active ? "text-foreground" : ""}`}>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="px-3 pb-3 space-y-1">
          <button onClick={() => setDark(!dark)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-muted/60 hover:bg-muted transition-all">
            <div className="w-8 h-8 rounded-lg bg-card border border-border flex items-center justify-center">
              {dark ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4 text-indigo-500" />}
            </div>
            <span className="text-[13px]">{dark ? "浅色模式" : "深色模式"}</span>
          </button>
          <button onClick={() => setShowChangePassword(true)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-accent text-muted-foreground hover:text-foreground transition-all">
            <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
              <Lock className="w-4 h-4" />
            </div>
            <span className="text-[13px]">修改密码</span>
          </button>
          <button onClick={() => { logout(); navigate("/login"); }}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-all">
            <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
              <LogOut className="w-4 h-4" />
            </div>
            <span className="text-[13px]">退出登录</span>
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="shrink-0 bg-card border-b border-border h-[60px] flex items-center px-6">
          <div className="flex-1">
            <h2 className="text-[18px]">{currentNav.label}</h2>
          </div>
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 text-[13px] text-muted-foreground px-3 py-1.5 rounded-xl hover:bg-accent transition-all"
            >
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-rose-500 to-pink-600 flex items-center justify-center text-white text-[11px]">
                {user.username[0].toUpperCase()}
              </div>
              {user.username}
            </button>
            {userMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-52 bg-card rounded-xl border border-border shadow-xl shadow-black/10 py-2 z-50">
                <div className="px-4 py-2.5 border-b border-border">
                  <p className="text-[14px]">{user.username}</p>
                  <p className="text-[12px] text-muted-foreground mt-0.5">管理员</p>
                </div>
                <button
                  onClick={() => { setUserMenuOpen(false); setShowChangePassword(true); }}
                  className="w-full flex items-center gap-2.5 px-4 py-2.5 text-[13px] text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
                >
                  <Lock className="w-4 h-4" /> 修改密码
                </button>
                <button
                  onClick={() => { setUserMenuOpen(false); logout(); navigate("/login"); }}
                  className="w-full flex items-center gap-2.5 px-4 py-2.5 text-[13px] text-muted-foreground hover:text-destructive hover:bg-destructive/5 transition-all"
                >
                  <LogOut className="w-4 h-4" /> 退出登录
                </button>
              </div>
            )}
          </div>
        </header>
        <main className="flex-1 overflow-auto bg-background">
          <Outlet />
        </main>
      </div>

      <ChangePasswordDialog
        isOpen={showChangePassword}
        onClose={() => setShowChangePassword(false)}
        onSuccess={() => setShowChangePassword(false)}
      />
    </div>
  );
}
