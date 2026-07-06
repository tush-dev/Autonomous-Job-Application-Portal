"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  Bell,
  Moon,
  Sun,
  Command,
  LogOut,
  User as UserIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "next-themes";

interface TopBarProps {
  onCmdOpen: () => void;
  sidebarCollapsed: boolean;
  user?: {
    full_name?: string;
    email?: string;
    avatar_url?: string;
  } | null;
}

export function TopBar({ onCmdOpen, sidebarCollapsed, user }: TopBarProps) {
  const { theme, setTheme } = useTheme();
  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "U";
  const sidebarWidth = sidebarCollapsed ? 72 : 260;

  return (
    <header
      className="fixed top-0 right-0 z-30 h-16 lg:h-20 border-b border-border/30 bg-background/70 backdrop-blur-xl transition-all duration-300"
      style={{ left: sidebarWidth }}
    >
      <div className="flex h-full items-center justify-between px-4 lg:px-8">
        {/* Search / Cmd+K trigger */}
        <button
          onClick={onCmdOpen}
          className="group flex items-center gap-2 rounded-2xl border border-border/50 bg-card/50 px-4 py-2 text-sm text-muted-foreground hover:border-border hover:bg-card/80 transition-all duration-200 w-full max-w-md"
        >
          <Search className="h-4 w-4 shrink-0" />
          <span className="flex-1 text-left">Search or type a command...</span>
          <kbd className="hidden sm:inline-flex items-center gap-1 rounded-lg border border-border/50 bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
            <Command className="h-2.5 w-2.5" />K
          </kbd>
        </button>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="rounded-xl"
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="rounded-xl relative">
            <Bell className="h-4 w-4" />
            <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-primary" />
          </Button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="rounded-xl gap-2 pl-2">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.avatar_url} />
                  <AvatarFallback className="text-xs bg-primary/10 text-primary">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden sm:inline text-sm font-medium">
                  {user?.full_name || "User"}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <span>{user?.full_name || "User"}</span>
                  <span className="text-xs font-normal text-muted-foreground">
                    {user?.email || ""}
                  </span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <UserIcon className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem>
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
