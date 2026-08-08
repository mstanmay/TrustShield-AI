import React, { createContext, useContext, useState, useId } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

const HighlightContext = createContext(null);

export const Highlight = ({
  children,
  mode = "parent",
  hover = true,
  defaultValue,
  value: controlledValue,
  onChange,
  className = "",
  containerClassName = "",
  layoutId: customLayoutId,
  ...props
}) => {
  const generatedId = useId();
  const layoutId = customLayoutId || `highlight-${generatedId}`;
  
  const [internalValue, setInternalValue] = useState(defaultValue);
  const [hoveredValue, setHoveredValue] = useState(null);

  const activeValue = controlledValue !== undefined ? controlledValue : internalValue;

  const handleSelect = (val) => {
    if (controlledValue === undefined) {
      setInternalValue(val);
    }
    onChange?.(val);
  };

  return (
    <HighlightContext.Provider
      value={{
        activeValue,
        setActiveValue: handleSelect,
        hoveredValue,
        setHoveredValue,
        hover,
        mode,
        layoutId,
        highlightClassName: className,
      }}
    >
      <div className={cn("relative flex items-center", containerClassName)} {...props}>
        {children}
      </div>
    </HighlightContext.Provider>
  );
};

export const HighlightItem = ({
  children,
  value,
  className = "",
  onClick,
  onMouseEnter,
  onMouseLeave,
  ...props
}) => {
  const ctx = useContext(HighlightContext);

  if (!ctx) {
    throw new Error("HighlightItem must be used within a Highlight component");
  }

  const {
    activeValue,
    setActiveValue,
    hoveredValue,
    setHoveredValue,
    hover,
    layoutId,
    highlightClassName,
  } = ctx;

  const isCurrentActive = hover ? (hoveredValue !== null ? hoveredValue === value : activeValue === value) : activeValue === value;
  const isSelectedTab = activeValue === value;

  const handleClick = (e) => {
    setActiveValue(value);
    onClick?.(e);
  };

  const handleMouseEnter = (e) => {
    if (hover) {
      setHoveredValue(value);
    }
    onMouseEnter?.(e);
  };

  const handleMouseLeave = (e) => {
    if (hover) {
      setHoveredValue(null);
    }
    onMouseLeave?.(e);
  };

  return (
    <div
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={cn(
        "relative z-10 transition-colors duration-200 select-none cursor-pointer flex items-center justify-center",
        isSelectedTab ? "text-white font-bold" : "theme-text-muted hover:theme-text",
        className
      )}
      {...props}
    >
      {isCurrentActive && (
        <motion.div
          layoutId={layoutId}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{
            type: "spring",
            stiffness: 500,
            damping: 35,
          }}
          className={cn(
            "absolute inset-0 z-[-1] rounded-lg bg-[#206a5e] shadow-md border border-[#a9f0e0]/40 pointer-events-none",
            highlightClassName
          )}
        />
      )}
      <span className="relative z-10">{children}</span>
    </div>
  );
};

export default Highlight;
