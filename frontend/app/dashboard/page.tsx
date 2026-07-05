"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Briefcase,
  FileText,
  TrendingUp,
  Calendar,
  Loader2,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import type { ApplicationStats } from "@/types/api";

const statCards = [
  { label: "Total Applications", key: "total", icon: Briefcase, color: "text-blue-500" },
  { label: "Interviews", key: "interview", icon: Calendar, color: "text-green-500" },
  { label: "Offers", key: "offer", icon: TrendingUp, color: "text-purple-500" },
  { label: "Resumes", key: "resumes", icon: FileText, color: "text-orange-500" },
];

export default function DashboardPage() {
  const [stats, setStats] = useState<ApplicationStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get("/applications/stats")
      .then((res) => setStats(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your job search activity
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card, index) => (
          <motion.div
            key={card.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="rounded-xl border p-6"
          >
            <div className="flex items-center justify-between">
              <card.icon className={`h-8 w-8 ${card.color}`} />
            </div>
            <p className="mt-4 text-2xl font-bold">
              {card.key === "resumes"
                ? "—"
                : stats?.[card.key as keyof ApplicationStats] ?? 0}
            </p>
            <p className="text-sm text-muted-foreground">{card.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border p-6">
          <h2 className="mb-4 text-lg font-semibold">Application Status</h2>
          {stats ? (
            <div className="space-y-3">
              {[
                { label: "Applied", value: stats.applied, color: "bg-blue-500" },
                { label: "Screening", value: stats.screening, color: "bg-yellow-500" },
                { label: "Interview", value: stats.interview, color: "bg-green-500" },
                { label: "Offer", value: stats.offer, color: "bg-purple-500" },
                { label: "Rejected", value: stats.rejected, color: "bg-red-500" },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-3">
                  <div className={`h-3 w-3 rounded-full ${item.color}`} />
                  <span className="flex-1 text-sm">{item.label}</span>
                  <span className="text-sm font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No applications yet
            </p>
          )}
        </div>

        <div className="rounded-xl border p-6">
          <h2 className="mb-4 text-lg font-semibold">Success Rates</h2>
          {stats ? (
            <div className="space-y-4">
              <div>
                <div className="mb-1 flex justify-between text-sm">
                  <span>Interview Rate</span>
                  <span className="font-medium">
                    {stats.interview_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-green-500 transition-all"
                    style={{ width: `${Math.min(stats.interview_rate, 100)}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="mb-1 flex justify-between text-sm">
                  <span>Offer Rate</span>
                  <span className="font-medium">
                    {stats.offer_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-purple-500 transition-all"
                    style={{ width: `${Math.min(stats.offer_rate, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Not enough data yet
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
