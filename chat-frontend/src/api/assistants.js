import request from "./index";
export const getAssistants = () => request.get("/assistants");
export const createAssistant = (data) => request.post("/assistants", data);
export const updateAssistant = (id, data) =>
  request.patch(`/assistants/${id}`, data);
export const deleteAssistant = (id) => request.delete(`/assistants/${id}`);
