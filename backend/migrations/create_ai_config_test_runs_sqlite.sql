-- SQLite 版本：创建 AI 配置样本测试运行记录表
CREATE TABLE IF NOT EXISTS ai_config_test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id INTEGER NOT NULL,
    tester_user_id INTEGER NOT NULL,

    -- 测试文件信息
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    invoice_type VARCHAR(50) NOT NULL,

    -- 测试模式
    test_mode VARCHAR(50) NOT NULL,
    tested_strategy VARCHAR(50),

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (config_id) REFERENCES ai_configs(id),
    FOREIGN KEY (tester_user_id) REFERENCES users(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_ai_config_test_runs_config_id ON ai_config_test_runs(config_id);
CREATE INDEX IF NOT EXISTS idx_ai_config_test_runs_tester_user_id ON ai_config_test_runs(tester_user_id);
CREATE INDEX IF NOT EXISTS idx_ai_config_test_runs_created_at ON ai_config_test_runs(created_at);
