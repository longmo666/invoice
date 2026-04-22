import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";
import { authService, type User as ApiUser } from "../../lib/services/auth";
import { userService, type PageResult } from "../../lib/services/user";
import { formatBeijingTime } from "../../lib/helpers/format";

export interface User {
  id: number;
  username: string;
  role: "user" | "admin";
  status: "active" | "disabled";
  remainingQuota: number;
  usedQuota: number;
  registeredAt: string;
  lastLoginAt: string | null;
}

interface AuthContextType {
  user: User | null;
  users: User[];
  loading: boolean;
  login: (username: string, password: string, isAdmin?: boolean) => Promise<{ success: boolean; error?: string }>;
  register: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  fetchUsers: () => Promise<void>;
  updateUser: (id: number, updates: { status: "active" | "disabled" }) => Promise<void>;
  addQuota: (id: number, amount: number) => Promise<void>;
  deleteUser: (id: number) => Promise<void>;
  deleteUsers: (ids: number[]) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

function mapApiUser(apiUser: ApiUser): User {
  return {
    id: apiUser.id,
    username: apiUser.username,
    role: apiUser.role,
    status: apiUser.status,
    remainingQuota: apiUser.remaining_quota,
    usedQuota: apiUser.used_quota,
    registeredAt: formatBeijingTime(apiUser.created_at),
    lastLoginAt: apiUser.last_login_at ? formatBeijingTime(apiUser.last_login_at) : null,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  // 初始化：检查登录状态
  useEffect(() => {
    const initAuth = async () => {
      if (authService.isAuthenticated()) {
        const response = await authService.getMe();
        if (response.success && response.data) {
          setUser(mapApiUser(response.data));
        } else {
          authService.clearToken();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = useCallback(async (username: string, password: string, isAdmin = false) => {
    try {
      const response = isAdmin
        ? await authService.adminLogin({ username, password })
        : await authService.login({ username, password });

      if (response.success && response.data) {
        setUser(mapApiUser(response.data.user));
        return { success: true };
      }
      return { success: false, error: response.error || "登录失败" };
    } catch (error) {
      return { success: false, error: "网络错误" };
    }
  }, []);

  const register = useCallback(async (username: string, password: string) => {
    try {
      const response = await authService.register({ username, password });
      if (response.success && response.data) {
        setUser(mapApiUser(response.data.user));
        return { success: true };
      }
      return { success: false, error: response.error || "注册失败" };
    } catch (error) {
      return { success: false, error: "网络错误" };
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  const fetchUsers = useCallback(async () => {
    const response = await userService.getUsers({ page: 1, page_size: 100 });
    if (response.success && response.data) {
      setUsers(response.data.items.map(mapApiUser));
    }
  }, []);

  const updateUser = useCallback(async (id: number, updates: { status: "active" | "disabled" }) => {
    const response = await userService.updateStatus(id, updates.status);
    if (response.success) {
      await fetchUsers();
    }
  }, [fetchUsers]);

  const addQuota = useCallback(async (id: number, amount: number) => {
    const response = await userService.addQuota(id, amount);
    if (response.success) {
      await fetchUsers();
    }
  }, [fetchUsers]);

  const deleteUser = useCallback(async (id: number) => {
    await userService.deleteUser(id);
    await fetchUsers();
  }, [fetchUsers]);

  const deleteUsers = useCallback(async (ids: number[]) => {
    await userService.batchDelete(ids);
    await fetchUsers();
  }, [fetchUsers]);

  return (
    <AuthContext.Provider value={{ user, users, loading, login, register, logout, fetchUsers, updateUser, addQuota, deleteUser, deleteUsers }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}