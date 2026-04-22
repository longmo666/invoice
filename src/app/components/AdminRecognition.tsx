import { useLocation, useNavigate } from 'react-router';
import { useMemo } from 'react';
import { FileText, TrainFront } from 'lucide-react';
import { useAdminRecognition } from './admin-recognition/useAdminRecognition';
import AdminRecognitionToolbar from './admin-recognition/AdminRecognitionToolbar';
import InvoiceRecordsPanel from './admin-recognition/InvoiceRecordsPanel';
import TrainRecordsPanel from './admin-recognition/TrainRecordsPanel';
import AdminRecognitionDetailModal from './admin-recognition/AdminRecognitionDetailModal';
import Pagination from './Pagination';
import type { AdminRecognitionTab } from './admin-recognition/types';

const tabs: { key: AdminRecognitionTab; label: string; icon: typeof FileText }[] = [
  { key: 'invoice', label: '普通发票', icon: FileText },
  { key: 'train', label: '高铁票', icon: TrainFront },
];

export default function AdminRecognition() {
  const location = useLocation();
  const navigate = useNavigate();

  const tab: AdminRecognitionTab = useMemo(() => {
    if (location.pathname.includes('/recognition/train')) return 'train';
    return 'invoice';
  }, [location.pathname]);

  const state = useAdminRecognition(tab);

  const switchTab = (t: AdminRecognitionTab) => {
    navigate(`/admin/recognition/${t}`);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Tab bar */}
      <div className="flex border-b border-border bg-card/50 px-6">
        {tabs.map(t => {
          const active = tab === t.key;
          return (
            <button key={t.key} onClick={() => switchTab(t.key)}
              className={`flex items-center gap-2 px-5 py-3 text-[14px] border-b-2 transition-all ${
                active ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}>
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Toolbar */}
      <AdminRecognitionToolbar
        tab={tab}
        keyword={state.keyword}
        filterStatus={state.filterStatus}
        filterType={state.filterType}
        loading={state.loading}
        headerChecked={state.headerChecked}
        checkedCount={state.checkedCount}
        total={state.total}
        onKeywordChange={state.setKeyword}
        onFilterStatusChange={state.setFilterStatus}
        onFilterTypeChange={state.setFilterType}
        onSearch={state.handleSearch}
        onReset={state.handleReset}
        onRefresh={state.loadTasks}
        onToggleAll={state.toggleAll}
        onBatchDelete={state.handleBatchDelete}
        onExportCSV={state.handleExportCSV}
        onExportExcel={state.handleExportExcel}
      />

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {tab === 'invoice' ? (
          <InvoiceRecordsPanel
            tasks={state.tasks}
            headerChecked={state.headerChecked}
            onToggleAll={state.toggleAll}
            onToggleCheck={state.toggleCheck}
            onViewDetail={state.handleViewDetail}
            onDelete={state.handleDelete}
          />
        ) : (
          <TrainRecordsPanel
            tasks={state.tasks}
            headerChecked={state.headerChecked}
            onToggleAll={state.toggleAll}
            onToggleCheck={state.toggleCheck}
            onViewDetail={state.handleViewDetail}
            onDelete={state.handleDelete}
          />
        )}
      </div>

      {/* Pagination */}
      <div className="shrink-0 border-t border-border bg-card/50 px-6 py-3">
        <Pagination
          page={state.page}
          totalPages={state.totalPages}
          pageSize={state.pageSize}
          total={state.total}
          onPageChange={state.setPage}
          onPageSizeChange={state.setPageSize}
        />
      </div>

      {/* Detail Modal */}
      <AdminRecognitionDetailModal
        selectedTask={state.selectedTask}
        taskDetail={state.taskDetail}
        loadingDetail={state.loadingDetail}
        onClose={state.closeDetail}
      />
    </div>
  );
}
