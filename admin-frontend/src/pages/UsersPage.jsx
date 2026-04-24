import { useState, useEffect } from "react";
import { getUsers, updateUser, deleteUser } from "../api/users";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (user) => {
    try {
      const updated = await updateUser(user.id, { is_active: !user.is_active });
      setUsers(users.map((u) => (u.id === user.id ? updated : u)));
    } catch {
      alert("操作失败");
    }
  };

  const handleDelete = async (user) => {
    if (!confirm(`确认删除用户 ${user.username}？`)) return;
    try {
      await deleteUser(user.id);
      setUsers(users.filter((u) => u.id !== user.id));
    } catch {
      alert("删除失败");
    }
  };

  const roleColors = {
    admin: "bg-red-100 text-red-600",
    vip: "bg-yellow-100 text-yellow-600",
    user: "bg-gray-100 text-gray-600",
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">用户管理</h2>

      {loading ? (
        <p className="text-gray-400">加载中...</p>
      ) : (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500">
              <tr>
                <th className="px-6 py-3 text-left">用户名</th>
                <th className="px-6 py-3 text-left">邮箱</th>
                <th className="px-6 py-3 text-left">角色</th>
                <th className="px-6 py-3 text-left">状态</th>
                <th className="px-6 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-800">
                    {user.username}
                  </td>
                  <td className="px-6 py-4 text-gray-500">{user.email}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${roleColors[user.role]}`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        user.is_active
                          ? "bg-green-100 text-green-600"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {user.is_active ? "正常" : "已禁用"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleToggleActive(user)}
                        className="text-blue-500 hover:text-blue-700 text-xs"
                      >
                        {user.is_active ? "禁用" : "启用"}
                      </button>
                      <button
                        onClick={() => handleDelete(user)}
                        className="text-red-400 hover:text-red-600 text-xs"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
