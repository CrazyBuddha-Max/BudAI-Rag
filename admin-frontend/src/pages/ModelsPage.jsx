import { useState, useEffect } from "react";
import {
  getModels,
  createModel,
  updateModel,
  deleteModel,
} from "../api/llmModels";

const EMPTY_FORM = {
  name: "",
  provider: "openai",
  model_name: "",
  api_key: "",
  api_base_url: "",
  max_tokens: 4096,
  embedding_type: "api",
  embedding_model_name: "",
};

export default function ModelsPage() {
  const [models, setModels] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      setModels(await getModels());
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setForm(EMPTY_FORM);
    setEditTarget(null);
    setShowForm(true);
  };

  const openEdit = (model) => {
    setForm({ ...model, api_key: "" });
    setEditTarget(model);
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...form, max_tokens: Number(form.max_tokens) };
      if (!data.api_base_url) delete data.api_base_url;
      if (!data.embedding_model_name) delete data.embedding_model_name;
      if (editTarget) {
        if (!data.api_key) delete data.api_key;
        const updated = await updateModel(editTarget.id, data);
        setModels(models.map((m) => (m.id === editTarget.id ? updated : m)));
      } else {
        const created = await createModel(data);
        setModels([...models, created]);
      }
      setShowForm(false);
    } catch (err) {
      alert(err.detail || "操作失败");
    }
  };

  const handleDelete = async (model) => {
    if (!confirm(`确认删除模型 ${model.name}？`)) return;
    try {
      await deleteModel(model.id);
      setModels(models.filter((m) => m.id !== model.id));
    } catch {
      alert("删除失败");
    }
  };

  const handleToggleActive = async (model) => {
    try {
      const updated = await updateModel(model.id, {
        is_active: !model.is_active,
      });
      setModels(models.map((m) => (m.id === model.id ? updated : m)));
    } catch {
      alert("操作失败");
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">模型管理</h2>
        <button
          onClick={openCreate}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
        >
          + 新增模型
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h3 className="font-semibold text-gray-800 mb-4">
            {editTarget ? "编辑模型" : "新增模型"}
          </h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
            {[
              { label: "模型别名", key: "name", required: true },
              { label: "模型名称", key: "model_name", required: true },
              { label: "API Key", key: "api_key", required: !editTarget },
              { label: "API Base URL", key: "api_base_url" },
              { label: "Max Tokens", key: "max_tokens", type: "number" },
              { label: "Embedding 模型名", key: "embedding_model_name" },
            ].map(({ label, key, required, type }) => (
              <div key={key}>
                <label className="block text-sm text-gray-600 mb-1">
                  {label}
                </label>
                <input
                  type={type || "text"}
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  required={required}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
            ))}
            <div>
              <label className="block text-sm text-gray-600 mb-1">
                Provider
              </label>
              <select
                value={form.provider}
                onChange={(e) => setForm({ ...form, provider: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="openai">OpenAI / 兼容格式</option>
                <option value="anthropic">Anthropic</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">
                Embedding 类型
              </label>
              <select
                value={form.embedding_type}
                onChange={(e) =>
                  setForm({ ...form, embedding_type: e.target.value })
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="api">API</option>
                <option value="local">本地模型</option>
              </select>
            </div>
            <div className="col-span-2 flex gap-3">
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
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500">
              <tr>
                <th className="px-6 py-3 text-left">名称</th>
                <th className="px-6 py-3 text-left">Provider</th>
                <th className="px-6 py-3 text-left">模型</th>
                <th className="px-6 py-3 text-left">Embedding</th>
                <th className="px-6 py-3 text-left">状态</th>
                <th className="px-6 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {models.map((model) => (
                <tr key={model.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-800">
                    {model.name}
                  </td>
                  <td className="px-6 py-4 text-gray-500">{model.provider}</td>
                  <td className="px-6 py-4 text-gray-500">
                    {model.model_name}
                  </td>
                  <td className="px-6 py-4 text-gray-500">
                    {model.embedding_type === "local" ? "本地" : "API"} /{" "}
                    {model.embedding_model_name || "-"}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        model.is_active
                          ? "bg-green-100 text-green-600"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {model.is_active ? "启用" : "禁用"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-3">
                      <button
                        onClick={() => openEdit(model)}
                        className="text-blue-500 hover:text-blue-700 text-xs"
                      >
                        编辑
                      </button>
                      <button
                        onClick={() => handleToggleActive(model)}
                        className="text-yellow-500 hover:text-yellow-700 text-xs"
                      >
                        {model.is_active ? "禁用" : "启用"}
                      </button>
                      <button
                        onClick={() => handleDelete(model)}
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
