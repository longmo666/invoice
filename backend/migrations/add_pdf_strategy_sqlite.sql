-- SQLite 版本：添加 pdf_strategy 字段
ALTER TABLE ai_configs ADD COLUMN pdf_strategy VARCHAR(50) DEFAULT 'convert_to_images' NOT NULL;
