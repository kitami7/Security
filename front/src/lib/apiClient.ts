// src/lib/apiClient.ts
import createClient from "openapi-fetch";
import type { paths } from "../openapi-schema";

export const apiClient = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_URL,
  fetch: (request) => fetch(request),
  credentials: "include"
});
