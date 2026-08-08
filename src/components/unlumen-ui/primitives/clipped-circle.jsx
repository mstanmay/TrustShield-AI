import React from "react";
import { cn } from "@/lib/utils";

/**
 * ClippedCircle Primitive Component
 * Renders an absolute positioned circular cutout backdrop/overlay for card and button containers.
 */
export const ClippedCircle = ({
  circleSize = 400,
  circleClassName = "bg-white/20",
  className = "",
  style = {},
  ...props
}) => {
  return (
    <div
      className={cn(
        "pointer-events-none absolute -bottom-1/2 -right-1/2 rounded-full opacity-40 mix-blend-soft-light transition-all duration-500 group-hover:scale-110 shrink-0",
        circleClassName,
        className
      )}
      style={{
        width: `${circleSize}px`,
        height: `${circleSize}px`,
        ...style,
      }}
      aria-hidden="true"
      {...props}
    />
  );
};

export default ClippedCircle;
