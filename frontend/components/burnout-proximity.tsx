"use client"

import { useEffect, useState } from "react"

type ProximityLevel = "Stable" | "Watch" | "Recovery recommended"

function levelFromValue(v: number): ProximityLevel {
  if (v <= 35) return "Stable"
  if (v <= 65) return "Watch"
  return "Recovery recommended"
}

const levelStyle: Record<ProximityLevel, { bar: string; text: string; bg: string }> = {
  Stable: {
    bar: "bg-primary",
    text: "text-primary",
    bg: "bg-primary/10",
  },
  Watch: {
    bar: "bg-accent",
    text: "text-accent",
    bg: "bg-accent/10",
  },
  "Recovery recommended": {
    bar: "bg-destructive",
    text: "text-destructive",
    bg: "bg-destructive/10",
  },
}

export function BurnoutProximity({ value = 28 }: { value?: number }) {
  const [animated, setAnimated] = useState(0)
  const level = levelFromValue(value)
  const style = levelStyle[level]

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(value), 400)
    return () => clearTimeout(timer)
  }, [value])

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-card-foreground">Burnout Proximity</h3>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${style.text} ${style.bg}`}>
          {level}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className={`h-full rounded-full transition-all duration-1000 ease-out ${style.bar}`}
          style={{ width: `${animated}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">
        {level === "Stable"
          ? "All signals within healthy range."
          : level === "Watch"
            ? "Some indicators elevated. Monitor closely."
            : "Multiple factors suggest immediate rest is needed."}
      </p>
    </div>
  )
}
