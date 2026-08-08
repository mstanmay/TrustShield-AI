import React, { useState, useEffect } from "react";
import { Sun, Moon } from "lucide-react";
import { motion } from "framer-motion";

/**
 * ThemeSwitch Primitive Component
 * Renders an animated, interactive Sun/Moon theme toggle switch.
 */
export const ThemeSwitch = ({
  iconSize = 16,
  isDark: isDarkProp,
  toggleTheme: toggleThemeProp,
  className = "",
}) => {
  const [internalDark, setInternalDark] = useState(false);

  // Sync internal state with document dark class on mount/change
  useEffect(() => {
    if (typeof window !== "undefined") {
      const isDarkMode = document.documentElement.classList.contains("dark");
      setInternalDark(isDarkMode);
    }
  }, []);

  const isDarkMode = isDarkProp !== undefined ? isDarkProp : internalDark;

  const handleToggle = () => {
    if (toggleThemeProp) {
      toggleThemeProp();
    } else if (typeof window !== "undefined") {
      const root = document.documentElement;
      if (root.classList.contains("dark")) {
        root.classList.remove("dark");
        setInternalDark(false);
      } else {
        root.classList.add("dark");
        setInternalDark(true);
      }
    }
  };

  return (
    <button
      onClick={handleToggle}
      type="button"
      role="switch"
      aria-checked={isDarkMode}
      title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
      className={`relative inline-flex items-center h-8 w-14 rounded-full p-1 transition-colors duration-300 cursor-pointer select-none border border-slate-300 dark:border-slate-700 ${
        isDarkMode ? "bg-slate-900" : "bg-slate-100"
      } ${className}`}
    >
      {/* Sliding Knob */}
      <motion.div
        layout
        transition={{ type: "spring", stiffness: 700, damping: 30 }}
        className={`flex items-center justify-center w-6 h-6 rounded-full shadow-md ${
          isDarkMode
            ? "bg-[#206a5e] text-[#a9f0e0] translate-x-6"
            : "bg-amber-400 text-slate-900 translate-x-0"
        }`}
      >
        {isDarkMode ? (
          <Moon size={iconSize} className="transition-transform duration-200" />
        ) : (
          <Sun size={iconSize} className="transition-transform duration-200" />
        )}
      </motion.div>
    </button>
  );
};

export default ThemeSwitch;
