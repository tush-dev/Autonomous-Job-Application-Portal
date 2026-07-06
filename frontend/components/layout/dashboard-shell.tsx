"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import { CommandPalette } from "@/components/layout/command-palette";
import { TopBar } from "@/components/layout/top-bar";
import { FloatingAI } from "@/components/layout/floating-ai";
import { useAuth } from "@/hooks/use-auth";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [cmdOpen, setCmdOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    const saved = localStorage.getItem("sidebar-collapsed");
    if (saved) setSidebarCollapsed(saved === "true");
  }, []);

  const toggleSidebar = () => {
    const next = !sidebarCollapsed;
    setSidebarCollapsed(next);
    localStorage.setItem("sidebar-collapsed", String(next));
  };

  const sidebarWidth = sidebarCollapsed ? 72 : 260;

  return (
    <div className="relative min-h-screen bg-background">
      <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
      <CommandPalette open={cmdOpen} onOpenChange={setCmdOpen} />
      <FloatingAI />

      <TopBar onCmdOpen={() => setCmdOpen(true)} sidebarCollapsed={sidebarCollapsed} user={user} />

      <motion.main
        animate={{ paddingLeft: sidebarWidth }}
        transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
        className="pt-16 lg:pt-20 min-h-screen"
      >
        <div className="px-4 lg:px-8 py-6 lg:py-8">
          {children}
        </div>
      </motion.main>
    </div>
  );
}
