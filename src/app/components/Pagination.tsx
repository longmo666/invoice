import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  page: number;
  totalPages: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  pageSizeOptions?: number[];
}

const defaultPageSizes = [10, 20, 50, 100];

export default function Pagination({
  page,
  totalPages,
  pageSize,
  total,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = defaultPageSizes,
}: PaginationProps) {
  const [jumpInput, setJumpInput] = useState("");

  const handleJump = () => {
    const target = parseInt(jumpInput, 10);
    if (!isNaN(target) && target >= 1 && target <= totalPages) {
      onPageChange(target);
    }
    setJumpInput("");
  };

  return (
    <div className="px-6 py-3 border-t border-border flex items-center justify-between flex-wrap gap-2">
      <div className="flex items-center gap-3 text-[13px] text-muted-foreground">
        <span>共 {total} 条</span>
        <div className="flex items-center gap-1.5">
          <span>每页</span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="bg-muted/60 border border-border rounded px-1.5 py-0.5 text-[13px]"
          >
            {pageSizeOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <span>条</span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page === 1}
          className="flex items-center gap-1 px-2.5 py-1 text-[13px] border border-border rounded-lg hover:bg-accent disabled:opacity-30 transition-all"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="text-[13px] text-muted-foreground">
          {page} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
          className="flex items-center gap-1 px-2.5 py-1 text-[13px] border border-border rounded-lg hover:bg-accent disabled:opacity-30 transition-all"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-1.5 text-[13px] text-muted-foreground ml-2">
          <span>跳至</span>
          <input
            value={jumpInput}
            onChange={(e) => setJumpInput(e.target.value.replace(/\D/g, ""))}
            onKeyDown={(e) => e.key === "Enter" && handleJump()}
            className="w-12 bg-muted/60 border border-border rounded px-1.5 py-0.5 text-[13px] text-center"
            placeholder={String(page)}
          />
          <span>页</span>
          <button
            onClick={handleJump}
            className="px-2 py-0.5 text-[13px] border border-border rounded hover:bg-accent transition-all"
          >
            GO
          </button>
        </div>
      </div>
    </div>
  );
}
