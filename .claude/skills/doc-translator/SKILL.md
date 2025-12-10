---
name: doc-translator
description: 使用相应的工具（data-extractor 可以读取 PDF 与 Web Page 两种类型文档的文本、图片、公式、表格）阅读源文档（PDF、Web Page 等）内容（文字、图片、公式、表格等），将文档内容以原排版格式全量转换为 Markdown 格式的文档，并将其中的文字部分逐字精译成中文，然后将 Markdown 文档保存到本地指定路径。
allowed-tools: Read, Grep, Glob, filesystem, data-extractor, zai-mcp-server, web-reader, web-search-prime, time
---

# Document Translator

将 PDF 格式或 Web Page 格式的源文档转换成保持原排版格式的 Markdown 格式文档；若源文档是英文，将之逐字精译成中文；最后将 Markdown 文档保存到本地的指定路径。

## Instructions

1. 将源文档内容按段落长短分成多个批次，用于后续的精译处理；每个批次最多处理不超过 5 Pages，不过超过 15 个段落，不过超过 10000 Words；
2. 逐批处理：
   2.1. 使用 data-extractor 的 convert_pdf_to_markdown（单文档）或 batch_convert_pdfs_to_markdown（批文档）工具阅读 PDF 类型源文档的指定批次内容，并转换成目标 Markdown 格式；
   2.2. 使用 data-extractor 的 convert_webpage_to_markdown（单文档）或 batch_convert_webpages_to_markdown（批文档）工具阅读 Web Page 类型源文档指定批次内容，并将之转换成目标 Markdown 格式；
   2.3. 从 data-extractor 的 convert_xxx_to_markdown 或 batch_convert_xxxx_to_markdown 远程调用中接收 Markdown 格式的文本内容、图片、公式、表格等；
   2.4. 将从 data-extractor 远程调用获取的图片资源文件保存到本地指定路径；
   2.5. 将从 data-extractor 远程调用获取的 Markdown 格式文本内容、公式、表格写入目标 Markdown 文件；
   2.6. 修正目标 Markdown 文档中内容的整体布局（与源文档保持一致）；
   2.7. 修正目标 Markdown 文档中图片、公式、表格的引用方式、引用位置、显示格式等；
3. 检查文档翻译正确性，修复发现的问题；

## Translate checklist

1. 检查核对内容在源文档与目标文档中的内容一致性，如中英文内容是否对等，翻译得是否准确和完整；
2. 检查核对内容在源文档与目标文档中的布局一致性，如目录结构是否一致，整体排版格式是否相同，图片、公式、表格等的引用位置是否一致，显示格式是否显示正确；
3. 考虑 Markdown 格式语法与排版因素，如使用 Markdown 语法组织源文档中的表格内容，使用 LateX 语法组织源文档中的数学公式内容；
4. 考虑单次能够处理的内容最大长度因素（建议最多每次处理 5 Pages，或者 10000 Words）；
5. 可借助 zai-mcp-server 工具理解图片内容；

## 目标文档

1. 目标文档路径默认使用源文档所在路径下的 translate/ 路径，比如源文档是 /path/to/docs/A.pdf，那么目标文档路径默认是 /path/to/docs/translate/A.md；

## 图片资源

1. 图片资源路径默认使用源文档所在路径下的 images/doc_name/ 路径，比如源文档是 /path/to/docs/A.pdf，那么图片资源路径默认是 /path/to/docs/images/A/；
2. 图片保存在本地的文件名称需参考源文档中图的说明，或基于对图片内容的理解，使用简短且有识别性的英文名称；
