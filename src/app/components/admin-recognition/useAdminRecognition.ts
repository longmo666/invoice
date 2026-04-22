import { useState, useEffect, useCallback } from 'react';
import { recognitionService } from '../../../lib/services/recognition';
import type { RecognitionTaskDetail } from '../../../lib/types/recognition';
import type { AdminRecognitionTab, AdminTaskRow, TaskStatus, InvoiceType } from './types';

const DEFAULT_PAGE_SIZE = 10;

export function useAdminRecognition(tab: AdminRecognitionTab) {
  const [tasks, setTasks] = useState<AdminTaskRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [total, setTotal] = useState(0);
  const [keyword, setKeyword] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterType, setFilterType] = useState<string>('');

  // 详情弹窗
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [taskDetail, setTaskDetail] = useState<RecognitionTaskDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const totalPages = Math.ceil(total / pageSize) || 1;
  const checkedCount = tasks.filter(t => t.checked).length;
  const headerChecked = tasks.length > 0 && tasks.every(t => t.checked);
  const selectedTask = tasks.find(t => t.id === selectedTaskId) || null;

  const loadTasks = useCallback(async () => {
    setLoading(true);
    try {
      const response = await recognitionService.adminGetTasksPaginated({
        tab,
        invoiceType: (filterType || undefined) as InvoiceType | undefined,
        status: (filterStatus || undefined) as TaskStatus | undefined,
        keyword: keyword || undefined,
        page,
        pageSize,
      });
      if (response.success && response.data) {
        setTasks(response.data.items.map(item => ({ ...item, checked: false })));
        setTotal(response.data.total);
      }
    } catch (error) {
      console.error('Load admin tasks error:', error);
    } finally {
      setLoading(false);
    }
  }, [tab, filterType, filterStatus, keyword, page, pageSize]);

  useEffect(() => {
    setPage(1);
    setKeyword('');
    setFilterStatus('');
    setFilterType('');
  }, [tab]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleViewDetail = async (taskId: number) => {
    setSelectedTaskId(taskId);
    setTaskDetail(null);
    setLoadingDetail(true);
    try {
      const response = await recognitionService.adminGetTaskDetail(taskId);
      if (response.success && response.data) {
        setTaskDetail(response.data);
      }
    } catch (error) {
      console.error('Load task detail error:', error);
    } finally {
      setLoadingDetail(false);
    }
  };

  const closeDetail = () => {
    setSelectedTaskId(null);
    setTaskDetail(null);
  };

  const handleDelete = async (taskId: number) => {
    if (!confirm('确定要物理删除该任务？此操作不可恢复。')) return;
    try {
      await recognitionService.adminDeleteTasks([taskId]);
      setTasks(prev => prev.filter(t => t.id !== taskId));
      setTotal(prev => prev - 1);
    } catch {
      alert('删除失败');
    }
  };

  const handleBatchDelete = async () => {
    const ids = tasks.filter(t => t.checked).map(t => t.id);
    if (ids.length === 0) return;
    if (!confirm(`确定要物理删除选中的 ${ids.length} 条任务？`)) return;
    try {
      await recognitionService.adminDeleteTasks(ids);
      setTasks(prev => prev.filter(t => !ids.includes(t.id)));
      setTotal(prev => prev - ids.length);
    } catch {
      alert('批量删除失败');
    }
  };

  const handleExportCSV = async () => {
    const selected = tasks.filter(t => t.checked && t.status === 'done');
    if (selected.length === 0) { alert('请先勾选已完成的任务'); return; }
    for (const t of selected) {
      try { await recognitionService.adminExportToCsv(t.id); } catch { alert(`导出任务 ${t.id} 失败`); }
    }
  };

  const handleExportExcel = async () => {
    const selected = tasks.filter(t => t.checked && t.status === 'done');
    if (selected.length === 0) { alert('请先勾选已完成的任务'); return; }
    for (const t of selected) {
      try { await recognitionService.adminExportToExcel(t.id); } catch { alert(`导出任务 ${t.id} 失败`); }
    }
  };

  const toggleAll = () => {
    const target = !headerChecked;
    setTasks(prev => prev.map(t => ({ ...t, checked: target })));
  };

  const toggleCheck = (taskId: number) => {
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, checked: !t.checked } : t));
  };

  const handleSearch = () => { setPage(1); };
  const handleReset = () => { setKeyword(''); setFilterStatus(''); setFilterType(''); setPage(1); };

  return {
    // state
    tasks, loading, page, pageSize, total, totalPages, keyword, filterStatus, filterType,
    checkedCount, headerChecked, selectedTask, taskDetail, loadingDetail,
    // actions
    loadTasks, handleViewDetail, closeDetail, handleDelete, handleBatchDelete,
    handleExportCSV, handleExportExcel, toggleAll, toggleCheck,
    setPage, setPageSize, setKeyword, setFilterStatus, setFilterType,
    handleSearch, handleReset,
  };
}
