import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL;

const api = axios.create({ baseURL: API_BASE });
let refreshPromise = null;

const clearSession = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

export const refreshAccessToken = async () => {
  if (refreshPromise) return refreshPromise;

  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) throw new Error("No refresh token available");

  refreshPromise = axios.post(`${API_BASE}/auth/refresh`, {
    refresh_token: refreshToken,
  }).then((response) => {
    const { access_token: accessToken, refresh_token: newRefreshToken } = response.data;
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", newRefreshToken);
    return accessToken;
  }).finally(() => {
    refreshPromise = null;
  });

  return refreshPromise;
};

// attach access token to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = localStorage.getItem("refresh_token");

    if (
      error.response?.status !== 401 ||
      originalRequest?._retry ||
      !refreshToken ||
      originalRequest?.url?.endsWith("/auth/refresh")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const accessToken = await refreshAccessToken();
      originalRequest.headers.Authorization = `Bearer ${accessToken}`;

      return api(originalRequest);
    } catch (refreshError) {
      clearSession();
      window.location.assign("/login");
      return Promise.reject(refreshError);
    }
  },
);

export const logout = async () => {
  const refreshToken = localStorage.getItem("refresh_token");

  try {
    if (refreshToken) {
      await axios.post(`${API_BASE}/auth/logout`, { refresh_token: refreshToken });
    }
  } finally {
    clearSession();
    window.location.assign("/login");
  }
};

export default api;