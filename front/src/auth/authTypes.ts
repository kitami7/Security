// auth/types.ts
import type { paths } from "../openapi-schema";

export type User = paths["/me"]["get"]["responses"]["200"]["content"]["application/json"];

export interface AuthContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  fetchUser: () => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean
}

export interface AuthProviderProps {
  children: React.ReactNode;
}
