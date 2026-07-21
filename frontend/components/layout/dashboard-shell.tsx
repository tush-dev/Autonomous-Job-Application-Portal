"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/top-bar";
import { useAuth } from "@/hooks/use-auth";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Brain,
  Briefcase,
  FileText,
  GraduationCap,
  KanbanSquare,
  LayoutDashboard,
  Menu,
  MessageSquare,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";

const CommandPalette = dynamic(
  () => import("@/components/layout/command-palette").then((module) => module.CommandPalette),
  { ssr: false }
);
const FloatingAI = dynamic(
  () => import("@/components/layout/floating-ai").then((module) => module.FloatingAI),
  { ssr: false }
);

const mobileNav = [
  { label: "Home", href: "/dashboard", icon: LayoutDashboard },
  { label: "Jobs", href: "/dashboard/jobs", icon: Briefcase },
  { label: "Applications", href: "/dashboard/applications", icon: KanbanSquare },
  { label: "Resumes", href: "/dashboard/resumes", icon: FileText },
];

const mobileMoreNav = [
  { label: "AI Coach", href: "/dashboard/coach", icon: MessageSquare },
  { label: "Career Insights", href: "/dashboard/insights", icon: Brain },
  { label: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { label: "Interviews", href: "/dashboard/interviews", icon: GraduationCap },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [cmdOpen, setCmdOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user } = useAuth();
  const pathname = usePathname();

  useEffect(() => {
    const saved = localStorage.getItem("sidebar-collapsed");
    if (saved) setSidebarCollapsed(saved === "true");
  }, []);

  useEffect(() => {
    const media = window.matchMedia("(max-width: 767px)");
    const sync = () => setIsMobile(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);

  const toggleSidebar = () => {
    const next = !sidebarCollapsed;
    setSidebarCollapsed(next);
    localStorage.setItem("sidebar-collapsed", String(next));
  };

  const sidebarWidth = sidebarCollapsed ? 72 : 260;

  return (
    <div className="relative min-h-screen bg-background">
      {!isMobile && <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />}
      <CommandPalette open={cmdOpen} onOpenChange={setCmdOpen} />
      <FloatingAI />

      <TopBar onCmdOpen={() => setCmdOpen(true)} sidebarCollapsed={sidebarCollapsed} isMobile={isMobile} user={user} />

      <motion.main
        animate={{ paddingLeft: isMobile ? 0 : sidebarWidth }}
        transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
        className="min-h-screen pb-[calc(6.5rem+env(safe-area-inset-bottom))] pt-16 md:pb-0 lg:pt-20"
      >
        <div className="mx-auto w-full max-w-[1600px] px-3 py-4 sm:px-4 sm:py-6 lg:px-8 lg:py-8">
          {children}
        </div>
      </motion.main>

      {isMobile && (
        <nav aria-label="Mobile navigation" className="fixed inset-x-3 bottom-[calc(.75rem+env(safe-area-inset-bottom))] z-40 grid grid-cols-5 rounded-2xl border border-sidebar-border bg-sidebar/95 p-1.5 shadow-2xl shadow-primary/20 backdrop-blur-xl">
          {mobileNav.map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href + "/"));
            return (
              <Link key={item.href} href={item.href} aria-label={item.label} className={cn("flex min-h-12 min-w-0 flex-col items-center justify-center gap-1 rounded-xl px-1 py-1.5 text-[10px] font-medium text-sidebar-foreground transition-colors", active && "bg-sidebar-accent text-sidebar-primary")}>
                <item.icon className="h-[18px] w-[18px]" />
                <span className="max-w-full truncate">{item.label}</span>
              </Link>
            );
          })}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(true)}
            aria-label="More navigation"
            className={cn(
              "flex min-h-12 min-w-0 flex-col items-center justify-center gap-1 rounded-xl px-1 py-1.5 text-[10px] font-medium text-sidebar-foreground transition-colors",
              mobileMoreNav.some((item) => pathname.startsWith(item.href)) && "bg-sidebar-accent text-sidebar-primary"
            )}
          >
            <Menu className="h-[18px] w-[18px]" />
            <span>More</span>
          </button>
        </nav>
      )}

      <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
        <SheetContent side="bottom" className="rounded-t-3xl border-sidebar-border bg-sidebar px-4 pb-[calc(1rem+env(safe-area-inset-bottom))] text-sidebar-foreground">
          <SheetHeader className="text-left">
            <SheetTitle className="text-sidebar-accent-foreground">Explore JobAgent</SheetTitle>
          </SheetHeader>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {mobileMoreNav.map((item) => {
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex min-h-14 items-center gap-3 rounded-2xl border border-sidebar-border px-4 py-3 text-sm font-medium",
                    active ? "bg-sidebar-primary text-sidebar-primary-foreground" : "bg-sidebar-accent/60 text-sidebar-accent-foreground"
                  )}
                >
                  <item.icon className="h-5 w-5 shrink-0" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
