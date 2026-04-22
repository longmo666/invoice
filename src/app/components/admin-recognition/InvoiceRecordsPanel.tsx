import { Eye, Trash2 } from 'lucide-react';
import { TaskStatusBadge, ConfidenceBadge } from '../StatusBadge';
import { formatBeijingTime, mapInvoiceType } from '../../../lib/helpers/format';
import type { AdminTaskRow } from './types';

interface Props {
  tasks: AdminTaskRow[];
  headerChecked: boolean;
  onToggleAll: () => void;
  onToggleCheck: (id: number) => void;
  onViewDetail: (id: number) => void;
  onDelete: (id: number) => void;
}

export default function InvoiceRecordsPanel({ tasks, headerChecked, onToggleAll, onToggleCheck, onViewDetail, onDelete }: Props) {
  return (
    <table className="w-full">
      <thead>
        <tr className="border-b border-border bg-muted/40 sticky top-0 z-10">
          <th className="w-10 px-3 py-3"><input type="checkbox" checked={headerChecked} onChange={onToggleAll} /></th>
          {['归属账号', '发票号码', '开票日期', '购买方', '销售方', '价税合计', '可抵扣税额', '类型', '状态', '置信度', '创建时间', '操作'].map(h => (
            <th key={h} className="text-left px-3 py-3 text-[13px] text-muted-foreground whitespace-nowrap">{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {tasks.map(t => {
          const s = t.summary;
          return (
            <tr key={t.id} className="border-b border-border hover:bg-accent/40 transition-colors">
              <td className="px-3 py-3"><input type="checkbox" checked={t.checked} onChange={() => onToggleCheck(t.id)} /></td>
              <td className="px-3 py-3 text-[13px]">{t.username}</td>
              <td className="px-3 py-3 text-[13px] font-mono">{s.invoice_number || '-'}</td>
              <td className="px-3 py-3 text-[13px] text-muted-foreground">{s.invoice_date || '-'}</td>
              <td className="px-3 py-3 text-[13px] max-w-[160px] truncate">{s.buyer_name || '-'}</td>
              <td className="px-3 py-3 text-[13px] max-w-[160px] truncate">{s.seller_name || '-'}</td>
              <td className="px-3 py-3 text-[13px] text-primary">{s.total_amount || '-'}</td>
              <td className="px-3 py-3 text-[13px] text-emerald-600 dark:text-emerald-400">{s.deductible_tax || '-'}</td>
              <td className="px-3 py-3 text-[13px]">{t.invoice_type ? mapInvoiceType(t.invoice_type) : '-'}</td>
              <td className="px-3 py-3"><TaskStatusBadge status={t.status as any} /></td>
              <td className="px-3 py-3"><ConfidenceBadge score={t.confidence_score} /></td>
              <td className="px-3 py-3 text-[12px] text-muted-foreground whitespace-nowrap">{formatBeijingTime(t.created_at)}</td>
              <td className="px-3 py-3">
                <div className="flex items-center gap-1">
                  <button onClick={() => onViewDetail(t.id)} className="p-1.5 rounded-lg hover:bg-accent" title="查看详情">
                    <Eye className="w-4 h-4 text-muted-foreground" />
                  </button>
                  <button onClick={() => onDelete(t.id)} className="p-1.5 rounded-lg hover:bg-destructive/10" title="删除">
                    <Trash2 className="w-4 h-4 text-muted-foreground hover:text-destructive" />
                  </button>
                </div>
              </td>
            </tr>
          );
        })}
        {tasks.length === 0 && (
          <tr><td colSpan={13} className="text-center py-16 text-[14px] text-muted-foreground">暂无数据</td></tr>
        )}
      </tbody>
    </table>
  );
}
