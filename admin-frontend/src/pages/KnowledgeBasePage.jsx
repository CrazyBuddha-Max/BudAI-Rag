import { useState, useEffect } from "react";
import {
  getKBs,
  createKB,
  updateKB,
  deleteKB,
  getKBFiles,
} from "../api/knowledgeBases";

export default function KnowledgeBasePage() {
  const [kbs, setKbs] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [form, setForm] = useState({ name: "", description: "" });
  const [expandedKB, setExpandedKB] = useState(null);
  const [kbFiles, setKbFiles] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadKBs();
  }, []);

  const loadKBs = async () => {
    setLoading(true);
    try {
      setKbs(await getKBs());
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setForm({ name: "", description: "" });
    setEditTarget(null);
    setShowForm(true);
  };

  const openEdit = (kb) => {
    setForm({ name: kb.name, description: kb.description || "" });
    setEditTarget(kb);
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editTarget) {
        const updated = await updateKB(editTarget.id, form);
        setKbs(kbs.map((k) => (k.id === editTarget.id ? updated : k)));
      } else {
        const created = await createKB(form);
        setKbs([...kbs, created]);
      }
      setShowForm(false);
    } catch {
      alert("操作失败");
    }
  };

  const handleDelete = async (kb) => {
    if (!confirm(`确认删除知识库 ${kb.name}？`)) return;
    try {
      await deleteKB(kb.id);
      setKbs(kbs.filter((k) => k.id !== kb.id));
    } catch {
      alert("删除失败");
    }
  };

  const handleExpand = async (kb) => {
    if (expandedKB === kb.id) {
      setExpandedKB(null);
      return;
    }
    setExpandedKB(kb.id);
    if (!kbFiles[kb.id]) {
      const files = await getKBFiles(kb.id);
      setKbFiles({ ...kbFiles, [kb.id]: files });
    }
  };

  const statusColors = {
    pending: "bg-gray-100 text-gray-500",
    parsing: "bg-yellow-100 text-yellow-600",
    done: "bg-green-100 text-green-600",
    failed: "bg-red-100 text-red-600",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">知识库管理</h2>
        <button
          onClick={openCreate}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
        >
          + 新建知识库
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow p-6 mb-6 max-w-md">
          <h3 className="font-semibold text-gray-800 mb-4">
            {editTarget ? "编辑知识库" : "新建知识库"}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">名称</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">描述</label>
              <textarea
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
              >
                {editTarget ? "保存" : "创建"}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <p className="text-gray-400">加载中...</p>
      ) : (
        <div className="space-y-3">
          {kbs.map((kb) => (
            <div key={kb.id} className="bg-white rounded-xl shadow">
              <div className="flex items-center justify-between px-6 py-4">
                <div>
                  <h3 className="font-medium text-gray-800">{kb.name}</h3>
                  {kb.description && (
                    <p className="text-sm text-gray-500 mt-1">
                      {kb.description}
                    </p>
                  )}
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => handleExpand(kb)}
                    className="text-blue-500 hover:text-blue-700 text-sm"
                  >
                    {expandedKB === kb.id ? "收起文件" : "查看文件"}
                  </button>
                  <button
                    onClick={() => openEdit(kb)}
                    className="text-blue-500 hover:text-blue-700 text-sm"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => handleDelete(kb)}
                    className="text-red-400 hover:text-red-600 text-sm"
                  >
                    删除
                  </button>
                </div>
              </div>

              {expandedKB === kb.id && (
                <div className="border-t border-gray-100 px-6 py-4">
                  {kbFiles[kb.id]?.length === 0 ? (
                    <p className="text-gray-400 text-sm">暂无文件</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead className="text-gray-500">
                        <tr>
                          <th className="text-left py-2">文件名</th>
                          <th className="text-left py-2">大小</th>
                          <th className="text-left py-2">类型</th>
                          <th className="text-left py-2">解析状态</th>
                        </tr>
                      </thead>
                      <tbody>
                        {kbFiles[kb.id]?.map((file) => (
                          <tr key={file.id} className="border-t border-gray-50">
                            <td className="py-2 text-gray-700">
                              {file.filename}
                            </td>
                            <td className="py-2 text-gray-500">
                              {(file.file_size / 1024).toFixed(1)} KB
                            </td>
                            <td className="py-2 text-gray-500">
                              {file.file_type}
                            </td>
                            <td className="py-2">
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[file.parse_status]}`}
                              >
                                {file.parse_status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
