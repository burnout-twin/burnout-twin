"use client"

import { useState } from "react"
import { Calendar, GitPullRequest, Code, Mail, Users, Clock } from "lucide-react"

type StreamItem = {
  id: string
  icon: "calendar" | "pr" | "code" | "email" | "meeting"
  label: string
  time: string
  impact: "low" | "medium" | "high"
  active?: boolean
}

const streamItems: StreamItem[] = [
  { id: "1", icon: "calendar", label: "Team Sync", time: "10:00 AM", impact: "medium" },
  { id: "2", icon: "pr", label: "PR #102 - Fix login bug", time: "10:45 AM", impact: "low" },
  { id: "3", icon: "calendar", label: "Deep Work Block", time: "2:00 PM", impact: "low", active: true },
  { id: "4", icon: "email", label: "Client Follow-up", time: "3:30 PM", impact: "medium" },
  { id: "5", icon: "meeting", label: "1:1 with Manager", time: "4:00 PM", impact: "high" },
  { id: "6", icon: "code", label: "Deploy v2.1.0", time: "5:15 PM", impact: "medium" },
]

const iconMap = {
  calendar: Calendar,
  pr: GitPullRequest,
  code: Code,
  email: Mail,
  meeting: Users,
}

const impactColors = {
  low: "bg-primary/15 text-primary",
  medium: "bg-accent/15 text-accent",
  high: "bg-destructive/15 text-destructive",
}

export function DedalusStream({
  onItemHover,
}: {
  onItemHover?: (item: StreamItem | null) => void
}) {
  const [hoveredId, setHoveredId] = useState<string | null>(null)

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between px-6 pt-6 pb-4">
        <h2 className="text-lg font-semibold text-card-foreground">Dedalus Stream</h2>
        <div className="flex items-center gap-1.5">
          <Clock className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs text-muted-foreground">Today</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <div className="flex flex-col gap-2">
          {streamItems.map((item, index) => {
            const Icon = iconMap[item.icon]
            return (
              <button
                key={item.id}
                type="button"
                className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all duration-200 animate-slide-in-left ${
                  item.active
                    ? "bg-primary/10 ring-1 ring-primary/30"
                    : hoveredId === item.id
                      ? "bg-secondary"
                      : "hover:bg-secondary"
                }`}
                style={{ animationDelay: `${index * 80}ms` }}
                onMouseEnter={() => {
                  setHoveredId(item.id)
                  onItemHover?.(item)
                }}
                onMouseLeave={() => {
                  setHoveredId(null)
                  onItemHover?.(null)
                }}
              >
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                    item.active ? "bg-primary/20" : "bg-secondary"
                  }`}
                >
                  <Icon
                    className={`h-4 w-4 ${item.active ? "text-primary" : "text-muted-foreground"}`}
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-card-foreground truncate">
                    {item.label}
                  </p>
                  <p className="text-xs text-muted-foreground">{item.time}</p>
                </div>
                <span
                  className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${impactColors[item.impact]}`}
                >
                  {item.impact}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
