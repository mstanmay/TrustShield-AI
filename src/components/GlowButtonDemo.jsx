"use client";

import React from "react";
import { ArrowRight, Sparkles, Zap } from "lucide-react";
import { GlowButton } from "@/components/unlumen-ui/primitives/glow";

export const GlowButtonDemo = ({
  mode = "rotate",
  blur = "strong",
  duration = 5,
  glowScale = 1,
}) => {
  return (
    <div className="w-full max-w-4xl mx-auto py-12 px-6 space-y-12">
      {/* Demo Title Header */}
      <div className="text-center space-y-3">
        <h2 className="font-display-lg text-3xl md:text-4xl font-bold text-foreground">
          Glow Button Component
        </h2>
        <p className="text-muted-foreground font-mono text-sm max-w-xl mx-auto">
          Interactive button with multi-color rotating aura gradients and blur effects.
        </p>
      </div>

      {/* Main Glow Button Showcase */}
      <div className="flex min-h-60 flex-wrap items-center justify-center gap-8 p-10 theme-surface rounded-3xl border theme-border alpine-shadow">
        <GlowButton
          mode={mode}
          blur={blur}
          duration={duration}
          glowScale={glowScale}
          colors={["#FF5733", "#33FF57", "#3357FF", "#F1C40F"]}
        >
          Get Started
          <ArrowRight className="w-4 h-4 ml-1" />
        </GlowButton>

        <GlowButton
          mode="pulse"
          blur="medium"
          duration={3}
          glowScale={1.1}
          colors={["#206a5e", "#a9f0e0", "#326677", "#4b645e"]}
        >
          <Sparkles className="w-4 h-4 mr-1 text-[#a9f0e0]" />
          TrustShield Intelligence
        </GlowButton>

        <GlowButton
          mode="rotate"
          blur="strong"
          duration={4}
          glowScale={1}
          colors={["#8b5cf6", "#ec4899", "#3b82f6", "#10b981"]}
        >
          <Zap className="w-4 h-4 mr-1 text-amber-300" />
          Launch AI Sentinel
        </GlowButton>
      </div>
    </div>
  );
};

export default GlowButtonDemo;
