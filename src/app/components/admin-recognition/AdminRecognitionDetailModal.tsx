import { X } from 'lucide-react';
import type { RecognitionTaskDetail } from '../../../lib/types/recognition';
import type { AdminTaskRow } from './types';
import { getBestResultItem, extractDetailedFields } from '../../../lib/helpers/recognitionResult';
import InvoiceFieldDisplay from '../InvoiceFieldDisplay';

interface Props {
  selectedTask: AdminTaskRow | null;
  taskDetail: RecognitionTaskDetail | null;
  loadingDetail: boolean;
  onClose: () => void;
}

export default function AdminRecognitionDetailModal({ selectedTask, taskDetail, loadingDetail, onClose }: Props) {
  if (!selectedTask) return null;

  const bestItem = taskDetail?.items ? getBestResultItem(taskDetail.items) : null;
  const detailedFields = extractDetailedFields(bestItem);
  const invoiceType = selectedTask.invoice_type || 'vat_normal';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="bg-card rounded-2xl border border-border shadow-2xl w-[90vw] max-w-[700px] max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 className="text-[16px]">任务详情 · {selectedTask.original_filename}</h3>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-accent"><X className="w-5 h-5" /></button>
        </div>
        <div className="flex-1 overflow-auto px-6 py-5">
          {loadingDetail ? (
            <div className="flex items-center justify-center py-16">
              <div className="w-8 h-8 border-3 border-primary/30 border-t-primary rounded-full animate-spin" />
            </div>
          ) : detailedFields ? (
            <InvoiceFieldDisplay fields={detailedFields} invoiceType={invoiceType} />
          ) : (
            <div className="text-center py-16 text-[14px] text-muted-foreground">暂无识别结果</div>
          )}
        </div>
      </div>
    </div>
  );
}
