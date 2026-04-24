import request from "./index";

export const getUsers = () => request.get("/users");
export const getMe = () => request.get("/users/me");
export const updateUser = (id, data) => request.patch(`/users/${id}`, data);
export const deleteUser = (id) => request.delete(`/users/${id}`);
