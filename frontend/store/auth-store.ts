import { create } from "zustand";
import type { User } from "@/types/api";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: true }),
  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    set({ user: null, isAuthenticated: false });
  },
  hydrate: () => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) {
        set({ user: JSON.parse(stored), isAuthenticated: true });
      }
    } catch {
      localStorage.removeItem("user");
    }
  },
}));
