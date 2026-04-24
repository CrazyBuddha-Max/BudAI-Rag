import request from "./index";

export const getConversations = () => request.get("/conversations");
export const createConversation = (data) =>
  request.post("/conversations", data);
export const updateConversation = (id, data) =>
  request.patch(`/conversations/${id}`, data);
export const deleteConversation = (id) =>
  request.delete(`/conversations/${id}`);
export const getMessages = (id) => request.get(`/conversations/${id}/messages`);

export const getActiveModels = () => request.get("/llm-models/active");
export const getKBs = () => request.get("/knowledge-bases");
