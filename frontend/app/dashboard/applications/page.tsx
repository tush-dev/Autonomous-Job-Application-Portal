"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Briefcase, Building2, MapPin, Clock, Calendar,
  ArrowRight, MoreHorizontal, Plus,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

type StatusType = "SAVED" | "APPLIED" | "SCREENING" | "INTERVIEW" | "OFFER" | "REJECTED";

interface Application {
  id: string;
  job: {
    id: string;
    title: string;
    company?: { name: string };
    location?: string;
  };
  status: StatusType;
  submitted_at?: string;
  notes?: string;
  created_at: string;
}

const columns: { id: StatusType; label: string; color: string }[] = [
  { id: "SAVED", label: "Saved", color: "border-t-blue-500" },
  { id: "APPLIED", label: "Applied", color: "border-t-amber-500" },
  { id: "SCREENING", label: "Screening", color: "border-t-purple-500" },
  { id: "INTERVIEW", label: "Interview", color: "border-t-emerald-500" },
  { id: "OFFER", label: "Offer", color: "border-t-green-500" },
  { id: "REJECTED", label: "Rejected", color: "border-t-rose-500" },
];

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
};

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get("/applications")
      .then((res) => setApplications(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const getColumnApps = (status: StatusType) =>
    applications.filter((a) => a.status === status);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64 rounded-xl" />
        <div className="flex gap-4 overflow-x-auto pb-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-96 w-72 shrink-0 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6 pb-12">
      {/* Header */}
      <motion.div variants={fadeUp} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Applications</h1>
          <p className="mt-1 text-muted-foreground">
            Track and manage your job applications
          </p>
        </div>
        <Button className="rounded-xl gap-2">
          <Plus className="h-4 w-4" /> Add Application
        </Button>
      </motion.div>

      {/* Kanban board */}
      <motion.div variants={fadeUp} className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide" style={{ scrollSnapType: "x mandatory" }}>
        {columns.map((col) => {
          const apps = getColumnApps(col.id);
          return (
            <div
              key={col.id}
              className="flex w-72 shrink-0 flex-col rounded-2xl border border-border/30 bg-card/30 backdrop-blur-sm"
              style={{ scrollSnapAlign: "start" }}
            >
              {/* Column header */}
              <div className={cn("flex items-center justify-between border-b border-border/20 px-4 py-3 rounded-t-2xl", col.color)}>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold">{col.label}</span>
                  <Badge variant="outline" className="text-[10px] h-5 px-1.5">
                    {apps.length}
                  </Badge>
                </div>
                <button className="rounded-lg p-1 text-muted-foreground hover:text-foreground transition-colors">
                  <MoreHorizontal className="h-3.5 w-3.5" />
                </button>
              </div>

              {/* Cards */}
              <ScrollArea className="flex-1 p-3 space-y-3" style={{ maxHeight: "calc(100vh - 280px)" }}>
                {apps.length === 0 ? (
                  <div className="flex flex-col items-center py-8 text-center">
                    <div className="rounded-xl bg-muted/50 p-3 mb-2">
                      <Briefcase className="h-5 w-5 text-muted-foreground/50" />
                    </div>
                    <p className="text-xs text-muted-foreground">No applications</p>
                  </div>
                ) : (
                  apps.map((app, i) => (
                    <motion.div
                      key={app.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                    >
                      <Card className="cursor-pointer hover:border-primary/30 transition-all duration-200">
                        <CardContent className="p-4 space-y-2">
                          <p className="text-sm font-semibold leading-snug line-clamp-2">
                            {app.job?.title || "Unknown Position"}
                          </p>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Building2 className="h-3 w-3" />
                            <span className="truncate">{app.job?.company?.name || "Unknown"}</span>
                          </div>
                          {app.job?.location && (
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <MapPin className="h-3 w-3" />
                              <span>{app.job.location}</span>
                            </div>
                          )}
                          <div className="flex items-center gap-1 text-[10px] text-muted-foreground pt-1">
                            <Clock className="h-3 w-3" />
                            <span>{new Date(app.created_at).toLocaleDateString()}</span>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))
                )}
              </ScrollArea>
            </div>
          );
        })}
      </motion.div>
    </motion.div>
  );
}
