import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

const navItems = [
  { path: "/users", label: "用户管理", icon: "👥" },
  { path: "/models", label: "模型管理", icon: "🤖" },
  { path: "/knowledge-bases", label: "知识库管理", icon: "📚" },
  { path: "/files", label: "文件管理", icon: "📁" },
];

export default function DashboardLayout() {
  const navigate = useNavigate();
  const { clearAuth } = useAuth();

  const handleLogout = () => {
    clearAuth();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* 侧边栏 */}
      <aside className="w-56 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-xl font-bold">BudAI 管理后台</h1>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:bg-gray-800 hover:text-white"
                }`
              }
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={handleLogout}
            className="w-full text-gray-400 hover:text-white text-sm py-2 text-left px-3 hover:bg-gray-800 rounded-lg transition-colors"
          >
            退出登录
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 p-8 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
