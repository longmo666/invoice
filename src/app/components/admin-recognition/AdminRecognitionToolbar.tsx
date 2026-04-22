import { Search, RotateCcw, RefreshCw, Download, Trash2 } from 'lucide-react';
import type { AdminRecognitionTab } from './types';

interface ToolbarProps {
  tab: AdminRecognitionTab;
  keyword: string;
  filterStatus: string;
  filterType: string;
  loading: boolean;
  headerChecked: boolean;
  checkedCount: number;
  total: number;
  onKeywordChange: (v: string) => void;
  onFilterStatusChange: (v: string) => void;
  onFilterTypeChange: (v: string) => void;
  onSearch: () => void;
  onReset: () => void;
  onRefresh: () => void;
  onToggleAll: () => void;
  onBatchDelete: () => void;
  onExportCSV: () => void;
  onExportExcel: () => void;
}

export default function AdminRecognitionToolbar(props: ToolbarProps) {
  const {
    tab, keyword, filterStatus, filterType, loading, headerChecked, checkedCount, total,
    onKeywordChange, onFilterStatusChange, onFilterTypeChange,
    onSearch, onReset, onRefresh, onToggleAll, onBatchDelete, onExportCSV, onExportExcel,
  } = props;

  const placeholder = tab === 'train'
    ? '客票号 / 乘客 / 车次 / 归属账号'
    : '发票号 / 购买方 / 销售方 / 归属账号';

  return (
    <div className="px-6 py-4 border-b border-border space-y-3 bg-card/50">
      {/* Row 1: title + refresh */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-[15px]">{tab === 'train' ? '高铁票记录' : '发票记录'}（管理员）</span>
        <span className="text-[13px] text-muted-foreground">{total} 条</span>
        <div className="flex-1" />
        <button onClick={onRefresh} disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 text-[13px] border border-border rounded-lg hover:bg-accent transition-all disabled:opacity-50">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          {loading ? '加载中...' : '刷新'}
        </button>
      </div>

      {/* Row 2: filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <input value={keyword} onChange={e => onKeywordChange(e.target.value)}
          placeholder={placeholder}
          className="bg-muted/60 border border-border rounded-lg px-3 py-1.5 text-[13px] w-64 focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all" />
        {tab === 'invoice' && (
          <select value={filterType} onChange={e => onFilterTypeChange(e.target.value)}
            className="px-3 py-1.5 text-[13px] bg-muted/60 border border-border rounded-lg">
            <option value="">全部类型</option>
            <option value="vat_special">专票</option>
            <option value="vat_normal">普票</option>
          </select>
        )}
        <select value={filterStatus} onChange={e => onFilterStatusChange(e.target.value)}
          className="px-3 py-1.5 text-[13px] bg-muted/60 border border-border rounded-lg">
          <option value="">全部状态</option>
          <option value="done">已完成</option>
          <option value="processing">处理中</option>
          <option value="failed">失败</option>
        </select>
        <button onClick={onSearch} className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] bg-primary text-primary-foreground rounded-lg hover:shadow-md transition-all">
          <Search className="w-3.5 h-3.5" /> 搜索
        </button>
        <button onClick={onReset} className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] border border-border rounded-lg hover:bg-accent transition-all">
          <RotateCcw className="w-3.5 h-3.5" /> 重置
        </button>
      </div>

      {/* Row 3: batch actions */}
      <div className="flex items-center gap-2.5">
        <button onClick={onToggleAll} className="px-3 py-1.5 text-[13px] border border-border rounded-lg hover:bg-accent transition-all">
          {headerChecked ? '取消全选' : '全选'}
        </button>
        <div className="w-px h-5 bg-border" />
        <button onClick={onExportCSV} className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] border border-border rounded-lg hover:bg-accent transition-all">
          <Download className="w-3.5 h-3.5" /> CSV
        </button>
        <button onClick={onExportExcel} className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] border border-border rounded-lg hover:bg-accent transition-all">
          <Download className="w-3.5 h-3.5" /> Excel
        </button>
        {checkedCount > 0 && (
          <>
            <div className="w-px h-5 bg-border" />
            <button onClick={onBatchDelete}
              className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] border border-destructive/30 text-destructive rounded-lg hover:bg-destructive/10 transition-all">
              <Trash2 className="w-3.5 h-3.5" /> 删除({checkedCount})
            </button>
          </>
        )}
      </div>
    </div>
  );
}
