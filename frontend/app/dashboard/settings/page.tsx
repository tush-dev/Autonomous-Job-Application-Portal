"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Settings,
  User,
  Bell,
  Shield,
  Loader2,
  Save,
  Palette,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  is_verified: boolean;
  mfa_enabled: boolean;
  created_at: string;
}

export default function SettingsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [name, setName] = useState("");
  const [dailyLimit, setDailyLimit] = useState(20);

  useEffect(() => {
    Promise.all([
      apiClient.get("/auth/me"),
      apiClient.get("/auth/me/settings"),
    ])
      .then(([profileRes, settingsRes]) => {
        setProfile(profileRes.data);
        setName(profileRes.data.full_name);
        setDailyLimit(settingsRes.data.daily_application_limit ?? 20);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await Promise.all([
        apiClient.patch("/auth/me", { full_name: name }),
        apiClient.put("/auth/me/settings", { daily_application_limit: dailyLimit }),
      ]);
      toast.success("Settings saved");
    } catch {
      toast.error("Failed to save settings");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="mt-1 text-muted-foreground">Manage your account and preferences</p>
      </div>

      <div className="rounded-xl border">
        <div className="border-b px-6 py-4">
          <div className="flex items-center gap-2">
            <User className="h-5 w-5 text-muted-foreground" />
            <h2 className="font-semibold">Profile</h2>
          </div>
        </div>
        <form onSubmit={handleSave} className="space-y-4 p-6">
          <div>
            <label className="block text-sm font-medium mb-1">Full Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              value={profile?.email || ""}
              disabled
              className="w-full rounded-lg border bg-muted px-3 py-2 text-sm opacity-60"
            />
            <p className="mt-1 text-xs text-muted-foreground">
              {profile?.is_verified ? "Verified" : "Not verified"}
            </p>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save Changes
          </button>
        </form>
      </div>

      <div className="rounded-xl border">
        <div className="border-b px-6 py-4">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-muted-foreground" />
            <h2 className="font-semibold">Security</h2>
          </div>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Two-Factor Authentication</p>
              <p className="text-sm text-muted-foreground">
                {profile?.mfa_enabled ? "MFA is enabled" : "Add an extra layer of security"}
              </p>
            </div>
            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
              profile?.mfa_enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"
            }`}>
              {profile?.mfa_enabled ? "Enabled" : "Disabled"}
            </span>
          </div>
        </div>
      </div>

      <div className="rounded-xl border">
        <div className="border-b px-6 py-4">
          <div className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-muted-foreground" />
            <h2 className="font-semibold">Preferences</h2>
          </div>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Daily Application Limit</p>
              <p className="text-sm text-muted-foreground">Maximum applications per day</p>
            </div>
            <input
              type="number"
              min={1}
              max={100}
              value={dailyLimit}
              onChange={(e) => setDailyLimit(Number(e.target.value))}
              className="w-20 rounded-lg border bg-background px-3 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
