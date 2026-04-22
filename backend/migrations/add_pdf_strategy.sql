-- 添加 pdf_strategy 字段
ALTER TABLE ai_configs ADD COLUMN pdf_strategy VARCHAR(50) DEFAULT 'convert_to_images' NOT NULL;

-- 更新注释
COMMENT ON COLUMN ai_configs.pdf_strategy IS 'PDF 处理策略: direct_pdf, convert_to_images';
