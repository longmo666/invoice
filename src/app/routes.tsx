import { createBrowserRouter, Navigate, Outlet } from "react-router";
import Layout from "./components/Layout";
import UploadRecognition from "./components/UploadRecognition";
import PendingReview from "./components/PendingReview";
import RecordList from "./components/RecordList";
import FileCleaning from "./components/FileCleaning";
import UserLoginPage from "./components/UserLoginPage";
import AdminLoginPage from "./components/AdminLoginPage";
import RegisterPage from "./components/RegisterPage";
import AdminLayout from "./components/AdminLayout";
import AdminDashboard from "./components/AdminDashboard";
import AdminUsers from "./components/AdminUsers";
import AdminRecognition from "./components/AdminRecognition";
import AdminCleaning from "./components/AdminCleaning";
import AdminAIConfig from "./components/AdminAIConfig";
import { AuthProvider } from "./components/AuthContext";

function RootWrapper() {
  return (
    <AuthProvider>
      <Outlet />
    </AuthProvider>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    Component: RootWrapper,
    children: [
      { path: "login", Component: UserLoginPage },
      { path: "admin/login", Component: AdminLoginPage },
      { path: "register", Component: RegisterPage },
      {
        path: "admin",
        Component: AdminLayout,
        children: [
          { index: true, Component: AdminDashboard },
          { path: "users", Component: AdminUsers },
          { path: "recognition/invoice", Component: AdminRecognition },
          { path: "recognition/train", Component: AdminRecognition },
          { path: "cleaning", Component: AdminCleaning },
          { path: "ai-config", Component: AdminAIConfig },
          /* 旧管理端路由 1:1 重定向 */
          { path: "invoices", element: <Navigate to="/admin/recognition/invoice" replace /> },
          { path: "trains", element: <Navigate to="/admin/recognition/train" replace /> },
        ],
      },
      {
        path: "",
        Component: Layout,
        children: [
          { index: true, element: <Navigate to="/login" replace /> },

          /* ===== 新路由：/recognition/{type}/{tab} ===== */
          { path: "recognition/invoice/upload", Component: UploadRecognition },
          { path: "recognition/invoice/review", Component: PendingReview },
          { path: "recognition/invoice/list", Component: RecordList },
          { path: "recognition/train/upload", Component: UploadRecognition },
          { path: "recognition/train/review", Component: PendingReview },
          { path: "recognition/train/list", Component: RecordList },

          /* ===== 旧路由 1:1 重定向 ===== */
          { path: "invoice/upload", element: <Navigate to="/recognition/invoice/upload" replace /> },
          { path: "invoice/review", element: <Navigate to="/recognition/invoice/review" replace /> },
          { path: "invoice/list", element: <Navigate to="/recognition/invoice/list" replace /> },
          { path: "train/upload", element: <Navigate to="/recognition/train/upload" replace /> },
          { path: "train/review", element: <Navigate to="/recognition/train/review" replace /> },
          { path: "train/list", element: <Navigate to="/recognition/train/list" replace /> },

          /* ===== 文件清洗（独立模块，路由不变） ===== */
          { path: "cleaning", Component: FileCleaning },
        ],
      },
    ],
  },
]);
