import request from "./index";

export const getFiles = () => request.get("/files");

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/files", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const parseFiles = (data) => request.post("/files/parse", data);
export const downloadFile = (id) => `/api/v1/files/${id}/download`;
export const deleteFile = (id) => request.delete(`/files/${id}`);
