/**
 * AI 配置列表组件
 * 展示配置列表，支持激活、编辑、删除、测试连接操作
 */

import { useState } from "react";
import {
  Play,
  Edit2,
  Trash2,
  CheckCircle2,
  Circle,
  Loader2,
  AlertCircle,
  FileText,
} from "lucide-react";
import type { AIConfig } from "../../lib/types/ai-config";
import {
  PROVIDER_VENDOR_LABELS,
  API_STYLE_LABELS,
  PDF_STRATEGY_LABELS,
} from "../../lib/types/ai-config";
import {
  activateAIConfig,
  deleteAIConfig,
  testAIConfigConnection,
} from "../../lib/api/ai-config";

interface AIConfigListProps {
  configs: AIConfig[];
  onEdit: (config: AIConfig) => void;
  onRefresh: () => void;
  onSampleTest: (config: AIConfig) => void;
}

export default function AIConfigList({
  configs,
  onEdit,
  onRefresh,
  onSampleTest,
}: AIConfigListProps) {
  const [testingId, setTestingId] = useState<number | null>(null);
  const [testResults, setTestResults] = useState<
    Record<number, {
      success: boolean;
      message: string;
      latency?: number;
      request_path?: string;
      status_code?: number;
    }>
  >({});
  const [activatingId, setActivatingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleActivate = async (id: number) => {
    try {
      setActivatingId(id);
      await activateAIConfig(id);
      onRefresh();
    } catch (error: any) {
      alert(`激活失败: ${error.message || "未知错误"}`);
    } finally {
      setActivatingId(null);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`确定要删除配置"${name}"吗？`)) {
      return;
    }
    try {
      setDeletingId(id);
      await deleteAIConfig(id);
      onRefresh();
    } catch (error: any) {
      alert(`删除失败: ${error.message || "未知错误"}`);
    } finally {
      setDeletingId(null);
    }
  };

  const handleTest = async (config: AIConfig) => {
    try {
      setTestingId(config.id);
      const result = await testAIConfigConnection(config.id);
      setTestResults((prev) => ({
        ...prev,
        [config.id]: {
          success: result.success,
          message: result.message,
          latency: result.latency_ms,
          request_path: result.request_path,
          status_code: result.status_code,
        },
      }));
    } catch (error: any) {
      setTestResults((prev) => ({
        ...prev,
        [config.id]: {
          success: false,
          message: error.message || "连接测试失败",
        },
      }));
    } finally {
      setTestingId(null);
    }
  };

  if (configs.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>暂无配置，请点击"新增配置"创建</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {configs.map((config) => {
        const testResult = testResults[config.id];
        const isActivating = activatingId === config.id;
        const isDeleting = deletingId === config.id;
        const isTesting = testingId === config.id;

        return (
          <div
            key={config.id}
            className={`bg-card border rounded-xl p-4 transition-all ${
              config.active
                ? "border-primary shadow-sm ring-1 ring-primary/10"
                : "border-border hover:border-primary/30"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-[15px] font-medium truncate">
                    {config.name}
                  </h3>
                  {config.active && (
                    <span className="px-2 py-0.5 text-[11px] bg-primary/10 text-primary rounded-md">
                      当前生效
                    </span>
                  )}
                  {!config.enabled && (
                    <span className="px-2 py-0.5 text-[11px] bg-muted text-muted-foreground rounded-md">
                      已禁用
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-[13px]">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">厂商类型:</span>
                    <span>{PROVIDER_VENDOR_LABELS[config.provider_vendor]}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">接口风格:</span>
                    <span>{API_STYLE_LABELS[config.api_style]}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Base URL:</span>
                    <span className="truncate">{config.base_url}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">模型:</span>
                    <span className="truncate">{config.model_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">API Key:</span>
                    <span className="font-mono text-[12px]">
                      {config.api_key_masked}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">PDF 策略:</span>
                    <span>{PDF_STRATEGY_LABELS[config.pdf_strategy]}</span>
                  </div>
                </div>

                {testResult && (
                  <div
                    className={`mt-3 p-2 rounded-lg text-[12px] ${
                      testResult.success
                        ? "bg-green-500/10 text-green-600 dark:text-green-400"
                        : "bg-red-500/10 text-red-600 dark:text-red-400"
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {testResult.success ? (
                        <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
                      ) : (
                        <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                      )}
                      <div className="flex-1">
                        <div>{testResult.message}</div>
                        {testResult.latency && (
                          <div className="text-[11px] opacity-75 mt-0.5">
                            延迟: {testResult.latency}ms
                          </div>
                        )}
                        {testResult.request_path && (
                          <div className="text-[11px] opacity-75 mt-0.5 font-mono">
                            路径: {testResult.request_path}
                          </div>
                        )}
                        {testResult.status_code && (
                          <div className="text-[11px] opacity-75 mt-0.5">
                            状态码: {testResult.status_code}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => onSampleTest(config)}
                  disabled={!config.enabled}
                  className="p-2 rounded-lg hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="样本测试"
                >
                  <FileText className="w-4 h-4" />
                </button>

                <button
                  onClick={() => handleTest(config)}
                  disabled={isTesting || !config.enabled}
                  className="p-2 rounded-lg hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="测试连接"
                >
                  {isTesting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                </button>

                <button
                  onClick={() => handleActivate(config.id)}
                  disabled={config.active || isActivating || !config.enabled}
                  className="p-2 rounded-lg hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={config.active ? "已激活" : "激活配置"}
                >
                  {isActivating ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : config.active ? (
                    <CheckCircle2 className="w-4 h-4 text-primary" />
                  ) : (
                    <Circle className="w-4 h-4" />
                  )}
                </button>

                <button
                  onClick={() => onEdit(config)}
                  className="p-2 rounded-lg hover:bg-accent transition-colors"
                  title="编辑"
                >
                  <Edit2 className="w-4 h-4" />
                </button>

                <button
                  onClick={() => handleDelete(config.id, config.name)}
                  disabled={isDeleting || config.active}
                  className="p-2 rounded-lg hover:bg-destructive/10 hover:text-destructive transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={config.active ? "当前生效的配置不能删除" : "删除"}
                >
                  {isDeleting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
