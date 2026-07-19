"use client";

import { useCallback, useEffect, useState } from "react";

import {
  Search,
  Bell,
  Moon,
  Sun,
  Command,
  LogOut,
  User as UserIcon,
} from "lucide-react";
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
import { apiClient } from "@/lib/api-client";
import type { Notification } from "@/types/api";

interface TopBarProps {
  onCmdOpen: () => void;
  sidebarCollapsed: boolean;
  isMobile?: boolean;
  user?: {
    full_name?: string;
    email?: string;
    avatar_url?: string;
  } | null;
}

export function TopBar({ onCmdOpen, sidebarCollapsed, isMobile = false, user }: TopBarProps) {
  const { resolvedTheme, setTheme } = useTheme();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const unreadCount = notifications.filter((item) => !item.is_read).length;

  const loadNotifications = useCallback(async () => {
    setNotificationsLoading(true);
    try {
      const response = await apiClient.get<Notification[]>("/notifications");
      setNotifications(response.data);
    } catch {
      setNotifications([]);
    } finally {
      setNotificationsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadNotifications();
  }, [loadNotifications]);

  const markAllRead = async () => {
    setNotifications((items) => items.map((item) => ({ ...item, is_read: true })));
    try {
      await apiClient.post("/notifications/read-all");
    } catch {
      void loadNotifications();
    }
  };
  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "U";
  const sidebarWidth = sidebarCollapsed ? 72 : 260;

  return (
    <header
      className="fixed top-0 right-0 z-30 h-16 lg:h-20 border-b border-border/60 bg-background/85 backdrop-blur-xl transition-all duration-300"
      style={{ left: isMobile ? 0 : sidebarWidth }}
    >
      <div className="flex h-full items-center justify-between px-4 lg:px-8">
        {/* Search / Cmd+K trigger */}
        <button
          onClick={onCmdOpen}
          className="group flex w-full max-w-md items-center gap-2 rounded-full border border-border/70 bg-card/80 px-3 py-2.5 text-sm text-muted-foreground shadow-sm transition-all duration-200 hover:border-primary/25 hover:bg-card sm:px-4"
        >
          <Search className="h-4 w-4 shrink-0" />
          <span className="flex-1 truncate text-left"><span className="sm:hidden">Search...</span><span className="hidden sm:inline">Search or type a command...</span></span>
          <kbd className="hidden sm:inline-flex items-center gap-1 rounded-lg border border-border/50 bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
            <Command className="h-2.5 w-2.5" />K
          </kbd>
        </button>

        {/* Right actions */}
        <div className="ml-2 flex items-center gap-1 sm:gap-2">
          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            aria-label={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            className="hidden rounded-xl sm:inline-flex"
          >
            {resolvedTheme === "dark" ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>

          {/* Notifications */}
          <DropdownMenu
            open={notificationsOpen}
            onOpenChange={(next) => {
              setNotificationsOpen(next);
              if (next) void loadNotifications();
            }}
          >
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-xl relative"
                aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ""}`}
              >
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <span className="absolute right-1.5 top-1.5 flex h-2 w-2 rounded-full bg-primary" />
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[min(22rem,calc(100vw-2rem))] p-0">
              <div className="flex items-center justify-between border-b border-border px-4 py-3">
                <div>
                  <p className="font-semibold">Notifications</p>
                  <p className="text-xs text-muted-foreground">
                    {unreadCount ? `${unreadCount} unread` : "You're all caught up"}
                  </p>
                </div>
                {unreadCount > 0 && (
                  <button onClick={markAllRead} className="text-xs font-medium text-primary hover:underline">
                    Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto p-2">
                {notificationsLoading ? (
                  <p className="py-8 text-center text-sm text-muted-foreground">Loading notifications…</p>
                ) : notifications.length === 0 ? (
                  <div className="px-4 py-8 text-center">
                    <Bell className="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
                    <p className="text-sm font-medium">No notifications yet</p>
                    <p className="mt-1 text-xs text-muted-foreground">Job and application updates will appear here.</p>
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`mb-1 rounded-xl px-3 py-2.5 ${notification.is_read ? "" : "bg-primary/10"}`}
                    >
                      <div className="flex gap-2">
                        {!notification.is_read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />}
                        <div className="min-w-0">
                          <p className="text-sm font-medium">{notification.title}</p>
                          {notification.body && <p className="mt-0.5 text-xs text-muted-foreground">{notification.body}</p>}
                          <p className="mt-1 text-[11px] text-muted-foreground">
                            {new Date(notification.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

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
