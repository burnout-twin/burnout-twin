"use client"

import { useState } from "react"
import { ChevronDown, ArrowUp, ArrowDown, Minus } from "lucide-react"

type Driver = {
  label: string
  direction: "up" | "down" | "stable"
  severity: "low" | "medium" | "high"
}

const drivers: Driver[] = [
  { label: "Meetings load", direction: "up", severity: "high" },
  { label: "Slack activity", direction: "up", severity: "medium" },
  { label: "Context switching", direction: "up", severity: "high" },
  { label: "Deep work blocks", direction: "down", severity: "medium" },
  { label: "Sleep quality", direction: "down", severity: "low" },
  { label: "Break frequency", direction: "down", severity: "medium" },
]

const directionIcon = {
  up: ArrowUp,
  down: ArrowDown,
  stable: Minus,
}

const directionColor = {
  up: "text-destructive",
  down: "text-primary",
  stable: "text-muted-foreground",
}

const severityDot = {
  low: "bg-primary",
  medium: "bg-accent",
  high: "bg-destructive",
}

export function StressDrivers() {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="flex flex-col">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between py-1 group"
      >
        <h3 className="text-sm font-semibold text-card-foreground">Stress Drivers</h3>
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <span className="text-xs group-hover:text-card-foreground transition-colors">
            {expanded ? "Collapse" : "Why does your twin look this way?"}
          </span>
          <ChevronDown
            className={`h-4 w-4 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
          />
        </div>
      </button>

      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          expanded ? "max-h-[400px] opacity-100 mt-3" : "max-h-0 opacity-0"
        }`}
      >
        <div className="flex flex-col gap-2">
          {drivers.map((d) => {
            const Icon = directionIcon[d.direction]
            return (
              <div
                key={d.label}
                className="flex items-center gap-3 rounded-xl bg-secondary/50 px-3 py-2.5"
              >
                <div className={`h-2 w-2 shrink-0 rounded-full ${severityDot[d.severity]}`} />
                <span className="flex-1 text-sm text-card-foreground">{d.label}</span>
                <Icon className={`h-3.5 w-3.5 ${directionColor[d.direction]}`} />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
