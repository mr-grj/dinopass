import axios from "axios";

import { getKeyDerivation } from "../utils";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
});

apiClient.interceptors.request.use((config) => {
  const keyDerivation = getKeyDerivation();
  if (keyDerivation) {
    config.headers["x-ciphermoth-key-derivation"] = keyDerivation;
  }
  return config;
});

export default apiClient;
