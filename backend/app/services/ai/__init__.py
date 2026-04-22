"""
AI 基础设施共享层

提供所有 AI API 调用所需的公共能力：
- transport: 传输模式枚举
- http_helpers: URL/Header 构造纯函数
- request_builders: 请求构建器（多态）
- response_parsers: 响应解析器（多态）
- rate_limiter: 全局速率限制

业务层（recognition、cleaning、未来的学术工具等）只能通过此包获取 AI 基础能力。
"""
