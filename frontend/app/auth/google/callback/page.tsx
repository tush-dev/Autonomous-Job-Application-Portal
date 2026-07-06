"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api-client";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    const currentOrigin = window.location.origin;
    const redirectUri = currentOrigin + "/auth/google/callback";

    console.log("[Google OAuth Callback]", {
      currentOrigin,
      redirectUri,
      hasCode: !!code,
      codePrefix: code ? code.substring(0, 10) + "..." : null,
      fullUrl: window.location.href,
    });

    if (!code) {
      setError("No authorization code received from Google");
      return;
    }

    apiClient
      .post("/auth/google", {
        code,
        redirect_uri: redirectUri,
      })
      .then((res) => {
        localStorage.setItem("access_token", res.data.access_token);
        localStorage.setItem("refresh_token", res.data.refresh_token);
        localStorage.setItem("user", JSON.stringify(res.data.user));
        router.push("/dashboard");
      })
      .catch((err) => {
        console.error("[Google OAuth Callback Error]", {
          status: err?.response?.status,
          data: err?.response?.data,
          message: err?.message,
        });
        setError("Google sign-in failed. Please try again.");
      });
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-500">{error}</p>
          <button
            onClick={() => router.push("/auth/login")}
            className="mt-4 text-sm text-primary hover:underline"
          >
            Back to login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
        <p className="mt-4 text-muted-foreground">Signing you in with Google...</p>
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
        <p className="mt-4 text-muted-foreground">Loading...</p>
      </div>
    }>
      <GoogleCallbackContent />
    </Suspense>
  );
}
