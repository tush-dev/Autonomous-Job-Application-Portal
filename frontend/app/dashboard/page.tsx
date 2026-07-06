"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Upload,
  Search,
  FileText,
  Mic,
  Sparkles,
  TrendingUp,
  Briefcase,
  Target,
  Star,
  ArrowRight,
  Clock,
  Building2,
  MapPin,
  GraduationCap,
  BookOpen,
  Bot,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { DashboardData } from "@/types/api";

const quickActions = [
  { icon: Upload, label: "Upload Resume", href: "/dashboard/resumes", gradient: "from-blue-500 to-blue-600" },
  { icon: Search, label: "Find Jobs", href: "/dashboard/jobs", gradient: "from-purple-500 to-purple-600" },
  { icon: FileText, label: "Review Resume", href: "/dashboard/resumes", gradient: "from-emerald-500 to-emerald-600" },
  { icon: Mic, label: "Prepare Interview", href: "/dashboard/interviews", gradient: "from-amber-500 to-amber-600" },
];

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] } },
};

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [greeting, setGreeting] = useState("Good morning");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 17) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  useEffect(() => {
    apiClient
      .get("/matching/dashboard")
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-40 w-full rounded-2xl" />
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-2xl" />
          ))}
        </div>
        <div className="grid gap-5 lg:grid-cols-3">
          <Skeleton className="h-64 rounded-2xl lg:col-span-2" />
          <Skeleton className="h-64 rounded-2xl" />
        </div>
      </div>
    );
  }

  const health = data?.resume_health || data?.career_insights;
  const resumeScore = health?.resume_health_score ?? 0;
  const atsScore = health?.ats_score ?? 0;
  const jobsToday = data?.recommended_jobs?.length ?? 0;
  const jobMatches = data?.recommended_jobs ?? [];
  const recentJobs = data?.recent_jobs ?? [];
  const appStats = data?.application_stats;
  const learningPath = data?.learning_path ?? [];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Hero Section */}
      <motion.div variants={fadeUp}>
        <Card className="relative overflow-hidden border-0 bg-gradient-to-br from-primary/10 via-purple-500/5 to-emerald-500/5">
          <div className="absolute inset-0 bg-grid-white/[0.02] [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]" />
          <CardContent className="relative p-6 lg:p-8">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Bot className="h-3.5 w-3.5 text-primary" />
                  <span>Career Copilot is online</span>
                </div>
                <h1 className="text-2xl lg:text-3xl font-bold tracking-tight">
                  {greeting}, <span className="text-gradient">Tushar</span>
                </h1>
                <p className="text-sm text-muted-foreground">
                  {appStats?.total || 0} applications tracked
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                {[
                  { label: "Resume", value: resumeScore.toFixed(0), color: "text-gradient" },
                  { label: "ATS", value: atsScore.toFixed(0), color: "text-blue-400" },
                  { label: "Today", value: jobsToday.toString(), color: "text-emerald-400" },
                  { label: "Interviews", value: (data?.upcoming_interviews?.length ?? 0).toString(), color: "text-purple-400" },
                ].map((s) => (
                  <div key={s.label} className="flex flex-col items-center rounded-xl border border-border/50 bg-card/50 px-4 py-2.5">
                    <span className="text-[10px] text-muted-foreground">{s.label}</span>
                    <span className={`text-xl font-bold ${s.color}`}>{s.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {quickActions.map((action) => (
                <Link key={action.label} href={action.href}>
                  <Button variant="outline" className="group rounded-xl border-border/50 bg-background/50 hover:bg-background/80 transition-all duration-200">
                    <div className={`rounded-lg p-1 mr-2 bg-gradient-to-br ${action.gradient}`}>
                      <action.icon className="h-3.5 w-3.5 text-white" />
                    </div>
                    <span>{action.label}</span>
                    <ArrowRight className="ml-2 h-3.5 w-3.5 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
                  </Button>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Stats */}
      <motion.div variants={fadeUp} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Applications", value: appStats?.total ?? 0, icon: Briefcase, color: "text-blue-400", bg: "bg-blue-500/10" },
          { label: "Interview Rate", value: appStats?.interview ?? 0, icon: TrendingUp, color: "text-emerald-400", bg: "bg-emerald-500/10" },
          { label: "Offers", value: appStats?.offer ?? 0, icon: Star, color: "text-amber-400", bg: "bg-amber-500/10" },
          { label: "Active", value: appStats?.applied ?? 0, icon: Target, color: "text-purple-400", bg: "bg-purple-500/10" },
        ].map((stat) => (
          <Card key={stat.label} className="group hover:border-primary/30 transition-all duration-300">
            <CardContent className="p-5">
              <div className={`rounded-xl p-2 w-fit ${stat.bg}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
              <p className="mt-3 text-2xl font-bold">{stat.value}</p>
              <p className="mt-0.5 text-xs text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Main grid */}
      <div className="grid gap-5 lg:grid-cols-3">
        {/* Recommended Jobs */}
        <motion.div variants={fadeUp} className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">AI-Recommended Jobs</h2>
            </div>
            <Link href="/dashboard/jobs">
              <Button variant="ghost" size="sm" className="text-xs gap-1">
                View all <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </div>

          {jobMatches.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center py-12 text-center">
                <div className="rounded-2xl bg-muted p-4 mb-4">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                </div>
                <p className="font-medium">No recommendations yet</p>
                <p className="text-sm text-muted-foreground mt-1">Upload your resume to get personalized job matches</p>
                <Link href="/dashboard/resumes">
                  <Button variant="outline" className="mt-4 gap-2">
                    <Upload className="h-4 w-4" /> Upload Resume
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2.5">
              {jobMatches.slice(0, 6).map((job, i) => (
                <motion.div key={job.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                  <Card className="group hover:border-primary/30 transition-all duration-300 cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-purple-500/20">
                          <Building2 className="h-6 w-6 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <h3 className="font-semibold truncate">{job.title}</h3>
                              <p className="text-sm text-muted-foreground">{job.company?.name || "Unknown"}</p>
                            </div>
                            <Badge variant={job.match?.match_score != null && job.match.match_score >= 60 ? "success" : job.match?.match_score != null && job.match.match_score >= 30 ? "warning" : "secondary"} className="shrink-0">
                              {job.match?.match_score?.toFixed(0) ?? "?"}% match
                            </Badge>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
                            {job.location && <span className="inline-flex items-center gap-1"><MapPin className="h-3 w-3" /> {job.location}</span>}
                            <span className="capitalize">{job.remote}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Right column */}
        <motion.div variants={fadeUp} className="space-y-4">
          <Card>
            <CardHeader className="pb-2 px-4 pt-4">
              <div className="flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-primary" />
                <CardTitle className="text-sm font-medium">Learning Roadmap</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="px-4 pb-4">
              {learningPath.length === 0 ? (
                <div className="flex flex-col items-center py-8 text-center">
                  <div className="rounded-2xl bg-muted p-3 mb-3">
                    <GraduationCap className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <p className="text-sm text-muted-foreground">Skills recommendations will appear here after resume analysis</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {learningPath.slice(0, 4).map((skill) => (
                    <div key={skill.id} className="space-y-1.5">
                      <div className="flex items-center justify-between text-sm">
                        <span>{skill.skill_name}</span>
                        <span className="text-xs text-muted-foreground">{skill.progress}%</span>
                      </div>
                      <Progress value={skill.progress} className="h-1.5" />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2 px-4 pt-4">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="px-4 pb-4">
              <div className="space-y-4">
                {recentJobs.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">No recent activity yet</p>
                ) : (
                  recentJobs.slice(0, 4).map((job) => (
                    <div key={job.id} className="flex items-center gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                        <Briefcase className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{job.title}</p>
                        <p className="text-xs text-muted-foreground">{job.company?.name || "Unknown"}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
