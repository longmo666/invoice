/**
 * 上传识别 — 纯壳组件
 * 所有状态与副作用委托给 useRecognitionWorkspace
 * 本文件只做：Outlet context → hook → 布局
 */
import { useOutletContext } from "react-router";
import { Upload, Eye, Sparkles } from "lucide-react";
import { useRecognitionWorkspace } from "./recognition-upload/useRecognitionWorkspace";
import UploadPanel from "./UploadPanel";
import PreviewPanel from "./PreviewPanel";
import ResultPanel from "./ResultPanel";

const mobileTabs = [
  { key: "upload" as const, label: "上传", icon: Upload },
  { key: "preview" as const, label: "预览", icon: Eye },
  { key: "result" as const, label: "结果", icon: Sparkles },
];

export default function UploadRecognition() {
  const { activeMenu, isMobile } = useOutletContext<{ activeMenu: string; isMobile: boolean }>();
  const ws = useRecognitionWorkspace(activeMenu);

  const panelProps = {
    files: ws.files,
    currentFileId: ws.currentFileId,
    isTrainTicket: ws.isTrainTicket,
    recognitionMode: ws.recognitionMode,
    restoring: ws.restoring,
    uploading: ws.uploading,
    selectedFiles: ws.selectedFiles,
    page: ws.page,
    totalPages: ws.totalPages,
    total: ws.total,
    onPageChange: ws.onPageChange,
    onRecognitionModeChange: ws.setRecognitionMode,
    onFileSelect: ws.handleFileSelect,
    onUpload: ws.handleUpload,
    onExportCSV: ws.handleExportCSV,
    onExportExcel: ws.handleExportExcel,
    onSelectAll: ws.handleSelectAll,
    onBatchDelete: ws.handleBatchDelete,
    onFileClick: ws.handleFileClick,
    onFileToggle: ws.handleFileToggle,
    onFileRemove: ws.handleFileRemove,
    fileInputRef: ws.fileInputRef,
  };

  if (isMobile) {
    return (
      <div className="flex flex-col h-full">
        <input ref={ws.fileInputRef} type="file" multiple accept="image/*,.pdf,.xml,.ofd"
          style={{ display: 'none', position: 'absolute', pointerEvents: 'none' }}
          onChange={ws.handleFileSelect} />

        <div className="shrink-0 flex border-b border-border bg-card">
          {mobileTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => ws.setMobileTab(tab.key)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-3 text-[13px] border-b-2 transition-all ${
                ws.mobileTab === tab.key
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground"
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-auto">
          {ws.mobileTab === "upload" && <UploadPanel {...panelProps} isMobile />}
          {ws.mobileTab === "preview" && (
            <PreviewPanel files={ws.files} currentFile={ws.currentFile} onRetryFailed={ws.handleRetryFailed} isMobile />
          )}
          {ws.mobileTab === "result" && (
            <ResultPanel
              currentFile={ws.currentFile} viewMode={ws.viewMode} onViewModeChange={ws.setViewMode}
              detailedFields={ws.detailedFields} currentResultJson={ws.currentResultJson}
              invoiceType={ws.invoiceType} isMobile
            />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      <input ref={ws.fileInputRef} type="file" multiple accept="image/*,.pdf,.xml,.ofd"
        style={{ display: 'none', position: 'absolute', pointerEvents: 'none' }}
        onChange={ws.handleFileSelect} />

      <UploadPanel {...panelProps} />

      <PreviewPanel files={ws.files} currentFile={ws.currentFile} onRetryFailed={ws.handleRetryFailed} />

      <ResultPanel
        currentFile={ws.currentFile} viewMode={ws.viewMode} onViewModeChange={ws.setViewMode}
        detailedFields={ws.detailedFields} currentResultJson={ws.currentResultJson}
        invoiceType={ws.invoiceType}
      />
    </div>
  );
}
