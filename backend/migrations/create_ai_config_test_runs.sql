-- 创建 AI 配置样本测试运行记录表
CREATE TABLE IF NOT EXISTS ai_config_test_runs (
    id SERIAL PRIMARY KEY,
    config_id INTEGER NOT NULL REFERENCES ai_configs(id),
    tester_user_id INTEGER NOT NULL REFERENCES users(id),

    -- 测试文件信息
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,  -- image, pdf
    invoice_type VARCHAR(50) NOT NULL,  -- vat_special, vat_normal, railway_ticket

    -- 测试模式
    test_mode VARCHAR(50) NOT NULL,  -- image_single, pdf_compare
    tested_strategy VARCHAR(50),  -- direct_pdf, convert_to_images

    -- 测试结果
    success BOOLEAN NOT NULL,
    request_path VARCHAR(500),
    execution_path VARCHAR(500),
    latency_ms INTEGER,
    error_message TEXT,

    -- 响应数据
    raw_response TEXT,
    parsed_result TEXT,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建索引
CREATE INDEX idx_ai_config_test_runs_config_id ON ai_config_test_runs(config_id);
CREATE INDEX idx_ai_config_test_runs_tester_user_id ON ai_config_test_runs(tester_user_id);
CREATE INDEX idx_ai_config_test_runs_created_at ON ai_config_test_runs(created_at);

-- 添加注释
COMMENT ON TABLE ai_config_test_runs IS 'AI 配置样本测试运行记录';
COMMENT ON COLUMN ai_config_test_runs.config_id IS 'AI 配置 ID';
COMMENT ON COLUMN ai_config_test_runs.tester_user_id IS '测试人员 ID';
COMMENT ON COLUMN ai_config_test_runs.file_name IS '文件名';
COMMENT ON COLUMN ai_config_test_runs.file_type IS '文件类型: image, pdf';
COMMENT ON COLUMN ai_config_test_runs.invoice_type IS '发票类型: vat_special, vat_normal, railway_ticket';
COMMENT ON COLUMN ai_config_test_runs.test_mode IS '测试模式: image_single, pdf_compare';
COMMENT ON COLUMN ai_config_test_runs.tested_strategy IS '测试的策略: direct_pdf, convert_to_images';
COMMENT ON COLUMN ai_config_test_runs.success IS '是否成功';
COMMENT ON COLUMN ai_config_test_runs.request_path IS '请求路径';
COMMENT ON COLUMN ai_config_test_runs.execution_path IS '执行路径';
COMMENT ON COLUMN ai_config_test_runs.latency_ms IS '延迟（毫秒）';
COMMENT ON COLUMN ai_config_test_runs.error_message IS '错误信息';
COMMENT ON COLUMN ai_config_test_runs.raw_response IS '原始响应（JSON）';
COMMENT ON COLUMN ai_config_test_runs.parsed_result IS '解析结果（JSON）';
