---
name: doc-translator
description: Coordinate document translation workflow by orchestrating specialized skills for PDF/web extraction, formatting, and batch processing. Use when translating documents to Chinese Markdown format.
allowed-tools: Skill, filesystem, time
---

# Document Translator (Coordinator)

文档翻译协调器，负责编排整个文档翻译流程，管理各个子技能的协作。

## 协调职责

### 1. 流程编排

- 分析文档类型和大小
- 选择合适的处理策略
- 协调各子技能的执行顺序
- 管理数据流转

### 2. 资源管理

- 创建和管理输出目录
- 协调图片资源存储
- 管理临时文件
- 清理工作环境

### 3. 质量控制

- 监控各步骤执行状态
- 验证输出质量
- 处理错误和异常
- 生成处理报告

## 核心工作流程

### 输入处理

1. **文档识别**

   ```
   输入: 文档路径或 URL
   分析:
   - 文档类型（PDF/Web）
   - 文档大小（页数/字数）
   - 处理复杂度
   ```

2. **策略选择**

   ```
   if 文档类型 == PDF:
       使用 pdf-reader
   elif 文档类型 == Web:
       使用 web-translator

   if 文档大小 > 阈值:
       启用 batch-processor
   else:
       直接处理
   ```

### 处理流程

#### 小文档直接处理

```
doc-translator
    ├── 创建输出目录
    ├── 调用 extractor (pdf-reader/web-translator)
    ├── 调用 markdown-formatter
    ├── 生成最终文档
    └── 清理临时文件
```

#### 大文档批次处理

```
doc-translator
    ├── 创建输出目录
    ├── 调用 batch-processor
    │   ├── 创建批次计划
    │   ├── 循环处理每批:
    │   │   ├── extractor
    │   │   └── markdown-formatter
    │   └── 合并批次结果
    ├── 生成最终文档
    └── 清理临时文件
```

## 目录结构管理

### 输出目录规范

```
/path/to/source/
├── translate/                   # 翻译输出目录
│   ├── document.md              # 最终翻译文档
│   ├── document_report.md       # 处理报告
│   └── images/                  # 图片资源
│       ├── document/            # 文档相关图片
│       └── batch_N/             # 批次临时图片（处理后清理）
└── temp/                        # 临时文件（处理后清理）
    ├── batch_1.md
    ├── batch_2.md
    └── progress.json
```

### 文件命名规范

- 最终文档：`{doc_name}.md`
- 批次文件：`{doc_name}_batch_{N}.md`
- 进度文件：`{doc_name}_progress.json`
- 报告文件：`{doc_name}_report.md`

## 使用方法

### PDF 文档翻译

```
翻译这个 PDF 文档：/path/to/document.pdf
```

### 网页翻译

```
翻译这个网页：https://example.com/article
```

### 批量翻译

```
翻译这些文档：
- /path/to/doc1.pdf
- /path/to/doc2.pdf
- https://example.com/article1
```

### 高级选项

```
翻译这个文档，保存到指定目录：/path/to/document.pdf --output /custom/path/
```

## 质量保证流程

### 1. 预处理检查

- [ ] 文件可访问性验证
- [ ] 文档格式检查
- [ ] 存储空间确认
- [ ] 权限验证

### 2. 处理中监控

- [ ] 进度跟踪
- [ ] 错误日志记录
- [ ] 中间结果验证
- [ ] 资源使用监控

### 3. 后处理验证

- [ ] 完整性检查
- [ ] 格式验证
- [ ] 图片引用检查
- [ ] 链接有效性验证

### 4. 质量报告

生成详细的质量报告：

```markdown
# 文档翻译报告

## 基本信息

- 源文档：document.pdf
- 输出文档：document.md
- 处理时间：2025-12-10 20:00:00
- 总耗时：15 分钟

## 处理统计

- 总页数：150
- 批次数量：5
- 提取图片：23 张
- 提取表格：8 个
- 提取公式：15 个

## 质量检查

- [x] 内容完整性
- [x] 格式正确性
- [x] 图片引用
- [x] 链接有效

## 问题记录

1. 第 75 页图片路径错误 - 已标记
2. 第 120 页表格转换 Error - 已手动修正
```

## 错误处理策略

### 1. 子技能失败处理

- pdf-reader 失败 → 尝试备用提取方案
- web-translator 失败 → 使用 web-reader 作为后备
- markdown-formatter 失败 → 跳过格式化，使用原始内容
- batch-processor 失败 → 切换到单批次处理模式

### 2. 部分失败处理

- 记录失败的具体内容
- 继续处理剩余部分
- 在最终报告中标注问题
- 提供手动修复建议

### 3. 恢复机制

- 支持从失败点恢复
- 保存中间状态
- 避免重复处理已完成部分

## 性能优化

### 1. 智能批次划分

- 根据文档特征动态调整批次大小
- 在章节边界划分批次
- 考虑图片和表格分布

### 2. 并行处理

- 独立文档并行处理
- 批次间流水线处理
- 资源使用优化

### 3. 缓存机制

- 缓存已处理的内容
- 避免重复处理
- 支持增量更新

## 监控和日志

### 处理日志格式

```json
{
  "timestamp": "2025-12-10T20:00:00Z",
  "document": "document.pdf",
  "stage": "extraction",
  "batch_id": 3,
  "status": "processing",
  "message": "正在处理第 61-90 页",
  "progress": 60
}
```

### 性能指标

- 处理速度（页/分钟）
- 内存使用峰值
- 临时文件大小
- 错误率统计

## 与其他技能的集成

### 调用方式

通过 `Skill` 工具调用子技能：

```python
# 调用 PDF 提取
result = await Skill("pdf-reader", {
    "file_path": "/path/to/document.pdf",
    "options": {"extract_images": True}
})

# 调用格式化
formatted = await Skill("markdown-formatter", {
    "content": result["content"],
    "check_images": True
})
```

### 数据传递

- 使用结构化数据格式
- 包含元数据和统计信息
- 支持部分结果传递
- 错误信息传播

## 最佳实践

### 1. 文档组织

- 保持源文档和输出文档的目录结构一致
- 使用清晰的命名规范
- 保留处理历史

### 2. 错误预防

- 预先检查所有前置条件
- 提供清晰的错误消息
- 记录详细的调试信息

### 3. 用户体验

- 提供进度反馈
- 支持中断和恢复
- 生成易于理解的处理报告
