"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";

export function useAuth(requireAuth = true) {
  const router = useRouter();
  const { user, isAuthenticated, hydrate } = useAuthStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (requireAuth && !isAuthenticated) {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.push("/auth/login");
      }
    }
  }, [requireAuth, isAuthenticated, router]);

  return { user, isAuthenticated };
}
