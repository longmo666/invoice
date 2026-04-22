/**
 * 待复核页面中央 hook
 * 管理 items/page/pageSize/refreshing/reviewingId/editedData/submitting
 * 及 loadPendingItems/handleReview/handleConfirm/handleVoid
 */
import { useState, useEffect } from "react";
import {
  recognitionService,
  type PendingReviewItem,
  type InvoiceType,
} from "../../../lib/services/recognition";
import { getResultData } from "../../../lib/helpers/pendingReview";

const DEFAULT_PAGE_SIZE = 10;

/** 按 activeMenu 推导 invoiceType，与 upload/list 保持一致 */
const MENU_INVOICE_TYPE: Record<string, InvoiceType> = {
  invoice: "vat_normal",
  train: "railway_ticket",
};

export function usePendingReview(activeMenu: string) {
  const isTrainTicket = activeMenu === "train";
  const invoiceType: InvoiceType = MENU_INVOICE_TYPE[activeMenu] || "vat_normal";

  const [items, setItems] = useState<PendingReviewItem[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [refreshing, setRefreshing] = useState(false);
  const [reviewingId, setReviewingId] = useState<number | null>(null);
  const [editedData, setEditedData] = useState<any>({});
  const [submitting, setSubmitting] = useState(false);

  const totalPages = Math.ceil(items.length / pageSize) || 1;
  const paged = items.slice((page - 1) * pageSize, page * pageSize);
  const reviewingItem = items.find((i) => i.id === reviewingId) || null;

  const loadPendingItems = async () => {
    setRefreshing(true);
    try {
      const response = await recognitionService.getPendingReviewItems(invoiceType);
      if (response.success && response.data) {
        setItems(response.data);
      }
    } catch (error) {
      console.error("Load pending items error:", error);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => { loadPendingItems(); }, [activeMenu]);

  const handleReview = (item: PendingReviewItem) => {
    setReviewingId(item.id);
    setEditedData(getResultData(item));
  };

  const handleFieldChange = (field: string, value: string) => {
    setEditedData((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleConfirm = async () => {
    if (!reviewingItem) return;
    setSubmitting(true);
    try {
      const response = await recognitionService.updateReview(reviewingItem.id, editedData);
      if (response.success) {
        setItems((prev) => prev.filter((i) => i.id !== reviewingItem.id));
        setReviewingId(null);
        setEditedData({});
      }
    } catch (error) {
      console.error("Confirm review error:", error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleVoid = async (itemId: number) => {
    if (!confirm("确定要作废该记录？作废后将物理删除，不可恢复。")) return;
    try {
      const response = await recognitionService.voidReviewItem(itemId);
      if (response.success) {
        setItems((prev) => prev.filter((i) => i.id !== itemId));
        if (reviewingId === itemId) { setReviewingId(null); setEditedData({}); }
      }
    } catch (error) {
      console.error("Void item error:", error);
      alert("作废失败");
    }
  };

  return {
    isTrainTicket,
    items,
    page,
    setPage,
    pageSize,
    setPageSize,
    totalPages,
    paged,
    refreshing,
    reviewingId,
    setReviewingId,
    reviewingItem,
    editedData,
    submitting,
    loadPendingItems,
    handleReview,
    handleFieldChange,
    handleConfirm,
    handleVoid,
  };
}
