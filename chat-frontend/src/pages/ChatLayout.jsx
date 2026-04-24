import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  getAssistants,
  createAssistant,
  deleteAssistant,
} from "../api/assistants";
import {
  getConversations,
  createConversation,
  deleteConversation,
  getMessages,
  getActiveModels,
  getKBs,
} from "../api/conversations";

export default function ChatLayout() {
  const navigate = useNavigate();
  const [assistants, setAssistants] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [models, setModels] = useState([]);
  const [kbs, setKbs] = useState([]);
  const [selectedAssistant, setSelectedAssistant] = useState(null);
  const [selectedConv, setSelectedConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [showAssistantForm, setShowAssistantForm] = useState(false);
  const [selectedKB, setSelectedKB] = useState("");
  const [assistantForm, setAssistantForm] = useState({
    name: "",
    llm_model_id: "",
    embedding_model_id: "",
    system_prompt: "你是一个有帮助的AI助手",
    temperature: 0.7,
    max_tokens: 2048,
    context_length: 4000,
    top_n: 3,
  });
  const messagesEndRef = useRef(null);

  useEffect(() => {
    Promise.all([
      getAssistants().then(setAssistants),
      getActiveModels().then(setModels),
      getKBs().then(setKbs),
    ]);
  }, []);

  useEffect(() => {
    if (selectedAssistant) {
      getConversations().then((convs) =>
        setConversations(
          convs.filter((c) => c.assistant_id === selectedAssistant.id),
        ),
      );
    }
  }, [selectedAssistant]);

  useEffect(() => {
    if (selectedConv) {
      getMessages(selectedConv.id).then(setMessages);
    }
  }, [selectedConv]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleCreateAssistant = async (e) => {
    e.preventDefault();
    try {
      const created = await createAssistant({
        ...assistantForm,
        temperature: Number(assistantForm.temperature),
        max_tokens: Number(assistantForm.max_tokens),
        context_length: Number(assistantForm.context_length),
        top_n: Number(assistantForm.top_n),
      });
      setAssistants([...assistants, created]);
      setShowAssistantForm(false);
    } catch (err) {
      alert(err.detail || "创建失败");
    }
  };

  const handleCreateConversation = async () => {
    if (!selectedAssistant) return;
    const title = `对话 ${conversations.length + 1}`;
    const conv = await createConversation({
      assistant_id: selectedAssistant.id,
      title,
    });
    setConversations([...conversations, conv]);
    setSelectedConv(conv);
    setMessages([]);
  };

  const handleSend = async () => {
    if (!input.trim() || !selectedConv || streaming) return;
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setStreaming(true);

    const aiMsg = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, aiMsg]);

    try {
      const token = localStorage.getItem("token");
      const body = JSON.stringify({
        conversation_id: selectedConv.id,
        content: userMsg.content,
        knowledge_base_id: selectedKB || null,
      });

      const response = await fetch("/api/v1/conversations/chat?stream=true", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body,
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter((l) => l.startsWith("data: "));
        for (const line of lines) {
          const data = line.slice(6);
          if (data === "[DONE]") break;
          fullContent += data;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: "assistant",
              content: fullContent,
            };
            return updated;
          });
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "出错了，请重试",
        };
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div className="h-screen flex bg-gray-900 text-white">
      {/* 左侧：助手列表 */}
      <div className="w-64 bg-gray-800 flex flex-col border-r border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <h1 className="font-bold text-lg">BudAI</h1>
        </div>

        <div className="p-3 border-b border-gray-700">
          <button
            onClick={() => setShowAssistantForm(!showAssistantForm)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm py-2 rounded-lg"
          >
            + 新建助手
          </button>
        </div>

        {showAssistantForm && (
          <div className="p-3 border-b border-gray-700 bg-gray-750">
            <form onSubmit={handleCreateAssistant} className="space-y-2">
              <input
                placeholder="助手名称"
                value={assistantForm.name}
                onChange={(e) =>
                  setAssistantForm({ ...assistantForm, name: e.target.value })
                }
                required
                className="w-full bg-gray-700 text-white text-sm px-3 py-1.5 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              />
              <select
                value={assistantForm.llm_model_id}
                onChange={(e) =>
                  setAssistantForm({
                    ...assistantForm,
                    llm_model_id: e.target.value,
                  })
                }
                required
                className="w-full bg-gray-700 text-white text-sm px-3 py-1.5 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              >
                <option value="">选择对话模型</option>
                {models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
              <select
                value={assistantForm.embedding_model_id}
                onChange={(e) =>
                  setAssistantForm({
                    ...assistantForm,
                    embedding_model_id: e.target.value,
                  })
                }
                className="w-full bg-gray-700 text-white text-sm px-3 py-1.5 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              >
                <option value="">选择Embedding模型（可选）</option>
                {models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
              <textarea
                placeholder="系统提示词"
                value={assistantForm.system_prompt}
                onChange={(e) =>
                  setAssistantForm({
                    ...assistantForm,
                    system_prompt: e.target.value,
                  })
                }
                rows={2}
                className="w-full bg-gray-700 text-white text-sm px-3 py-1.5 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              />
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs py-1.5 rounded"
                >
                  创建
                </button>
                <button
                  type="button"
                  onClick={() => setShowAssistantForm(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-500 text-white text-xs py-1.5 rounded"
                >
                  取消
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="flex-1 overflow-y-auto">
          {assistants.map((asst) => (
            <div key={asst.id}>
              <button
                onClick={() => {
                  setSelectedAssistant(asst);
                  setSelectedConv(null);
                  setMessages([]);
                }}
                className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-700 transition-colors ${
                  selectedAssistant?.id === asst.id
                    ? "bg-gray-700 border-l-2 border-blue-500"
                    : ""
                }`}
              >
                <div className="font-medium truncate">🤖 {asst.name}</div>
              </button>

              {selectedAssistant?.id === asst.id && (
                <div className="pl-4 pb-2">
                  <button
                    onClick={handleCreateConversation}
                    className="w-full text-left px-3 py-1.5 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                  >
                    + 新建对话
                  </button>
                  {conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => setSelectedConv(conv)}
                      className={`w-full text-left px-3 py-1.5 text-xs truncate rounded transition-colors ${
                        selectedConv?.id === conv.id
                          ? "bg-gray-600 text-white"
                          : "text-gray-400 hover:text-white hover:bg-gray-700"
                      }`}
                    >
                      💬 {conv.title}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="p-3 border-t border-gray-700">
          <button
            onClick={handleLogout}
            className="w-full text-gray-400 hover:text-white text-xs py-2 text-left"
          >
            退出登录
          </button>
        </div>
      </div>

      {/* 右侧：聊天窗口 */}
      <div className="flex-1 flex flex-col">
        {selectedConv ? (
          <>
            {/* 顶部工具栏 */}
            <div className="bg-gray-800 px-6 py-3 border-b border-gray-700 flex items-center justify-between">
              <h2 className="font-medium">{selectedConv.title}</h2>
              <div className="flex items-center gap-3">
                <select
                  value={selectedKB}
                  onChange={(e) => setSelectedKB(e.target.value)}
                  className="bg-gray-700 text-white text-sm px-3 py-1.5 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
                >
                  <option value="">不使用知识库</option>
                  {kbs.map((kb) => (
                    <option key={kb.id} value={kb.id}>
                      {kb.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-20">
                  <p className="text-4xl mb-3">🤖</p>
                  <p>开始和 {selectedAssistant?.name} 对话吧</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-2xl px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-br-sm"
                        : "bg-gray-700 text-gray-100 rounded-bl-sm"
                    }`}
                  >
                    {msg.content ||
                      (streaming && i === messages.length - 1 ? "▌" : "")}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* 输入框 */}
            <div className="bg-gray-800 px-6 py-4 border-t border-gray-700">
              <div className="flex gap-3">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="输入消息，Enter 发送，Shift+Enter 换行"
                  rows={2}
                  disabled={streaming}
                  className="flex-1 bg-gray-700 text-white text-sm px-4 py-3 rounded-xl border border-gray-600 focus:outline-none focus:border-blue-500 resize-none disabled:opacity-50"
                />
                <button
                  onClick={handleSend}
                  disabled={streaming || !input.trim()}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-5 rounded-xl disabled:opacity-50 transition-colors"
                >
                  {streaming ? "⏳" : "发送"}
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <p className="text-5xl mb-4">💬</p>
              <p className="text-lg">
                {selectedAssistant
                  ? "选择或新建一个对话"
                  : "选择一个 AI 助手开始"}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
