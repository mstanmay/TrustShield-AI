"use client";

import React from "react";
import { ClippedCircle } from "@/components/unlumen-ui/primitives/clipped-circle";
import { Button } from "@/components/ui/button";

export function ClippedCircleDemo({
  circleSize = 400,
}) {
  const actions = [
    { label: "Docs", variant: "default" },
    { label: "Install", variant: "outline" },
    { label: "Components", variant: "ghost" },
  ];

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-5 p-6">
      <div className="grid grid-cols-3 gap-3">
        {actions.map(({ label, variant }) => (
          <Button
            key={label}
            variant={variant}
            size="sm"
            className="relative overflow-hidden group"
          >
            {label}
            <ClippedCircle circleSize={260} circleClassName="bg-white/40" />
          </Button>
        ))}
      </div>

      <div className="relative min-h-75 overflow-hidden rounded-2xl border border-border/70 theme-surface p-8 shadow-sm group">
        <div className="flex h-full min-h-59 items-center justify-center rounded-xl border border-border/60 theme-surface-low p-10 shadow-inner">
          <div className="text-center space-y-2">
            <h4 className="font-display-lg text-2xl font-bold text-[#206a5e]">TrustShield UI</h4>
            <p className="font-data-mono text-xs theme-text-muted uppercase">SURVEILLANCE DESIGN SYSTEM</p>
          </div>
        </div>
        <ClippedCircle circleSize={circleSize} circleClassName="bg-[#206a5e]/20" />
      </div>
    </div>
  );
}

export default ClippedCircleDemo;
