import React, { forwardRef } from "react";
import { cn } from "@/lib/utils";

export const Button = forwardRef(
  (
    {
      className,
      variant = "default",
      size = "default",
      children,
      ...props
    },
    ref
  ) => {
    const variants = {
      default: "bg-[#206a5e] text-white hover:bg-[#206a5e]/90 shadow-sm",
      outline: "border border-[#206a5e]/40 text-[#206a5e] dark:text-[#a9f0e0] hover:bg-[#206a5e]/10",
      ghost: "text-[#206a5e] dark:text-[#a9f0e0] hover:bg-[#206a5e]/10",
      secondary: "bg-[#cde8e1] text-[#3e5651] hover:bg-[#cde8e1]/80",
    };

    const sizes = {
      default: "px-4 py-2 text-xs font-bold rounded-xl",
      sm: "px-3 py-1.5 text-xs font-medium rounded-lg",
      lg: "px-6 py-3 text-sm font-bold rounded-xl",
      icon: "w-9 h-9 p-0 flex items-center justify-center rounded-xl",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-data-mono transition-all active:scale-[0.98] cursor-pointer disabled:opacity-50 disabled:pointer-events-none",
          variants[variant] || variants.default,
          sizes[size] || sizes.default,
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
export default Button;
