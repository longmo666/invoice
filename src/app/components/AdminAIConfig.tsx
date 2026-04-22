/**
 * AI 配置管理主页面
 * 组合列表和表单，提供完整的配置管理界面
 */

import { useState, useEffect } from "react";
import { Plus, RefreshCw, Loader2 } from "lucide-react";
import AIConfigList from "./AIConfigList";
import AIConfigForm from "./AIConfigForm";
import AIConfigSampleTest from "./AIConfigSampleTest";
import type { AIConfig } from "../../lib/types/ai-config";
import { listAIConfigs } from "../../lib/api/ai-config";

export default function AdminAIConfig() {
  const [configs, setConfigs] = useState<AIConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<AIConfig | null>(null);
  const [showSampleTest, setShowSampleTest] = useState(false);
  const [testingConfig, setTestingConfig] = useState<AIConfig | null>(null);

  const loadConfigs = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      const data = await listAIConfigs();
      setConfigs(data);
    } catch (error: any) {
      console.error("加载配置失败:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadConfigs();
  }, []);

  const handleEdit = (config: AIConfig) => {
    setEditingConfig(config);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingConfig(null);
  };

  const handleFormSuccess = () => {
    handleCloseForm();
    loadConfigs(true);
  };

  const handleSampleTest = (config: AIConfig) => {
    setTestingConfig(config);
    setShowSampleTest(true);
  };

  const handleCloseSampleTest = () => {
    setShowSampleTest(false);
    setTestingConfig(null);
  };

  const handleSampleTestSuccess = () => {
    handleCloseSampleTest();
    loadConfigs(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-primary" />
          <p className="text-[13px] text-muted-foreground">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-[20px] font-medium mb-1">AI 配置管理</h1>
            <p className="text-[13px] text-muted-foreground">
              管理 AI 识别服务的配置，支持多厂商和多接口风格
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => loadConfigs(true)}
              disabled={refreshing}
              className="px-4 py-2 text-[13px] rounded-lg border border-border hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <RefreshCw
                className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`}
              />
              刷新
            </button>
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 text-[13px] bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              新增配置
            </button>
          </div>
        </div>

        <AIConfigList
          configs={configs}
          onEdit={handleEdit}
          onRefresh={() => loadConfigs(true)}
          onSampleTest={handleSampleTest}
        />

        {showForm && (
          <AIConfigForm
            config={editingConfig}
            onClose={handleCloseForm}
            onSuccess={handleFormSuccess}
          />
        )}

        {showSampleTest && testingConfig && (
          <AIConfigSampleTest
            config={testingConfig}
            onClose={handleCloseSampleTest}
            onSuccess={handleSampleTestSuccess}
          />
        )}
      </div>
    </div>
  );
}
