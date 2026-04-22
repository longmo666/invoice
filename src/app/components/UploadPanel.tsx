/**
 * 上传面板 + 文件列表（含分页）
 */
import {
  Upload,
  FileUp,
  Trash2,
  Download,
  Loader2,
  FileImage,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CloudUpload,
} from "lucide-react";
import HelpTip from "./HelpTip";
import type { RecognitionMode } from "../../lib/services/recognition";
import type { UploadedFile } from "./recognition-upload/types";
import { statusConfig } from "./recognition-upload/types";

interface UploadPanelProps {
  files: UploadedFile[];
  currentFileId: number | null;
  isTrainTicket: boolean;
  recognitionMode: RecognitionMode;
  restoring: boolean;
  uploading: boolean;
  selectedFiles: File[];
  page: number;
  totalPages: number;
  total: number;
  onPageChange: (page: number) => void;
  onRecognitionModeChange: (mode: RecognitionMode) => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onUpload: () => void;
  onExportCSV: () => void;
  onExportExcel: () => void;
  onSelectAll: () => void;
  onBatchDelete: () => void;
  onFileClick: (fileId: number) => void;
  onFileToggle: (fileId: number) => void;
  onFileRemove: (fileId: number) => void;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  isMobile?: boolean;
}

export default function UploadPanel({
  files, currentFileId, isTrainTicket, recognitionMode, restoring, uploading, selectedFiles,
  page, totalPages, total, onPageChange,
  onRecognitionModeChange, onFileSelect, onUpload, onExportCSV, onExportExcel,
  onSelectAll, onBatchDelete, onFileClick, onFileToggle, onFileRemove, fileInputRef,
  isMobile,
}: UploadPanelProps) {
  const selectableFiles = files.filter(
    (f) => f.status !== "uploading" && f.status !== "queued" && f.status !== "processing"
  );
  const allSelected = selectableFiles.length > 0 && selectableFiles.every((f) => f.selected);

  const fileNameDisplay =
    selectedFiles.length === 0
      ? null
      : selectedFiles.length === 1
      ? selectedFiles[0].name
      : `${selectedFiles[0].name} 等 ${selectedFiles.length} 个文件`;

  return (
    <div className={`${isMobile ? "flex flex-col h-full" : "w-80 shrink-0 border-r border-border flex flex-col"} bg-card`}>
      <div className={`${isMobile ? "p-4" : "p-5"} border-b border-border space-y-4`}>
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
            <CloudUpload className="w-4 h-4 text-primary" />
          </div>
          <h3 className="text-[15px]">上传文件</h3>
          <span className="ml-auto text-[11px] text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
            {isTrainTicket ? "高铁票" : "普通发票"}
          </span>
        </div>

        <div
          role="button"
          tabIndex={0}
          onClick={(e) => { e.stopPropagation(); if (!uploading) fileInputRef.current?.click(); }}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (!uploading) fileInputRef.current?.click(); } }}
          className={`group w-full border-2 border-dashed border-border rounded-xl ${isMobile ? "p-4" : "p-5"} text-center hover:border-primary/50 hover:bg-primary/[0.03] transition-all duration-200 cursor-pointer ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className={`${isMobile ? "w-10 h-10 mb-2" : "w-12 h-12 mb-3"} mx-auto rounded-xl bg-muted group-hover:bg-primary/10 transition-colors flex items-center justify-center`}>
            <FileUp className={`${isMobile ? "w-5 h-5" : "w-6 h-6"} text-muted-foreground group-hover:text-primary transition-colors`} />
          </div>
          {fileNameDisplay ? (
            <p className="text-[13px] text-foreground truncate">{fileNameDisplay}</p>
          ) : (
            <>
              <p className="text-[14px] text-foreground mb-1">点击选择文件</p>
              <p className="text-[12px] text-muted-foreground">支持图片、PDF、XML、OFD，可批量</p>
            </>
          )}
        </div>

        <div>
          <div className="flex items-center gap-1.5 mb-1.5">
            <label className="text-[12px] text-muted-foreground">识别模式</label>
            <HelpTip text="纯 AI 识别：使用 AI 模型识别发票内容，准确率高。混合模式和纯本地 OCR 暂未开放。" />
          </div>
          <div className="relative">
            <select value={recognitionMode} onChange={(e) => onRecognitionModeChange(e.target.value as RecognitionMode)}
              className="w-full appearance-none bg-muted/60 border border-border rounded-lg px-3 py-2 text-[13px] pr-8 focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all">
              <option value="ai">纯 AI 识别</option>
              <option value="hybrid" disabled>混合模式（本地 + AI）</option>
              <option value="local_ocr" disabled>纯本地 OCR</option>
            </select>
            <ChevronDown className="w-4 h-4 absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          </div>
        </div>

        <button type="button" onClick={onUpload} disabled={uploading || selectedFiles.length === 0}
          className="w-full flex items-center justify-center gap-2.5 bg-gradient-to-r from-primary to-indigo-600 text-white rounded-xl px-4 py-3 text-[15px] hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-px active:translate-y-0 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0">
          {uploading ? <><Loader2 className="w-5 h-5 animate-spin" /> 上传中...</> : <><Upload className="w-5 h-5" /> 上传文件</>}
        </button>

        <div className="flex gap-2">
          <div className="flex-1 relative">
            <button onClick={onExportCSV} disabled={files.length === 0 || !files.some(f => f.selected && f.status === "done")}
              className="w-full flex items-center justify-center gap-1.5 border border-border rounded-lg px-3 py-2 text-[13px] text-muted-foreground hover:bg-accent hover:text-foreground transition-all disabled:opacity-35">
              <Download className="w-3.5 h-3.5" /> 导出 CSV
            </button>
          </div>
          <div className="flex-1 relative">
            <button onClick={onExportExcel} disabled={files.length === 0 || !files.some(f => f.selected && f.status === "done")}
              className="w-full flex items-center justify-center gap-1.5 border border-border rounded-lg px-3 py-2 text-[13px] text-muted-foreground hover:bg-accent hover:text-foreground transition-all disabled:opacity-35">
              <Download className="w-3.5 h-3.5" /> 导出 Excel
            </button>
          </div>
          <HelpTip text="将已完成识别的结果导出为 CSV 或 Excel 表格，方便对接财务系统。" />
        </div>
      </div>

      {/* File list */}
      <div className="flex-1 overflow-auto">
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[14px]">文件列表</h3>
            <span className="text-[12px] text-muted-foreground bg-muted px-2.5 py-0.5 rounded-full">{total} 个</span>
          </div>
          {files.length === 0 && (
            restoring ? (
              <div className="text-center py-12">
                <Loader2 className="w-6 h-6 mx-auto mb-2 text-muted-foreground animate-spin" />
                <p className="text-[13px] text-muted-foreground">恢复任务列表...</p>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-muted flex items-center justify-center">
                  <FileImage className="w-7 h-7 text-muted-foreground/40" />
                </div>
                <p className="text-[14px] text-muted-foreground">暂无文件</p>
                <p className="text-[12px] text-muted-foreground/60 mt-1">请先选择并上传</p>
              </div>
            )
          )}
          <div className="space-y-1.5">
            {files.map((file) => {
              const sc = statusConfig[file.status];
              const Icon = sc.icon;
              const isActive = currentFileId === file.id;
              const canSelect = file.status !== "queued" && file.status !== "processing";
              return (
                <div key={file.id}
                  className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 ${isActive ? "bg-primary/8 ring-1 ring-primary/20" : "hover:bg-accent"}`}
                  onClick={(e) => { e.stopPropagation(); onFileClick(file.id); }}>
                  <input type="checkbox" checked={file.selected} disabled={!canSelect}
                    onChange={(e) => { e.stopPropagation(); onFileToggle(file.id); }}
                    onClick={(e) => e.stopPropagation()}
                    className="shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] truncate">{file.name}</p>
                    <span className={`inline-flex items-center gap-1 text-[11px] mt-0.5 ${sc.color}`}>
                      {Icon && <Icon className={`w-3 h-3 ${file.status === "processing" ? "animate-spin" : ""}`} />}
                      {sc.label}
                    </span>
                  </div>
                  {isMobile ? (
                    <button disabled={!canSelect}
                      onClick={(e) => { e.stopPropagation(); onFileRemove(file.id); }}
                      className="p-1 rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-all disabled:hidden">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  ) : (
                    <button disabled={!canSelect}
                      onClick={(e) => { e.stopPropagation(); onFileRemove(file.id); }}
                      className="opacity-0 group-hover:opacity-100 p-1 rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-all disabled:hidden">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Pagination + actions */}
      {files.length > 0 && (
        <div className="border-t border-border">
          {/* 分页控件 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <button
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1}
                className="p-1.5 rounded-lg hover:bg-accent disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-[12px] text-muted-foreground tabular-nums">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => onPageChange(page + 1)}
                disabled={page >= totalPages}
                className="p-1.5 rounded-lg hover:bg-accent disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
          {/* 全选 / 批量删除 */}
          <div className="p-4 flex gap-2">
            <button onClick={onSelectAll}
              className="flex-1 text-[13px] border border-border rounded-lg py-2 hover:bg-accent transition-all">
              {allSelected ? "取消全选" : "全选"}
            </button>
            <button onClick={onBatchDelete} disabled={!files.some((f) => f.selected)}
              className="flex-1 text-[13px] border border-destructive/30 text-destructive rounded-lg py-2 hover:bg-destructive/10 transition-all disabled:opacity-35">
              批量删除
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
