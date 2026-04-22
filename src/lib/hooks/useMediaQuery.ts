import { useState, useEffect } from "react";

/**
 * 响应式断点 hook
 * 与 Tailwind 断点保持一致: md = 768px, lg = 1024px
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window !== "undefined") {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    const mql = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    mql.addEventListener("change", handler);
    setMatches(mql.matches);
    return () => mql.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

/** 是否为移动端 (< 768px) */
export function useIsMobile(): boolean {
  return !useMediaQuery("(min-width: 768px)");
}

/** 是否为平板及以上 (>= 768px) */
export function useIsTablet(): boolean {
  return useMediaQuery("(min-width: 768px)");
}

/** 是否为桌面端 (>= 1024px) */
export function useIsDesktop(): boolean {
  return useMediaQuery("(min-width: 1024px)");
}
