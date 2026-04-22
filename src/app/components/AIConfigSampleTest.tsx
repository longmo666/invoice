/**
 * AI 配置样本测试组件
 * 支持上传图片或 PDF 进行样本测试
 */

import { useState } from "react";
import { X, Upload, Loader2, CheckCircle2, AlertCircle, FileImage, FileText } from "lucide-react";
import type { AIConfig, SampleTestResponse, SampleTestResult } from "../../lib/types/ai-config";
import { testSampleFile, updatePDFStrategy } from "../../lib/api/ai-config";
import { PDFStrategy, PDF_STRATEGY_LABELS } from "../../lib/types/ai-config";

interface AIConfigSampleTestProps {
  config: AIConfig;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AIConfigSampleTest({
  config,
  onClose,
  onSuccess,
}: AIConfigSampleTestProps) {
  const [file, setFile] = useState<File | null>(null);
  const [invoiceType, setInvoiceType] = useState("vat_normal");
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<SampleTestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [updatingStrategy, setUpdatingStrategy] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const ext = selectedFile.name.toLowerCase().split('.').pop();
      if (!['jpg', 'jpeg', 'png', 'bmp', 'gif', 'pdf'].includes(ext || '')) {
        setError("仅支持图片（JPG/PNG/BMP/GIF）或 PDF 文件");
        return;
      }
      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  };

  const handleTest = async () => {
    if (!file) {
      setError("请先选择文件");
      return;
    }

    try {
      setTesting(true);
      setError(null);
      const response = await testSampleFile(config.id, file, invoiceType);
      setResult(response);
    } catch (err: any) {
      setError(err.message || "测试失败");
    } finally {
      setTesting(false);
    }
  };

  const handleSetStrategy = async (strategy: PDFStrategy) => {
    try {
      setUpdatingStrategy(true);
      await updatePDFStrategy(config.id, { pdf_strategy: strategy });
      onSuccess();
    } catch (err: any) {
      setError(err.message || "更新策略失败");
    } finally {
      setUpdatingStrategy(false);
    }
  };

  const renderTestResult = (testResult: SampleTestResult, title: string) => {
    return (
      <div className="border border-border rounded-lg p-4">
        <h4 className="text-[14px] font-medium mb-3">{title}</h4>

        <div className={`flex items-start gap-2 p-3 rounded-lg text-[13px] ${
          testResult.success
            ? "bg-green-500/10 text-green-600 dark:text-green-400"
            : "bg-red-500/10 text-red-600 dark:text-red-400"
        }`}>
          {testResult.success ? (
            <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          )}
          <div className="flex-1">
            <div className="font-medium">
              {testResult.success ? "测试成功" : "测试失败"}
            </div>
            {testResult.error_message && (
              <div className="mt-1 text-[12px] opacity-90">
                {testResult.error_message}
              </div>
            )}
          </div>
        </div>

        <div className="mt-3 space-y-2 text-[13px]">
          {testResult.latency_ms && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">延迟:</span>
              <span>{testResult.latency_ms}ms</span>
            </div>
          )}
          {testResult.request_path && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">请求路径:</span>
              <span className="font-mono text-[12px]">{testResult.request_path}</span>
            </div>
          )}
          {testResult.execution_path && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">执行路径:</span>
              <span className="font-mono text-[12px]">{testResult.execution_path}</span>
            </div>
          )}
          {testResult.total_pages && testResult.total_pages > 1 && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">PDF 页数:</span>
              <span className="font-medium">{testResult.total_pages} 页</span>
            </div>
          )}
          {testResult.best_page_index && testResult.total_pages && testResult.total_pages > 1 && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">最佳页:</span>
              <span className="font-medium text-primary">第 {testResult.best_page_index} 页</span>
              <span className="text-[11px] text-muted-foreground">(推荐依据)</span>
            </div>
          )}
          {testResult.field_completeness && (
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">字段完整度:</span>
              <span className="font-medium">
                {testResult.field_completeness.recognized_fields_count} / {testResult.field_completeness.required_fields_total}
                {" "}({testResult.field_completeness.completeness_rate}%)
              </span>
            </div>
          )}
          {testResult.field_completeness && testResult.field_completeness.missing_fields.length > 0 && (
            <div className="flex items-start gap-2">
              <span className="text-muted-foreground">缺失字段:</span>
              <span className="text-orange-600 dark:text-orange-400 text-[12px]">
                {testResult.field_completeness.missing_fields.join(", ")}
              </span>
            </div>
          )}
        </div>

        {testResult.structured_result && (
          <div className="mt-3">
            <div className="text-[13px] text-muted-foreground mb-2">识别结果:</div>
            <div className="bg-muted/50 rounded-lg p-3 text-[12px] font-mono max-h-[200px] overflow-y-auto">
              <pre className="whitespace-pre-wrap">
                {JSON.stringify(testResult.structured_result, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {testResult.all_page_results && testResult.all_page_results.length > 1 && (
          <details className="mt-3">
            <summary className="text-[13px] text-muted-foreground cursor-pointer hover:text-foreground">
              所有页面结果 (点击展开 {testResult.all_page_results.length} 页)
            </summary>
            <div className="mt-2 space-y-2">
              {testResult.all_page_results.map((pageResult, idx) => (
                <div key={idx} className="bg-muted/50 rounded-lg p-3">
                  <div className="text-[12px] font-medium mb-2">第 {idx + 1} 页</div>
                  <div className="text-[12px] font-mono max-h-[150px] overflow-y-auto">
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(pageResult, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </details>
        )}

        {testResult.raw_response && (
          <details className="mt-3">
            <summary className="text-[13px] text-muted-foreground cursor-pointer hover:text-foreground">
              原始响应 (点击展开)
            </summary>
            <div className="mt-2 bg-muted/50 rounded-lg p-3 text-[12px] font-mono max-h-[300px] overflow-y-auto">
              <pre className="whitespace-pre-wrap">
                {JSON.stringify(testResult.raw_response, null, 2)}
              </pre>
            </div>
          </details>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-border flex items-center justify-between">
          <div>
            <h2 className="text-[18px] font-medium">样本测试</h2>
            <p className="text-[13px] text-muted-foreground mt-1">
              配置: {config.name}
            </p>
            <div className="text-[12px] text-muted-foreground mt-2 space-y-1">
              <div>厂商: {config.provider_vendor} | 接口: {config.api_style}</div>
              <div>模型: {config.model_name}</div>
              <div>Base URL: {config.base_url}</div>
              <div>当前 PDF 策略: {config.pdf_strategy === "direct_pdf" ? "直接传 PDF" : "转图片后识别"}</div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-accent transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && (
            <div className="p-3 bg-destructive/10 text-destructive rounded-lg text-[13px] flex items-start gap-2">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <div>{error}</div>
            </div>
          )}

          <div>
            <label className="block text-[13px] font-medium mb-2">
              上传测试文件 <span className="text-destructive">*</span>
            </label>
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.bmp,.gif,.pdf"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center gap-3"
              >
                <Upload className="w-8 h-8 text-muted-foreground" />
                <div className="text-[13px]">
                  {file ? (
                    <div className="flex items-center gap-2">
                      {file.name.toLowerCase().endsWith('.pdf') ? (
                        <FileText className="w-4 h-4" />
                      ) : (
                        <FileImage className="w-4 h-4" />
                      )}
                      <span className="font-medium">{file.name}</span>
                    </div>
                  ) : (
                    <>
                      <div className="font-medium">点击选择文件</div>
                      <div className="text-muted-foreground text-[12px] mt-1">
                        支持 JPG、PNG、BMP、GIF、PDF
                      </div>
                    </>
                  )}
                </div>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-[13px] font-medium mb-2">
              发票类型
            </label>
            <select
              value={invoiceType}
              onChange={(e) => setInvoiceType(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option value="vat_special">增值税专用发票</option>
              <option value="vat_normal">增值税普通发票</option>
              <option value="railway_ticket">火车票</option>
            </select>
          </div>

          <button
            onClick={handleTest}
            disabled={!file || testing}
            className="w-full px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-[14px] font-medium"
          >
            {testing && <Loader2 className="w-4 h-4 animate-spin" />}
            {testing ? "测试中..." : "开始测试"}
          </button>

          {result && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-[14px] font-medium">
                <div className="w-1 h-4 bg-primary rounded-full" />
                测试结果
              </div>

              {result.test_mode === "image_single" && result.result && (
                renderTestResult(result.result, "图片识别结果")
              )}

              {result.test_mode === "pdf_compare" && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    {result.direct_pdf_result && (
                      renderTestResult(result.direct_pdf_result, "直接传 PDF")
                    )}
                    {result.convert_to_images_result && (
                      renderTestResult(result.convert_to_images_result, "转图片后识别")
                    )}
                  </div>

                  {result.recommended_strategy && (
                    <div className="border border-primary/30 bg-primary/5 rounded-lg p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="text-[14px] font-medium mb-2">推荐策略</div>
                          <div className="text-[13px] mb-1">
                            <span className="font-medium">
                              {PDF_STRATEGY_LABELS[result.recommended_strategy as PDFStrategy]}
                            </span>
                          </div>
                          <div className="text-[12px] text-muted-foreground">
                            {result.recommendation_reason}
                          </div>
                        </div>
                        <button
                          onClick={() => handleSetStrategy(result.recommended_strategy as PDFStrategy)}
                          disabled={updatingStrategy || config.pdf_strategy === result.recommended_strategy}
                          className="px-4 py-2 text-[13px] bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shrink-0"
                        >
                          {updatingStrategy && <Loader2 className="w-4 h-4 animate-spin" />}
                          {config.pdf_strategy === result.recommended_strategy ? "已设为默认" : "设为默认策略"}
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-border flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-[13px] rounded-lg hover:bg-accent transition-colors"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}
