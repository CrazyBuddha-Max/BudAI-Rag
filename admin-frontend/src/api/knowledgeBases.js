import request from "./index";

export const getKBs = () => request.get("/knowledge-bases");
export const createKB = (data) => request.post("/knowledge-bases", data);
export const updateKB = (id, data) =>
  request.patch(`/knowledge-bases/${id}`, data);
export const deleteKB = (id) => request.delete(`/knowledge-bases/${id}`);
export const getKBFiles = (id) => request.get(`/knowledge-bases/${id}/files`);
