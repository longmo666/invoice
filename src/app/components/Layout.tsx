import { Outlet, NavLink, useLocation, useNavigate } from "react-router";
import { useState, useEffect, useMemo, useRef } from "react";
import {
  FileText,
  TrainFront,
  FolderSync,
  ScanLine,
  Sun,
  Moon,
  Upload,
  ClipboardCheck,
  List,
  ChevronRight,
  ChevronDown,
  Zap,
  LogOut,
  CreditCard,
  Lock,
  Menu,
  X,
} from "lucide-react";
import { useAuth } from "./AuthContext";
import ChangePasswordDialog from "./ChangePasswordDialog";
import { useIsMobile } from "../../lib/hooks/useMediaQuery";

/**
 * 一级菜单"发票识别"下的二级子项
 */
const recognitionChildren = [
  {
    id: "invoice",
    label: "普通发票",
    desc: "增值税电子普通发票",
    icon: FileText,
    gradient: "from-blue-500 to-indigo-600",
    lightBg: "bg-blue-50",
    darkBg: "dark:bg-blue-500/10",
  },
  {
    id: "train",
    label: "高铁票",
    desc: "电子客票识别",
    icon: TrainFront,
    gradient: "from-emerald-500 to-teal-600",
    lightBg: "bg-emerald-50",
    darkBg: "dark:bg-emerald-500/10",
  },
];

/** 一级菜单"发票识别"的视觉配置 */
const recognitionParent = {
  id: "recognition",
  label: "发票识别",
  desc: "发票与票据智能识别",
  icon: ScanLine,
  gradient: "from-blue-500 to-indigo-600",
  lightBg: "bg-blue-50",
  darkBg: "dark:bg-blue-500/10",
};

/** 独立一级菜单（不属于发票识别） */
const standaloneMenuItems = [
  {
    id: "cleaning",
    label: "文件清洗",
    desc: "批量文件分类整理",
    icon: FolderSync,
    gradient: "from-amber-500 to-orange-600",
    lightBg: "bg-amber-50",
    darkBg: "dark:bg-amber-500/10",
  },
];

/**
 * 识别模块子 Tab 配置
 * 按 activeMenu 动态切换，避免高铁票下显示"发票列表"
 */
const subTabsMap: Record<string, { key: string; label: string; icon: typeof Upload }[]> = {
  invoice: [
    { key: "upload", label: "上传识别", icon: Upload },
    { key: "review", label: "待复核", icon: ClipboardCheck },
    { key: "list", label: "发票列表", icon: List },
  ],
  train: [
    { key: "upload", label: "上传识别", icon: Upload },
    { key: "review", label: "待复核", icon: ClipboardCheck },
    { key: "list", label: "高铁票列表", icon: List },
  ],
};

export default function Layout() {
  const isMobile = useIsMobile();
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved === 'dark';
  });
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [recExpanded, setRecExpanded] = useState(true);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, loading, logout } = useAuth();

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login");
    }
  }, [user, loading, navigate]);

  /**
   * 从 URL 推导当前激活的菜单
   * /recognition/train/* → "train"
   * /recognition/invoice/* → "invoice"
   * /cleaning → "cleaning"
   */
  const activeMenu = useMemo(() => {
    if (location.pathname.startsWith("/recognition/train")) return "train";
    if (location.pathname.startsWith("/cleaning")) return "cleaning";
    return "invoice";
  }, [location.pathname]);

  /**
   * 从 URL 推导当前激活的子 Tab
   * /recognition/invoice/review → "review"
   */
  const activeTab = useMemo(() => {
    const parts = location.pathname.split("/");
    // /recognition/invoice/upload → parts = ["", "recognition", "invoice", "upload"]
    return parts[3] || "upload";
  }, [location.pathname]);

  // 进入识别路由时自动展开一级菜单
  useEffect(() => {
    if (activeMenu === "invoice" || activeMenu === "train") setRecExpanded(true);
  }, [activeMenu]);

  const isCleaning = activeMenu === "cleaning";
  const currentMenu = recognitionChildren.find((m) => m.id === activeMenu) || standaloneMenuItems.find((m) => m.id === activeMenu) || recognitionParent;

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

  const handleLogout = () => {
    setUserMenuOpen(false);
    logout();
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">加载中...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  const handleMenuClick = (id: string) => {
    setDrawerOpen(false);
    if (id === "cleaning") {
      navigate("/cleaning");
    } else {
      navigate(`/recognition/${id}/upload`);
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* ===== Mobile Drawer Overlay ===== */}
      {isMobile && drawerOpen && (
        <div className="fixed inset-0 z-40 bg-black/50" onClick={() => setDrawerOpen(false)} />
      )}

      {/* ===== Sidebar ===== */}
      <aside className={`
        ${isMobile
          ? `fixed inset-y-0 left-0 z-50 w-[280px] transform transition-transform duration-300 ${drawerOpen ? "translate-x-0" : "-translate-x-full"}`
          : "w-[260px] shrink-0"
        }
        border-r border-border bg-sidebar flex flex-col
      `}>
        <div className="px-5 py-5 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-indigo-600 flex items-center justify-center shadow-lg shadow-primary/25">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-[17px] tracking-tight">智能票据平台</h1>
              <p className="text-[11px] text-muted-foreground mt-0.5">Smart Invoice Platform</p>
            </div>
          </div>
          {isMobile && (
            <button onClick={() => setDrawerOpen(false)} className="p-1.5 rounded-lg hover:bg-accent">
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          <p className="px-3 pb-2 text-[11px] text-muted-foreground tracking-wider uppercase">
            业务模块
          </p>

          {/* ===== 一级菜单：发票识别（可展开） ===== */}
          {(() => {
            const isRecActive = activeMenu === "invoice" || activeMenu === "train";
            return (
              <div>
                <button
                  onClick={() => setRecExpanded((v) => !v)}
                  className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 ${
                    isRecActive
                      ? "bg-gradient-to-r from-primary/10 to-primary/5 shadow-sm ring-1 ring-primary/10"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-all ${
                    isRecActive ? `bg-gradient-to-br ${recognitionParent.gradient} shadow-md` : "bg-muted"
                  }`}>
                    <recognitionParent.icon className={`w-[18px] h-[18px] ${isRecActive ? "text-white" : "text-muted-foreground"}`} />
                  </div>
                  <div className="flex-1 text-left min-w-0">
                    <p className={`text-[14px] ${isRecActive ? "text-foreground" : ""}`}>{recognitionParent.label}</p>
                    <p className={`text-[11px] mt-0.5 truncate ${isRecActive ? "text-primary/60" : "text-muted-foreground/50"}`}>{recognitionParent.desc}</p>
                  </div>
                  <ChevronDown className={`w-4 h-4 shrink-0 transition-transform duration-200 ${recExpanded ? "rotate-180" : ""} ${isRecActive ? "text-primary/40" : "text-muted-foreground/40"}`} />
                </button>

                {/* 二级子项 */}
                {recExpanded && (
                  <div className="ml-5 mt-1 space-y-0.5 border-l-2 border-border pl-3">
                    {recognitionChildren.map((child) => {
                      const isChildActive = activeMenu === child.id;
                      return (
                        <button
                          key={child.id}
                          onClick={() => handleMenuClick(child.id)}
                          className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                            isChildActive
                              ? "bg-primary/8 text-foreground"
                              : "text-muted-foreground hover:bg-accent hover:text-foreground"
                          }`}
                        >
                          <div className={`w-7 h-7 rounded-md flex items-center justify-center shrink-0 transition-all ${
                            isChildActive ? `bg-gradient-to-br ${child.gradient} shadow-sm` : "bg-muted"
                          }`}>
                            <child.icon className={`w-[15px] h-[15px] ${isChildActive ? "text-white" : "text-muted-foreground"}`} />
                          </div>
                          <div className="flex-1 text-left min-w-0">
                            <p className={`text-[13px] ${isChildActive ? "text-foreground" : ""}`}>{child.label}</p>
                          </div>
                          {isChildActive && <ChevronRight className="w-3.5 h-3.5 text-primary/40 shrink-0" />}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })()}

          {/* ===== 独立一级菜单 ===== */}
          {standaloneMenuItems.map((item) => {
            const isActive = activeMenu === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleMenuClick(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-primary/10 to-primary/5 shadow-sm ring-1 ring-primary/10"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-all ${
                  isActive ? `bg-gradient-to-br ${item.gradient} shadow-md` : "bg-muted"
                }`}>
                  <item.icon className={`w-[18px] h-[18px] ${isActive ? "text-white" : "text-muted-foreground"}`} />
                </div>
                <div className="flex-1 text-left min-w-0">
                  <p className={`text-[14px] ${isActive ? "text-foreground" : ""}`}>{item.label}</p>
                  <p className={`text-[11px] mt-0.5 truncate ${isActive ? "text-primary/60" : "text-muted-foreground/50"}`}>{item.desc}</p>
                </div>
                {isActive && <ChevronRight className="w-4 h-4 text-primary/40 shrink-0" />}
              </button>
            );
          })}
        </nav>

        <div className="px-3 pb-4 space-y-1">
          <button
            onClick={() => setDark(!dark)}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-xl bg-muted/60 hover:bg-muted transition-all duration-200"
          >
            <div className="w-9 h-9 rounded-lg bg-card border border-border flex items-center justify-center">
              {dark ? (
                <Sun className="w-[18px] h-[18px] text-amber-500" />
              ) : (
                <Moon className="w-[18px] h-[18px] text-indigo-500" />
              )}
            </div>
            <div className="flex-1 text-left">
              <p className="text-[13px]">{dark ? "浅色模式" : "深色模式"}</p>
              <p className="text-[11px] text-muted-foreground mt-0.5">切换界面主题</p>
            </div>
          </button>
          <button onClick={() => { setShowChangePassword(true); setDrawerOpen(false); }}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-accent text-muted-foreground hover:text-foreground transition-all duration-200">
            <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center">
              <Lock className="w-[18px] h-[18px]" />
            </div>
            <span className="text-[13px]">修改密码</span>
          </button>
          <button onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-all duration-200">
            <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center">
              <LogOut className="w-[18px] h-[18px]" />
            </div>
            <span className="text-[13px]">退出登录</span>
          </button>
        </div>
      </aside>

      {/* ===== Main Content ===== */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="shrink-0 bg-card border-b border-border">
          <div className="flex items-center px-4 md:px-6 h-[56px] md:h-[60px]">
            {isMobile && (
              <button onClick={() => setDrawerOpen(true)} className="p-2 -ml-1 mr-2 rounded-lg hover:bg-accent">
                <Menu className="w-5 h-5" />
              </button>
            )}
            <div className={`w-9 h-9 rounded-xl ${currentMenu.lightBg} ${currentMenu.darkBg} flex items-center justify-center mr-3`}>
              <currentMenu.icon className="w-5 h-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-[16px] md:text-[18px] tracking-tight truncate">{currentMenu.label}<span className="text-muted-foreground ml-1">工作区</span></h2>
            </div>

            {/* User menu */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 md:gap-2.5 px-2 md:px-3 py-1.5 rounded-xl hover:bg-accent transition-all"
              >
                <div className="hidden md:flex items-center gap-1.5 text-[12px] text-muted-foreground">
                  <CreditCard className="w-3.5 h-3.5" />
                  <span>剩余 <span className="text-primary tabular-nums">{user.remainingQuota}</span> 次</span>
                </div>
                <div className="hidden md:block w-px h-4 bg-border" />
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-indigo-600 flex items-center justify-center text-white text-[11px]">
                  {user.username[0].toUpperCase()}
                </div>
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-card rounded-xl border border-border shadow-xl shadow-black/10 py-2 z-50">
                  <div className="px-4 py-2.5 border-b border-border">
                    <p className="text-[14px]">{user.username}</p>
                    <p className="text-[12px] text-muted-foreground mt-0.5">剩余可用次数：{user.remainingQuota}</p>
                  </div>
                  <button
                    onClick={() => { setUserMenuOpen(false); setShowChangePassword(true); }}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-[13px] text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
                  >
                    <Lock className="w-4 h-4" /> 修改密码
                  </button>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-[13px] text-muted-foreground hover:text-destructive hover:bg-destructive/5 transition-all"
                  >
                    <LogOut className="w-4 h-4" /> 退出登录
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Tab Row - only for invoice/train */}
          {!isCleaning && (
            <div className="px-4 md:px-6 flex items-center gap-1 -mb-px overflow-x-auto">
              {(subTabsMap[activeMenu] || subTabsMap.invoice).map((tab) => {
                const isActive = activeTab === tab.key;
                const to = `/recognition/${activeMenu}/${tab.key}`;
                return (
                  <NavLink
                    key={tab.key}
                    to={to}
                    className={`flex items-center gap-2 px-4 md:px-5 py-2.5 text-[13px] md:text-[14px] border-b-2 transition-all duration-200 whitespace-nowrap ${
                      isActive
                        ? "border-primary text-primary"
                        : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </NavLink>
                );
              })}
            </div>
          )}
        </header>

        <main className="flex-1 overflow-auto bg-background">
          <Outlet key={location.pathname} context={{ activeMenu, isMobile }} />
        </main>
      </div>

      <ChangePasswordDialog
        isOpen={showChangePassword}
        onClose={() => setShowChangePassword(false)}
        onSuccess={() => {
          setShowChangePassword(false);
        }}
      />
    </div>
  );
}
