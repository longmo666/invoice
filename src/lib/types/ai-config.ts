/**
 * AI 配置类型定义
 * 与后端字段完全一致，确保前后端统一
 */

/**
 * 厂商类型枚举
 */
export enum ProviderVendor {
  OPENAI_COMPATIBLE = "openai_compatible",
  ANTHROPIC_COMPATIBLE = "anthropic_compatible",
  GOOGLE_COMPATIBLE = "google_compatible",
  ZHIPU_COMPATIBLE = "zhipu_compatible",
}

/**
 * 接口风格枚举
 */
export enum ApiStyle {
  OPENAI_RESPONSES = "openai_responses",
  OPENAI_CHAT_COMPLETIONS = "openai_chat_completions",
  ANTHROPIC_MESSAGES = "anthropic_messages",
  GEMINI_GENERATE_CONTENT = "gemini_generate_content",
  ZHIPU_CHAT_COMPLETIONS = "zhipu_chat_completions",
  ZHIPU_OCR = "zhipu_ocr",
}

/**
 * PDF 策略枚举
 */
export enum PDFStrategy {
  DIRECT_PDF = "direct_pdf",
  CONVERT_TO_IMAGES = "convert_to_images",
}

/**
 * AI 配置完整模型
 */
export interface AIConfig {
  id: number;
  name: string;
  provider_vendor: ProviderVendor;
  api_style: ApiStyle;
  base_url: string;
  model_name: string;
  api_key_masked: string; // 脱敏后的 API Key
  has_api_key: boolean; // 是否已设置 API Key
  pdf_strategy: PDFStrategy; // PDF 处理策略
  ocr_chat_model?: string; // OCR 模式下结构化提取用的 chat 模型
  timeout: number;
  temperature: number;
  max_tokens: number;
  max_concurrency: number;
  supports_image_input: boolean;
  supports_pdf_file_input: boolean;
  supports_file_id: boolean;
  supports_file_url: boolean;
  requires_files_api: boolean;
  supports_structured_json: boolean;
  enabled: boolean;
  active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 创建 AI 配置请求
 */
export interface AIConfigCreateRequest {
  name: string;
  provider_vendor: ProviderVendor;
  api_style: ApiStyle;
  base_url: string;
  model_name: string;
  api_key: string;
  pdf_strategy?: PDFStrategy;
  ocr_chat_model?: string;
  timeout?: number;
  temperature?: number;
  max_tokens?: number;
  max_concurrency?: number;
  supports_image_input?: boolean;
  supports_pdf_file_input?: boolean;
  supports_file_id?: boolean;
  supports_file_url?: boolean;
  requires_files_api?: boolean;
  supports_structured_json?: boolean;
  enabled?: boolean;
}

/**
 * 更新 AI 配置请求
 */
export interface AIConfigUpdateRequest {
  name?: string;
  provider_vendor?: ProviderVendor;
  api_style?: ApiStyle;
  base_url?: string;
  model_name?: string;
  api_key?: string;
  pdf_strategy?: PDFStrategy;
  ocr_chat_model?: string;
  timeout?: number;
  temperature?: number;
  max_tokens?: number;
  max_concurrency?: number;
  supports_image_input?: boolean;
  supports_pdf_file_input?: boolean;
  supports_file_id?: boolean;
  supports_file_url?: boolean;
  requires_files_api?: boolean;
  supports_structured_json?: boolean;
  enabled?: boolean;
}

/**
 * 测试连接响应
 */
export interface DiagnosticStep {
  step: string;
  url: string;
  status_code: number | null;
  latency_ms: number | null;
  success: boolean;
  detail: string;
}

export interface AIConfigTestResponse {
  success: boolean;
  message: string;
  latency_ms?: number;
  request_path?: string;
  status_code?: number;
  diagnostic_steps: DiagnosticStep[];
}

/**
 * 样本测试模式枚举
 */
export enum SampleTestMode {
  IMAGE_SINGLE = "image_single",
  PDF_COMPARE = "pdf_compare",
}

/**
 * 样本测试结果
 */
export interface SampleTestResult {
  success: boolean;
  strategy?: string;
  latency_ms?: number;
  request_path?: string;
  execution_path?: string;
  status_code?: number;
  error_message?: string;
  raw_response?: Record<string, any>;
  structured_result?: Record<string, any>;
  diagnostic_steps?: DiagnosticStep[];
  field_completeness?: {
    required_fields_total: number;
    recognized_fields_count: number;
    missing_fields: string[];
    completeness_rate: number;
  };
  total_pages?: number;
  all_page_results?: Record<string, any>[];
  best_page_index?: number;
}

/**
 * 样本测试响应
 */
export interface SampleTestResponse {
  test_mode: SampleTestMode;
  file_name: string;
  file_type: string;
  invoice_type: string;
  result?: SampleTestResult;
  direct_pdf_result?: SampleTestResult;
  convert_to_images_result?: SampleTestResult;
  recommended_strategy?: string;
  recommendation_reason?: string;
}

/**
 * 更新 PDF 策略请求
 */
export interface UpdatePDFStrategyRequest {
  pdf_strategy: PDFStrategy;
}

/**
 * 厂商类型显示名称映射
 */
export const PROVIDER_VENDOR_LABELS: Record<ProviderVendor, string> = {
  [ProviderVendor.OPENAI_COMPATIBLE]: "OpenAI 兼容",
  [ProviderVendor.ANTHROPIC_COMPATIBLE]: "Anthropic 兼容",
  [ProviderVendor.GOOGLE_COMPATIBLE]: "Google Gemini",
  [ProviderVendor.ZHIPU_COMPATIBLE]: "智谱 GLM",
};

/**
 * 接口风格显示名称映射
 */
export const API_STYLE_LABELS: Record<ApiStyle, string> = {
  [ApiStyle.OPENAI_RESPONSES]: "OpenAI Responses",
  [ApiStyle.OPENAI_CHAT_COMPLETIONS]: "OpenAI Chat Completions",
  [ApiStyle.ANTHROPIC_MESSAGES]: "Anthropic Messages",
  [ApiStyle.GEMINI_GENERATE_CONTENT]: "Gemini generateContent",
  [ApiStyle.ZHIPU_CHAT_COMPLETIONS]: "智谱 Chat Completions",
  [ApiStyle.ZHIPU_OCR]: "智谱 OCR（文件上传+结构化）",
};

/**
 * PDF 策略显示名称映射
 */
export const PDF_STRATEGY_LABELS: Record<PDFStrategy, string> = {
  [PDFStrategy.DIRECT_PDF]: "直接传 PDF",
  [PDFStrategy.CONVERT_TO_IMAGES]: "转图片后识别",
};

/**
 * 根据厂商类型获取支持的接口风格
 */
export function getSupportedApiStyles(vendor: ProviderVendor): ApiStyle[] {
  switch (vendor) {
    case ProviderVendor.OPENAI_COMPATIBLE:
      return [ApiStyle.OPENAI_CHAT_COMPLETIONS, ApiStyle.OPENAI_RESPONSES];
    case ProviderVendor.ANTHROPIC_COMPATIBLE:
      return [ApiStyle.ANTHROPIC_MESSAGES];
    case ProviderVendor.GOOGLE_COMPATIBLE:
      return [ApiStyle.GEMINI_GENERATE_CONTENT];
    case ProviderVendor.ZHIPU_COMPATIBLE:
      return [ApiStyle.ZHIPU_CHAT_COMPLETIONS, ApiStyle.ZHIPU_OCR];
    default:
      return [];
  }
}

/**
 * 脱敏 API Key
 */
export function maskApiKey(apiKey: string): string {
  if (!apiKey || apiKey.length <= 8) {
    return "***";
  }
  return `${apiKey.slice(0, 8)}...`;
}
