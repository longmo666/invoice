/**
 * 识别结果面板（从 UploadRecognition 拆分）
 */
import { Sparkles, FileText } from "lucide-react";
import HelpTip from "./HelpTip";
import InvoiceFieldDisplay from "./InvoiceFieldDisplay";
import type { UploadedFile } from "./recognition-upload/types";
import type { DetailedInvoiceFields } from "../../lib/helpers/recognitionResult";

interface ResultPanelProps {
  currentFile: UploadedFile | undefined;
  viewMode: "structured" | "json";
  onViewModeChange: (mode: "structured" | "json") => void;
  detailedFields: DetailedInvoiceFields | null;
  currentResultJson: string;
  invoiceType: string;
  isMobile?: boolean;
}

export default function ResultPanel({
  currentFile, viewMode, onViewModeChange,
  detailedFields, currentResultJson, invoiceType, isMobile,
}: ResultPanelProps) {
  return (
    <div className={`${isMobile ? "flex flex-col h-full" : "w-[380px] shrink-0 border-l border-border flex flex-col"} bg-card`}>
      <div className={`${isMobile ? "px-4 py-3" : "px-5 py-4"} border-b border-border`}>
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-primary" />
          <h3 className="text-[15px]">识别结果</h3>
          <div className="ml-auto">
            <HelpTip text="结构化结果将识别内容按字段分类展示，方便核对；JSON 原文展示完整的识别返回数据。" />
          </div>
        </div>
        <div className="flex items-center gap-1 bg-muted/60 rounded-xl p-1">
          <button onClick={() => onViewModeChange("structured")}
            className={`flex-1 text-[13px] py-2 rounded-lg transition-all duration-200 ${viewMode === "structured" ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}>
            结构化结果
          </button>
          <button onClick={() => onViewModeChange("json")}
            className={`flex-1 text-[13px] py-2 rounded-lg transition-all duration-200 ${viewMode === "json" ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}>
            JSON 原文
          </button>
        </div>
      </div>

      <div className={`flex-1 overflow-auto ${isMobile ? "p-4" : "p-5"}`}>
        {(!currentFile || currentFile.status !== "done") && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className={`${isMobile ? "w-14 h-14 mb-3" : "w-16 h-16 mb-4"} mx-auto rounded-2xl bg-muted flex items-center justify-center`}>
              <FileText className={`${isMobile ? "w-7 h-7" : "w-8 h-8"} text-muted-foreground/25`} />
            </div>
            <p className="text-[15px] text-muted-foreground mb-1">暂无识别结果</p>
            <p className="text-[12px] text-muted-foreground/50">完成识别后展示</p>
          </div>
        )}

        {currentFile?.status === "done" && viewMode === "json" && (
          <pre className="text-[12px] bg-muted/60 rounded-xl p-5 overflow-auto whitespace-pre-wrap break-all border border-border">{currentResultJson}</pre>
        )}

        {currentFile?.status === "done" && viewMode === "structured" && (
          <InvoiceFieldDisplay fields={detailedFields} invoiceType={invoiceType} />
        )}
      </div>
    </div>
  );
}
