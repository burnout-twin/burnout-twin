"use client"

import { Brain } from "lucide-react"
import { TwinAvatar } from "@/components/twin-avatar"
import { BurnoutProximity } from "@/components/burnout-proximity"
import { StressDrivers } from "@/components/stress-drivers"
import { MicroIntervention } from "@/components/micro-intervention"

export default function Page() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card/60 backdrop-blur-sm sticky top-0 z-10">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/15">
              <Brain className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-base font-semibold text-foreground leading-tight">Digital Twin</h1>
              <p className="text-xs text-muted-foreground">Burnout Prediction System</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1.5">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
              </span>
              <span className="text-xs font-medium text-foreground">Monitoring Active</span>
            </div>
            <time className="text-xs text-muted-foreground tabular-nums" suppressHydrationWarning>
              {new Date().toLocaleDateString("en-US", {
                weekday: "long",
                month: "short",
                day: "numeric",
              })}
            </time>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl w-full px-4 py-8 flex-1">
        <div className="grid gap-6 lg:grid-cols-[1fr_1fr] items-stretch">

          {/* Left Column — The Twin */}
          <section className="flex flex-col items-center justify-center rounded-2xl bg-card border border-border shadow-sm py-12 px-6">
            <h2 className="sr-only">State at a Glance</h2>
            <TwinAvatar band="Focused" />
          </section>

          {/* Right Column — Metrics & Intervention */}
          <div className="flex flex-col gap-6">
            {/* Burnout Proximity + Stress Drivers */}
            <section className="rounded-2xl bg-card border border-border shadow-sm p-6 flex flex-col gap-5">
              <BurnoutProximity value={28} />
              <div className="border-t border-border pt-4">
                <StressDrivers />
              </div>
            </section>

            {/* Micro-Intervention */}
            <section className="rounded-2xl bg-card border border-border shadow-sm p-6 flex flex-col gap-4">
              <h3 className="text-sm font-semibold text-card-foreground">Suggested Micro-Intervention!</h3>
              <MicroIntervention />
            </section>
          </div>

        </div>
      </main>
    </div>
  )
}
