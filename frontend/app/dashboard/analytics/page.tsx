"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BarChart3, TrendingUp, Target, Star, Briefcase,
  Calendar, ArrowUpRight, ArrowDownRight,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface AppStats {
  total: number;
  applied: number;
  screening: number;
  interview: number;
  offer: number;
  rejected: number;
  failed: number;
  interview_rate: number;
  offer_rate: number;
}

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
};

const stageColors: Record<string, string> = {
  applied: "bg-amber-500",
  screening: "bg-purple-500",
  interview: "bg-emerald-500",
  offer: "bg-green-500",
  rejected: "bg-rose-500",
};

export default function AnalyticsPage() {
  const [stats, setStats] = useState<AppStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [weeklyActivity] = useState([12, 19, 8, 15, 22, 10, 6]);

  useEffect(() => {
    apiClient
      .get("/applications/stats")
      .then((res) => setStats(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64 rounded-xl" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-2xl" />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-80 rounded-2xl" />
          <Skeleton className="h-80 rounded-2xl" />
        </div>
      </div>
    );
  }

  const s = stats || { total: 0, applied: 0, screening: 0, interview: 0, offer: 0, rejected: 0, failed: 0, interview_rate: 0, offer_rate: 0 };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-8 pb-12">
      {/* Header */}
      <motion.div variants={fadeUp}>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="mt-1 text-muted-foreground">
          Track your application performance and trends
        </p>
      </motion.div>

      {/* Stats cards */}
      <motion.div variants={fadeUp} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Applications", value: s.total, icon: Briefcase, change: "+12%", color: "text-blue-400", bg: "bg-blue-500/10", up: true },
          { label: "Interview Rate", value: `${(s.interview_rate * 100).toFixed(0)}%`, icon: TrendingUp, change: "+5%", color: "text-emerald-400", bg: "bg-emerald-500/10", up: true },
          { label: "Offer Rate", value: `${(s.offer_rate * 100).toFixed(0)}%`, icon: Star, change: "+2%", color: "text-amber-400", bg: "bg-amber-500/10", up: true },
          { label: "Rejected", value: s.rejected, icon: Target, change: "-3%", color: "text-rose-400", bg: "bg-rose-500/10", up: false },
        ].map((stat) => (
          <Card key={stat.label} className="group hover:border-primary/30 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className={cn("rounded-xl p-2.5", stat.bg)}>
                  <stat.icon className={cn("h-5 w-5", stat.color)} />
                </div>
                <Badge variant={stat.up ? "success" : "destructive"} className="text-[10px] gap-0.5">
                  {stat.up ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                  {stat.change}
                </Badge>
              </div>
              <p className="mt-4 text-3xl font-bold">{stat.value}</p>
              <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Application Breakdown */}
        <motion.div variants={fadeUp}>
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-primary" />
                <CardTitle className="text-lg">Application Breakdown</CardTitle>
              </div>
              <CardDescription>Distribution across pipeline stages</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {[
                { label: "Applied", value: s.applied },
                { label: "Screening", value: s.screening },
                { label: "Interview", value: s.interview },
                { label: "Offer", value: s.offer },
                { label: "Rejected", value: s.rejected },
              ].map((stage) => {
                const pct = s.total > 0 ? (stage.value / s.total) * 100 : 0;
                return (
                  <div key={stage.label} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div className={cn("h-2.5 w-2.5 rounded-full", stageColors[stage.label.toLowerCase()])} />
                        <span>{stage.label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{stage.value}</span>
                        <span className="text-xs text-muted-foreground">
                          {pct.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
                        className={cn("h-full rounded-full", stageColors[stage.label.toLowerCase()])}
                      />
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </motion.div>

        {/* Success Rates */}
        <motion.div variants={fadeUp}>
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-primary" />
                <CardTitle className="text-lg">Success Rates</CardTitle>
              </div>
              <CardDescription>Conversion metrics from applications to offers</CardDescription>
            </CardHeader>
            <CardContent className="space-y-8">
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-emerald-400" />
                      <span>Interview Rate</span>
                    </div>
                    <span className="font-bold text-emerald-400">
                      {(s.interview_rate * 100).toFixed(0)}%
                    </span>
                  </div>
                  <Progress value={s.interview_rate * 100} className="h-3" />
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 text-amber-400" />
                      <span>Offer Rate</span>
                    </div>
                    <span className="font-bold text-amber-400">
                      {(s.offer_rate * 100).toFixed(0)}%
                    </span>
                  </div>
                  <Progress value={s.offer_rate * 100} className="h-3" />
                </div>
              </div>

              <Separator />

              {/* Weekly Activity */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Calendar className="h-4 w-4 text-primary" />
                  <p className="text-sm font-medium">Weekly Activity</p>
                </div>
                <div className="flex items-end justify-between gap-2 h-28">
                  {weeklyActivity.map((val, i) => {
                    const max = Math.max(...weeklyActivity);
                    const height = (val / max) * 100;
                    return (
                      <div key={i} className="flex flex-1 flex-col items-center gap-1">
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${height}%` }}
                          transition={{ duration: 0.5, delay: i * 0.05, ease: [0.25, 0.1, 0.25, 1] }}
                          className="w-full rounded-lg bg-gradient-to-t from-primary/50 to-primary"
                        />
                        <span className="text-[10px] text-muted-foreground">
                          {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
