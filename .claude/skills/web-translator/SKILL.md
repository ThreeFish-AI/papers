---
name: web-translator
description: Extract web page content and translate to Chinese while preserving formatting. Use when converting web pages to Markdown format with Chinese translation.
allowed-tools: data-extractor, web-reader, filesystem
---

# Web Translator

专门处理网页内容的提取、转换和中文翻译。

## Workflow

### 1. 内容提取

使用适当的工具提取网页内容：

- `data-extractor.convert_webpage_to_markdown` - 单个网页转换
- `data-extractor.batch_convert_webpages_to_markdown` - 批量网页转换
- `web-reader.webReader` - 备用方案，当 data-extractor 不可用时

### 2. 提取配置

```yaml
extract_main_content: true # 提取主要内容，过滤导航和广告
include_metadata: true # 包含页面元数据
embed_images: false # 图片保存为独立文件
```

### 3. 中文翻译

- 保持原始 Markdown 格式和结构
- 翻译所有文本内容为中文
- 保留代码块、链接和图片引用
- 处理相对链接转换为绝对链接

### 4. 图片处理

- 保存图片到 `/path/to/source/images/web_name/` 目录
- 使用有意义的英文名称命名图片
- 确保图片引用路径正确

## 输入格式

- 单个 URL：`https://example.com/page`
- 多个 URL：列表格式或通配符模式
- 本地 HTML 文件路径

## 输出格式

返回结构化数据：

- `content`: Markdown 格式的翻译内容
- `metadata`: 页面标题、描述等信息
- `images`: 提取的图片列表
- `links`: 页面中的链接信息

## 使用示例

### 基本用法

```
请翻译这个网页：https://example.com/article
```

### 高级用法

```
将这个网页转换为 Markdown 并翻译成中文，需要保留图片和表格：https://example.com/technical-doc
```

### 批量处理

```
批量处理这些网页：
- https://example.com/doc1
- https://example.com/doc2
- https://example.com/doc3
```

## 特殊处理

### 代码块

- 保留原始代码不变
- 添加中文注释说明
- 标注编程语言类型

### 表格

- 转换为 Markdown 表格格式
- 翻译表头和内容
- 保持表格结构完整

### 公式

- 保留 LaTeX 格式
- 添加中文说明
- 确保公式正确显示

## 注意事项

1. **网站权限**：遵守 robots.txt，避免频繁请求
2. **内容质量**：检查翻译准确性，特别是技术术语
3. **格式一致性**：确保 Markdown 语法正确
4. **链接处理**：验证内部链接的有效性
5. **图片描述**：为图片添加中文 alt 文本
