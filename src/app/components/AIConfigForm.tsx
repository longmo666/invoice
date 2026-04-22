/**
 * AI 配置表单组件
 * 支持新增和编辑配置，包含所有必需字段
 */

import { useState, useEffect } from "react";
import { X, Loader2 } from "lucide-react";
import type {
  AIConfig,
  AIConfigCreateRequest,
  AIConfigUpdateRequest,
} from "../../lib/types/ai-config";
import {
  ProviderVendor,
  ApiStyle,
  PDFStrategy,
  PROVIDER_VENDOR_LABELS,
  API_STYLE_LABELS,
  PDF_STRATEGY_LABELS,
  getSupportedApiStyles,
} from "../../lib/types/ai-config";
import { createAIConfig, updateAIConfig } from "../../lib/api/ai-config";

interface AIConfigFormProps {
  config?: AIConfig | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AIConfigForm({
  config,
  onClose,
  onSuccess,
}: AIConfigFormProps) {
  const isEdit = !!config;

  const [formData, setFormData] = useState<AIConfigCreateRequest>({
    name: "",
    provider_vendor: ProviderVendor.OPENAI_COMPATIBLE,
    api_style: ApiStyle.OPENAI_CHAT_COMPLETIONS,
    base_url: "",
    model_name: "",
    api_key: "",
    pdf_strategy: PDFStrategy.CONVERT_TO_IMAGES,
    ocr_chat_model: "",
    timeout: 60,
    temperature: 0.1,
    max_tokens: 4000,
    max_concurrency: 1,
    supports_image_input: true,
    supports_pdf_file_input: false,
    supports_file_id: false,
    supports_file_url: false,
    requires_files_api: false,
    supports_structured_json: true,
    enabled: true,
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (config) {
      setFormData({
        name: config.name,
        provider_vendor: config.provider_vendor,
        api_style: config.api_style,
        base_url: config.base_url,
        model_name: config.model_name,
        ocr_chat_model: config.ocr_chat_model || "",
        api_key: "", // 编辑时不显示原 API Key
        pdf_strategy: config.pdf_strategy,
        timeout: config.timeout,
        temperature: config.temperature,
        max_tokens: config.max_tokens,
        max_concurrency: config.max_concurrency,
        supports_image_input: config.supports_image_input,
        supports_pdf_file_input: config.supports_pdf_file_input,
        supports_file_id: config.supports_file_id,
        supports_file_url: config.supports_file_url,
        requires_files_api: config.requires_files_api,
        supports_structured_json: config.supports_structured_json,
        enabled: config.enabled,
      });
    }
  }, [config]);

  const handleProviderVendorChange = (vendor: ProviderVendor) => {
    const supportedStyles = getSupportedApiStyles(vendor);
    setFormData({
      ...formData,
      provider_vendor: vendor,
      api_style: supportedStyles[0] || ApiStyle.OPENAI_CHAT_COMPLETIONS,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    console.log('📝 表单提交开始', { isEdit, config, formData });

    if (!formData.name.trim()) {
      setError("配置名称不能为空");
      return;
    }
    if (!formData.base_url.trim()) {
      setError("Base URL 不能为空");
      return;
    }
    if (!formData.model_name.trim()) {
      setError("模型名称不能为空");
      return;
    }
    if (!isEdit && !formData.api_key.trim()) {
      setError("API Key 不能为空");
      return;
    }

    try {
      setSubmitting(true);
      console.log('📝 开始提交，submitting=true');
      if (isEdit && config) {
        const updateData: AIConfigUpdateRequest = { ...formData };
        // 如果编辑时 API Key 为空，则不更新
        if (!updateData.api_key) {
          delete updateData.api_key;
        }
        console.log('📝 调用 updateAIConfig', { id: config.id, updateData });
        await updateAIConfig(config.id, updateData);
        console.log('📝 updateAIConfig 成功');
      } else {
        console.log('📝 调用 createAIConfig', formData);
        await createAIConfig(formData);
        console.log('📝 createAIConfig 成功');
      }
      console.log('📝 调用 onSuccess');
      onSuccess();
    } catch (err: any) {
      console.error('📝 提交失败', err);
      setError(err.message || "操作失败");
    } finally {
      setSubmitting(false);
      console.log('📝 提交结束，submitting=false');
    }
  };

  const supportedApiStyles = getSupportedApiStyles(formData.provider_vendor);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-border flex items-center justify-between">
          <h2 className="text-[18px] font-medium">
            {isEdit ? "编辑配置" : "新增配置"}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-accent transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
          <div className="px-6 py-4 space-y-4">
            {error && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-lg text-[13px]">
                {error}
              </div>
            )}

            <div>
              <label className="block text-[13px] font-medium mb-1.5">
                配置名称 <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="例如: OpenAI GPT-4"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[13px] font-medium mb-1.5">
                  厂商类型 <span className="text-destructive">*</span>
                </label>
                <select
                  value={formData.provider_vendor}
                  onChange={(e) =>
                    handleProviderVendorChange(e.target.value as ProviderVendor)
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                >
                  {Object.entries(PROVIDER_VENDOR_LABELS).map(([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[13px] font-medium mb-1.5">
                  接口风格 <span className="text-destructive">*</span>
                </label>
                <select
                  value={formData.api_style}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      api_style: e.target.value as ApiStyle,
                    })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                >
                  {supportedApiStyles.map((style) => (
                    <option key={style} value={style}>
                      {API_STYLE_LABELS[style]}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-[13px] font-medium mb-1.5">
                Base URL <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={formData.base_url}
                onChange={(e) =>
                  setFormData({ ...formData, base_url: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="例如: https://api.openai.com"
              />
              <p className="text-[12px] text-muted-foreground mt-1">
                填写根地址即可，系统会自动拼接对应的 API 路径
              </p>
            </div>

            <div>
              <label className="block text-[13px] font-medium mb-1.5">
                模型名称 <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={formData.model_name}
                onChange={(e) =>
                  setFormData({ ...formData, model_name: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="例如: gpt-4-vision-preview"
              />
            </div>

            {formData.api_style === ApiStyle.ZHIPU_OCR && (
              <div>
                <label className="block text-[13px] font-medium mb-1.5">
                  结构化提取模型
                </label>
                <input
                  type="text"
                  value={formData.ocr_chat_model || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, ocr_chat_model: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                  placeholder="例如: glm-4-flash（留空默认 glm-4-flash）"
                />
                <p className="mt-1 text-[12px] text-muted-foreground">
                  OCR 模型只负责文字提取，结构化 JSON 提取需要用支持 chat 的模型
                </p>
              </div>
            )}

            <div>
              <label className="block text-[13px] font-medium mb-1.5">
                API Key <span className="text-destructive">*</span>
              </label>
              <input
                type="password"
                value={formData.api_key}
                onChange={(e) =>
                  setFormData({ ...formData, api_key: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] font-mono focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder={isEdit ? "留空则不修改" : "输入 API Key"}
              />
              {isEdit && config?.has_api_key && (
                <p className="mt-1 text-[12px] text-muted-foreground">
                  当前已设置 API Key: {config.api_key_masked}
                </p>
              )}
            </div>

            <div>
              <label className="block text-[13px] font-medium mb-1.5">
                PDF 处理策略
              </label>
              <select
                value={formData.pdf_strategy}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    pdf_strategy: e.target.value as PDFStrategy,
                  })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                {Object.entries(PDF_STRATEGY_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-[12px] text-muted-foreground">
                可在样本测试后根据对比结果调整
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-[13px] font-medium mb-1.5">
                  超时时间 (秒)
                </label>
                <input
                  type="number"
                  value={formData.timeout}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      timeout: parseInt(e.target.value) || 60,
                    })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                  min="10"
                  max="300"
                />
              </div>

              <div>
                <label className="block text-[13px] font-medium mb-1.5">
                  最大并发数
                </label>
                <input
                  type="number"
                  value={formData.max_concurrency}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      max_concurrency: parseInt(e.target.value) || 1,
                    })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                  min="1"
                  max="10"
                />
              </div>

              <div>
                <label className="block text-[13px] font-medium mb-1.5">
                  Temperature
                </label>
                <input
                  type="number"
                  value={formData.temperature}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      temperature: parseFloat(e.target.value) || 0.1,
                    })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                  min="0"
                  max="2"
                  step="0.1"
                />
              </div>
            </div>

            <div>
              <label className="block text-[13px] font-medium mb-1.5">
                Max Tokens
              </label>
              <input
                type="number"
                value={formData.max_tokens}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    max_tokens: parseInt(e.target.value) || 4000,
                  })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
                min="100"
                max="32000"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-[13px] font-medium">能力配置</label>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center gap-2 text-[13px]">
                  <input
                    type="checkbox"
                    checked={formData.supports_image_input}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        supports_image_input: e.target.checked,
                      })
                    }
                    className="w-4 h-4 rounded border-border"
                  />
                  支持图片输入
                </label>
                <label className="flex items-center gap-2 text-[13px]">
                  <input
                    type="checkbox"
                    checked={formData.supports_pdf_file_input}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        supports_pdf_file_input: e.target.checked,
                      })
                    }
                    className="w-4 h-4 rounded border-border"
                  />
                  支持 PDF 输入
                </label>
                <label className="flex items-center gap-2 text-[13px]">
                  <input
                    type="checkbox"
                    checked={formData.supports_structured_json}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        supports_structured_json: e.target.checked,
                      })
                    }
                    className="w-4 h-4 rounded border-border"
                  />
                  支持结构化 JSON
                </label>
                <label className="flex items-center gap-2 text-[13px]">
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        enabled: e.target.checked,
                      })
                    }
                    className="w-4 h-4 rounded border-border"
                  />
                  启用配置
                </label>
              </div>
            </div>
          </div>

          <div className="px-6 py-4 border-t border-border flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-[13px] rounded-lg hover:bg-accent transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 text-[13px] bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {isEdit ? "保存" : "创建"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
