import request from "./index";

export const getModels = () => request.get("/llm-models");
export const createModel = (data) => request.post("/llm-models", data);
export const updateModel = (id, data) =>
  request.patch(`/llm-models/${id}`, data);
export const deleteModel = (id) => request.delete(`/llm-models/${id}`);
