import React from "react";

/**
 * GlowButton Primitive Component
 * Renders a premium interactive button surrounded by an animated multi-color glowing aura.
 */
export const GlowButton = ({
  children,
  mode = "rotate",
  blur = "strong",
  duration = 5,
  glowScale = 1,
  colors = ["#206a5e", "#a9f0e0", "#326677", "#4b645e"],
  className = "",
  glowClassName = "",
  onClick,
  ...props
}) => {
  // Map blur prop to pixel values
  const blurMap = {
    soft: "blur-md",
    medium: "blur-xl",
    strong: "blur-2xl",
  };
  const blurClass = blurMap[blur] || (blur.includes("blur") ? blur : "blur-xl");

  // Format color array into CSS gradient string
  const gradientColors = Array.isArray(colors) && colors.length > 0
    ? colors.join(", ")
    : "#206a5e, #a9f0e0, #326677, #4b645e";

  const isRotate = mode === "rotate";
  const isPulse = mode === "pulse";

  return (
    <div className="relative inline-flex items-center justify-center group">
      {/* Animated Glowing Aura Background */}
      <div
        className={`absolute -inset-1 rounded-2xl opacity-75 group-hover:opacity-100 transition duration-500 ${blurClass} ${
          isRotate ? "animate-spin-slow" : ""
        } ${isPulse ? "animate-pulse" : ""} ${glowClassName}`}
        style={{
          background: `conic-gradient(from 0deg, ${gradientColors}, ${colors[0] || "#206a5e"})`,
          animationDuration: `${duration}s`,
          transform: `scale(${glowScale})`,
        }}
      />

      {/* Button Content */}
      <button
        onClick={onClick}
        className={`relative z-10 inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-display-lg font-bold text-white bg-slate-900/90 dark:bg-slate-950/90 backdrop-blur-md border border-white/20 hover:border-white/40 shadow-xl transition-all duration-300 active:scale-[0.97] cursor-pointer ${className}`}
        {...props}
      >
        {children}
      </button>
    </div>
  );
};

export default GlowButton;
