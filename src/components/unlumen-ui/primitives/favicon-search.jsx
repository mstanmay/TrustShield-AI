import React, { useState, useEffect, useRef, forwardRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

function extractDomain(input) {
  if (!input || !input.trim()) return null;
  try {
    const raw = input.includes("://") ? input : `https://${input}`;
    const url = new URL(raw);
    const host = url.hostname.replace(/^www\./, "");
    if (host.includes(".") && host.split(".").every(Boolean)) return host;
    return null;
  } catch {
    const cleaned = input.trim().replace(/^www\./, "");
    if (cleaned.includes(".") && cleaned.split(".").every(Boolean))
      return cleaned;
    return null;
  }
}

function getFaviconUrl(domain, size = 64) {
  return `https://www.google.com/s2/favicons?domain=${encodeURIComponent(domain)}&sz=${size}`;
}

const FaviconSearch = forwardRef(
  (
    {
      value: controlledValue,
      defaultValue = "",
      onChange,
      onSearch,
      placeholder = "Enter website URL or ticker...",
      clearable = true,
      faviconSize = 64,
      debounce = 350,
      className,
      inputClassName,
      ...props
    },
    ref
  ) => {
    const isControlled = controlledValue !== undefined;
    const [internalValue, setInternalValue] = useState(defaultValue);
    const value = isControlled ? controlledValue : internalValue;

    const [domain, setDomain] = useState(null);
    const [faviconReady, setFaviconReady] = useState(false);
    const [faviconError, setFaviconError] = useState(false);
    const prevDomainRef = useRef(null);

    useEffect(() => {
      const id = setTimeout(() => {
        const d = extractDomain(value);
        if (d !== prevDomainRef.current) {
          prevDomainRef.current = d;
          setFaviconReady(false);
          setFaviconError(false);
          setDomain(d);
        }
      }, debounce);
      return () => clearTimeout(id);
    }, [value, debounce]);

    const handleChange = (e) => {
      const v = e.target.value;
      if (!isControlled) setInternalValue(v);
      onChange?.(v);
    };

    const handleKeyDown = (e) => {
      if (e.key === "Enter") {
        onSearch?.(value, domain);
      }
    };

    const handleClear = () => {
      if (!isControlled) setInternalValue("");
      onChange?.("");
      setDomain(null);
      setFaviconReady(false);
      setFaviconError(false);
      prevDomainRef.current = null;
    };

    const showFavicon = domain && faviconReady && !faviconError;

    return (
      <div
        className={cn(
          "relative flex items-center w-full max-w-md group",
          className
        )}
      >
        <div className="pointer-events-none absolute left-3.5 flex items-center justify-center w-5 h-5 z-10">
          <AnimatePresence mode="wait">
            {showFavicon ? (
              <motion.img
                key={`favicon-${domain}`}
                src={getFaviconUrl(domain, faviconSize)}
                alt={domain}
                width={20}
                height={20}
                className="w-5 h-5 rounded-sm object-contain"
                initial={{ opacity: 0, scale: 0.5, filter: "blur(4px)" }}
                animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, scale: 0.5, filter: "blur(4px)" }}
                transition={{ type: "spring", stiffness: 400, damping: 28 }}
                onLoad={() => setFaviconReady(true)}
                onError={() => setFaviconError(true)}
              />
            ) : (
              <motion.span
                key="search-icon"
                initial={{ opacity: 0, scale: 0.7 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.7 }}
                transition={{ type: "spring", stiffness: 400, damping: 28 }}
                className="flex items-center justify-center text-muted-foreground"
              >
                {domain && !faviconError ? (
                  <Globe className="w-4.5 h-4.5" />
                ) : (
                  <Search className="w-4.5 h-4.5" />
                )}
              </motion.span>
            )}
          </AnimatePresence>

          {/* Preload img to detect load/error before showing the animated favicon */}
          {domain && !faviconReady && !faviconError && (
            <img
              src={getFaviconUrl(domain, faviconSize)}
              alt=""
              className="sr-only absolute"
              onLoad={() => setFaviconReady(true)}
              onError={() => setFaviconError(true)}
              aria-hidden
            />
          )}
        </div>

        <input
          ref={ref}
          type="text"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn(
            "flex w-full rounded-xl border border-border theme-surface-low",
            "pl-10 pr-10 py-2.5 text-xs text-foreground font-data-mono",
            "placeholder:text-muted-foreground",
            "outline-none",
            "transition-all duration-200",
            "focus:border-[#206a5e] focus:ring-1 focus:ring-[#206a5e]",
            "hover:border-muted-foreground/50",
            inputClassName
          )}
          {...props}
        />

        <AnimatePresence>
          {clearable && value && value.length > 0 && (
            <motion.button
              type="button"
              onClick={handleClear}
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.7 }}
              transition={{ type: "spring", stiffness: 400, damping: 28 }}
              className={cn(
                "absolute right-3 flex items-center justify-center z-10 cursor-pointer",
                "w-5 h-5 rounded-full text-muted-foreground",
                "hover:text-foreground hover:bg-muted transition-colors"
              )}
              aria-label="Clear input"
            >
              <X className="w-3.5 h-3.5" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

FaviconSearch.displayName = "FaviconSearch";

export { FaviconSearch, extractDomain, getFaviconUrl };
export default FaviconSearch;
