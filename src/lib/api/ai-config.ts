/**
 * AI 配置 API 服务层
 * 封装所有 AI 配置相关的 API 调用
 */

import { apiClient } from "./client";
import type {
  AIConfig,
  AIConfigCreateRequest,
  AIConfigUpdateRequest,
  AIConfigTestResponse,
  SampleTestResponse,
  UpdatePDFStrategyRequest,
} from "../types/ai-config";

/**
 * 获取 AI 配置列表
 */
export async function listAIConfigs(): Promise<AIConfig[]> {
  const response = await apiClient.get<AIConfig[]>("/ai-configs");
  if (!response.success || !response.data) {
    throw new Error(response.error || "获取配置列表失败");
  }
  return response.data;
}

/**
 * 获取单个 AI 配置详情
 */
export async function getAIConfig(id: number): Promise<AIConfig> {
  const response = await apiClient.get<AIConfig>(`/ai-configs/${id}`);
  if (!response.success || !response.data) {
    throw new Error(response.error || "获取配置详情失败");
  }
  return response.data;
}

/**
 * 创建 AI 配置
 */
export async function createAIConfig(
  data: AIConfigCreateRequest
): Promise<AIConfig> {
  const response = await apiClient.post<AIConfig>("/ai-configs", data);
  if (!response.success || !response.data) {
    throw new Error(response.error || "创建配置失败");
  }
  return response.data;
}

/**
 * 更新 AI 配置
 */
export async function updateAIConfig(
  id: number,
  data: AIConfigUpdateRequest
): Promise<AIConfig> {
  console.log('🔧 updateAIConfig 调用:', { id, data });
  const response = await apiClient.put<AIConfig>(`/ai-configs/${id}`, data);
  console.log('🔧 updateAIConfig 响应:', response);
  if (!response.success || !response.data) {
    throw new Error(response.error || "更新配置失败");
  }
  return response.data;
}

/**
 * 删除 AI 配置
 */
export async function deleteAIConfig(id: number): Promise<void> {
  const response = await apiClient.delete(`/ai-configs/${id}`);
  if (!response.success) {
    throw new Error(response.error || "删除配置失败");
  }
}

/**
 * 激活 AI 配置
 * 激活后会自动取消其他配置的激活状态
 */
export async function activateAIConfig(id: number): Promise<void> {
  const response = await apiClient.post(`/ai-configs/${id}/activate`, {});
  if (!response.success) {
    throw new Error(response.error || "激活配置失败");
  }
}

/**
 * 切换 AI 配置启用状态
 */
export async function toggleAIConfigEnabled(
  id: number,
  enabled: boolean
): Promise<void> {
  const response = await apiClient.post(`/ai-configs/${id}/toggle-enabled`, { enabled });
  if (!response.success) {
    throw new Error(response.error || "切换启用状态失败");
  }
}

/**
 * 测试 AI 配置连接
 */
export async function testAIConfigConnection(
  configId: number
): Promise<AIConfigTestResponse> {
  const response = await apiClient.post<AIConfigTestResponse>(
    `/ai-configs/test-connection?config_id=${configId}`,
    {}
  );
  if (!response.success || !response.data) {
    throw new Error(response.error || "测试连接失败");
  }
  return response.data;
}

/**
 * 样本测试（图片或 PDF）
 */
export async function testSampleFile(
  configId: number,
  file: File,
  invoiceType: string
): Promise<SampleTestResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("invoice_type", invoiceType);

  const response = await apiClient.post<SampleTestResponse>(
    `/ai-configs/${configId}/sample-test`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  if (!response.success || !response.data) {
    throw new Error(response.error || "样本测试失败");
  }
  return response.data;
}

/**
 * 更新 PDF 策略
 */
export async function updatePDFStrategy(
  configId: number,
  data: UpdatePDFStrategyRequest
): Promise<void> {
  const response = await apiClient.post(`/ai-configs/${configId}/pdf-strategy`, data);
  if (!response.success) {
    throw new Error(response.error || "更新 PDF 策略失败");
  }
}
