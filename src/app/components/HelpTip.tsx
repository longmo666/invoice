import { useState, useRef, useEffect } from "react";
import { HelpCircle, X } from "lucide-react";

interface HelpTipProps {
  text: string;
}

export default function HelpTip({ text }: HelpTipProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <div className="relative inline-flex" ref={ref}>
      <button
        onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
        className="w-5 h-5 rounded-full flex items-center justify-center text-muted-foreground/60 hover:text-primary hover:bg-primary/10 transition-all duration-200"
        type="button"
      >
        <HelpCircle className="w-3.5 h-3.5" />
      </button>
      {open && (
        <div className="absolute right-0 top-7 z-50 w-56 bg-card border border-border rounded-xl shadow-xl p-3 animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="flex items-start gap-2">
            <p className="text-[12px] text-muted-foreground flex-1 leading-relaxed">{text}</p>
            <button onClick={() => setOpen(false)} className="shrink-0 p-0.5 rounded hover:bg-accent transition-colors">
              <X className="w-3 h-3 text-muted-foreground" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
