"use client"

import { useEffect, useState } from "react"

export function BurnoutGauge({ risk = 22 }: { risk?: number }) {
  const [animatedRisk, setAnimatedRisk] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedRisk(risk), 500)
    return () => clearTimeout(timer)
  }, [risk])

  const riskLabel = risk <= 30 ? "Low Risk" : risk <= 60 ? "Moderate" : "High Risk"
  const riskColor =
    risk <= 30
      ? "text-primary"
      : risk <= 60
        ? "text-accent"
        : "text-destructive"

  // Gauge arc calculation
  const radius = 60
  const circumference = Math.PI * radius
  const offset = circumference - (animatedRisk / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <svg width="160" height="90" viewBox="0 0 160 90">
          {/* Background arc */}
          <path
            d="M 10 80 A 60 60 0 0 1 150 80"
            fill="none"
            stroke="hsl(var(--secondary))"
            strokeWidth="10"
            strokeLinecap="round"
          />
          {/* Filled arc */}
          <path
            d="M 10 80 A 60 60 0 0 1 150 80"
            fill="none"
            stroke={risk <= 30 ? "hsl(var(--primary))" : risk <= 60 ? "hsl(var(--accent))" : "hsl(var(--destructive))"}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${circumference}`}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
          <span className="text-3xl font-bold text-card-foreground tabular-nums">
            {animatedRisk}%
          </span>
        </div>
      </div>
      <div className="text-center">
        <p className={`text-sm font-semibold ${riskColor}`}>{riskLabel}</p>
        <p className="text-xs text-muted-foreground">Burnout Probability</p>
      </div>
    </div>
  )
}
