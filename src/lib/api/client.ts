const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

class ApiClient {
  private _baseURL: string;

  constructor(baseURL: string) {
    this._baseURL = baseURL;
  }

  /** 获取完整 API URL（供导出等需要直接 fetch 的场景使用） */
  getFullUrl(endpoint: string): string {
    return `${this._baseURL}${endpoint}`;
  }

  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getAuthHeaders(): HeadersInit {
    const headers: HeadersInit = {};
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const url = `${this._baseURL}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const contentType = response.headers.get('content-type');

      // 检查是否返回了 HTML 而不是 JSON
      if (contentType && !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('❌ API 返回了非 JSON 响应:', {
          url,
          method: options.method || 'GET',
          status: response.status,
          contentType,
          bodyPreview: text.substring(0, 200)
        });
        return {
          success: false,
          error: `服务器返回了 ${contentType} 而不是 JSON。URL: ${url}, Status: ${response.status}`,
        };
      }

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || data.detail || '请求失败',
        };
      }

      return data;
    } catch (error) {
      console.error('❌ API 请求异常:', {
        endpoint,
        error: error instanceof Error ? error.message : String(error)
      });
      return {
        success: false,
        error: error instanceof Error ? error.message : '网络错误',
      };
    }
  }

  /**
   * 下载文件流（用于导出 CSV/Excel 等）
   * 封装了认证 header 和 blob 下载逻辑
   */
  async downloadFile(endpoint: string, filename: string): Promise<void> {
    const url = this.getFullUrl(endpoint);
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`导出失败: ${response.status} ${text}`);
    }

    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(blobUrl);
    document.body.removeChild(a);
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    // 如果是 FormData，不设置 Content-Type，让浏览器自动设置
    if (data instanceof FormData) {
      const headers = this.getAuthHeaders();

      try {
        const response = await fetch(`${this._baseURL}${endpoint}`, {
          method: 'POST',
          headers,
          body: data,
        });

        const result = await response.json();

        if (!response.ok) {
          return {
            success: false,
            error: result.error || result.detail || '请求失败',
          };
        }

        return result;
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : '网络错误',
        };
      }
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
