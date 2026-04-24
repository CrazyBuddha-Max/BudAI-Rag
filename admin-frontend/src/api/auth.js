import request from "./index";

export const login = (data) => request.post("/auth/login", data);
export const register = (data) => request.post("/auth/register", data);
