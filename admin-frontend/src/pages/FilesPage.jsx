import { useState, useEffect } from "react";
import {
  getFiles,
  uploadFile,
  parseFiles,
  deleteFile,
  downloadFile,
} from "../api/files";
import { getModels } from "../api/llmModels";
import { getKBs } from "../api/knowledgeBases";

export default function FilesPage() {
  const [files, setFiles] = useState([]);
  const [models, setModels] = useState([]);
  const [kbs, setKbs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showParseForm, setShowParseForm] = useState(false);
  const [parseForm, setParseForm] = useState({
    file_ids: [],
    knowledge_base_id: "",
    embedding_model_id: "",
  });

  useEffect(() => {
    Promise.all([loadFiles(), loadModels(), loadKBs()]);
  }, []);

  const loadFiles = async () => {
    setLoading(true);
    try {
      setFiles(await getFiles());
    } finally {
      setLoading(false);
    }
  };

  const loadModels = async () => setModels(await getModels());
  const loadKBs = async () => setKbs(await getKBs());

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const created = await uploadFile(file);
      setFiles([...files, created]);
    } catch (err) {
      alert(err.detail || "上传失败");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (file) => {
    if (!confirm(`确认删除 ${file.filename}？`)) return;
    try {
      await deleteFile(file.id);
      setFiles(files.filter((f) => f.id !== file.id));
    } catch {
      alert("删除失败");
    }
  };

  const toggleSelectFile = (fileId) => {
    const ids = parseForm.file_ids;
    setParseForm({
      ...parseForm,
      file_ids: ids.includes(fileId)
        ? ids.filter((id) => id !== fileId)
        : [...ids, fileId],
    });
  };

  const handleParse = async (e) => {
    e.preventDefault();
    if (parseForm.file_ids.length === 0) {
      alert("请至少选择一个文件");
      return;
    }
    try {
      const result = await parseFiles(parseForm);
      alert(
        result.results
          .map(
            (r) =>
              `${r.filename}: ${r.status === "done" ? `成功，${r.chunk_count}个块` : `失败 - ${r.error}`}`,
          )
          .join("\n"),
      );
      setShowParseForm(false);
      setParseForm({
        file_ids: [],
        knowledge_base_id: "",
        embedding_model_id: "",
      });
      loadFiles();
    } catch {
      alert("解析失败");
    }
  };

  const statusColors = {
    pending: "bg-gray-100 text-gray-500",
    parsing: "bg-yellow-100 text-yellow-600",
    done: "bg-green-100 text-green-600",
    failed: "bg-red-100 text-red-600",
  };

  const embeddingModels = models.filter((m) => m.is_active);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">文件管理</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setShowParseForm(!showParseForm)}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm"
          >
            解析文件
          </button>
          <label className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm cursor-pointer">
            {uploading ? "上传中..." : "+ 上传文件"}
            <input
              type="file"
              className="hidden"
              onChange={handleUpload}
              accept=".pdf,.txt,.md,.docx"
              disabled={uploading}
            />
          </label>
        </div>
      </div>

      {showParseForm && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h3 className="font-semibold text-gray-800 mb-4">批量解析文件</h3>
          <form onSubmit={handleParse} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-600 mb-2">
                选择要解析的文件（可多选）
              </label>
              <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
                {files.map((file) => (
                  <label
                    key={file.id}
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={parseForm.file_ids.includes(file.id)}
                      onChange={() => toggleSelectFile(file.id)}
                    />
                    <span className="text-sm text-gray-700">
                      {file.filename}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs ${statusColors[file.parse_status]}`}
                    >
                      {file.parse_status}
                    </span>
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">
                关联知识库
              </label>
              <select
                value={parseForm.knowledge_base_id}
                onChange={(e) =>
                  setParseForm({
                    ...parseForm,
                    knowledge_base_id: e.target.value,
                  })
                }
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="">请选择知识库</option>
                {kbs.map((kb) => (
                  <option key={kb.id} value={kb.id}>
                    {kb.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">
                Embedding 模型
              </label>
              <select
                value={parseForm.embedding_model_id}
                onChange={(e) =>
                  setParseForm({
                    ...parseForm,
                    embedding_model_id: e.target.value,
                  })
                }
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="">请选择模型</option>
                {embeddingModels.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm"
              >
                开始解析
              </button>
              <button
                type="button"
                onClick={() => setShowParseForm(false)}
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
                <th className="px-6 py-3 text-left">文件名</th>
                <th className="px-6 py-3 text-left">大小</th>
                <th className="px-6 py-3 text-left">类型</th>
                <th className="px-6 py-3 text-left">解析状态</th>
                <th className="px-6 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {files.map((file) => (
                <tr key={file.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-800">
                    {file.filename}
                  </td>
                  <td className="px-6 py-4 text-gray-500">
                    {(file.file_size / 1024).toFixed(1)} KB
                  </td>
                  <td className="px-6 py-4 text-gray-500">{file.file_type}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[file.parse_status]}`}
                    >
                      {file.parse_status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-3">
                      <a
                        href={downloadFile(file.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-500 hover:text-blue-700 text-xs"
                      >
                        下载
                      </a>
                      <button
                        onClick={() => handleDelete(file)}
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
