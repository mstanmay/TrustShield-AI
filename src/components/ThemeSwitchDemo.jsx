"use client";

import React from "react";
import { ThemeSwitch } from "@/components/unlumen-ui/primitives/theme-switch";

export const ThemeSwitchDemo = ({ iconSize = 16 }) => {
  return (
    <div className="flex items-center justify-center gap-4 p-8">
      <ThemeSwitch iconSize={iconSize} />
    </div>
  );
};

export default ThemeSwitchDemo;
