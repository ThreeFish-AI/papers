---
name: doc-translator
description: 将 PDF 格式或 Web Page 格式的源文档转换成保持原排版格式的 Markdown 格式精译中文文档。
allowed-tools: filesystem, data-extractor, zai-mcp-server, web-reader, web-search-prime, time
---

# Document Translator

按照下文 Workflow，使用相应的工具（data-extractor 可以读取 PDF 与 Web Page 两种类型文档的文本、图片、公式、表格）阅读源文档（PDF、Web Page 等）内容（文字、图片、公式、表格等），将文档内容以原排版格式全量转换为 Markdown 格式，并将其中的文字部分逐字精译成中文，然后将之保存到本地指定路径的「目标 Markdown 文档」中。

## Workflow

1. 根据源文档内容按段落长短制定多个批次（每个批次最多处理不超过 30 Pages，不过超过 60 个段落，不过超过 6000 Words）处理文档的任务计划，后续逐批次地对这些内容进行转换和精译处理；创建一个用于接收完整文档内容的「目标 Markdown 文档」；
2. [循环]逐批次处理源文档的内容：
   1. 检查所有批次是否处理完成。若是，退出处理循环；若否，创建一个用于接收下个批次处理结果的「批次 Markdown 文档」；
   2. 使用 data-extractor 的 convert_pdf_to_markdown（单文档）或 batch_convert_pdfs_to_markdown（批文档）工具阅读 PDF 类型源文档的指定批次内容，并转换成目标 Markdown 格式；
   3. 使用 data-extractor 的 convert_webpage_to_markdown（单文档）或 batch_convert_webpages_to_markdown（批文档）工具阅读 Web Page 类型源文档指定批次内容，并将之转换成目标 Markdown 格式；
   4. 从 data-extractor 的 convert_xxx_to_markdown 或 batch_convert_xxxx_to_markdown 远程调用中接收 Markdown 格式的文本内容、图片、公式、表格等；
   5. 将从 data-extractor 远程调用获取的图片资源文件保存到本地指定的图片存放路径；
   6. 将从 data-extractor 远程调用获取的 Markdown 格式文本内容、公式、表格写入「批次 Markdown 文档」；
   7. 检查并修正「批次 Markdown 文档」中图片、公式、表格的引用方式、引用位置、显示格式等；
   8. 检查并修正「批次 Markdown 文档」中内容的整体布局（与源文档保持一致）；
   9. 检查并修正「批次 Markdown 文档」转换与翻译的正确性，修复发现问题；
   10. 将「批次 Markdown 文档」的内容追加到「目标 Markdown 文档」；
   11. 移除当前批次的「批次 Markdown 文档」；
3. 检查「目标 Markdown 文档」整体转换与翻译的正确性，修复发现问题；

## Special Note

**文档对象**

- 「源文档」：要被转换或翻译的文档；
- 「目标 Markdown 文档」：存放完整转换与翻译结果的文档。其存放路径是源文档所在路径下的 translate/ 路径（比如源文档路径是 `/path/to/source_docs/doc_A.pdf`，那么「目标 Markdown 文档」路径是 `/path/to/source_docs/translate/doc_A.md`）；
- 「批次 Markdown 文档」：存放处理过程中某个批次转换与翻译结果的临时文档。其存放路径与「目标 Markdown 文档」一致（比如源文档路径是 `/path/to/source_docs/doc_A.pdf` 的第 3 批次对应的「批次 Markdown 文档」的路径是 `/path/to/source_docs/translate/doc_A_3.md`，其中后缀「3」代表批次号）；

**图片资源**

- 图片资源路径是「源文档」所在路径（注意不是项目所在路径，也不是 data-extractor 服务运行路径）下的 `images/doc_name/` 路径（比如「源文档」路径是 `/path/to/source_docs/doc_A.pdf`，那么图片资源存放在 `/path/to/source_docs/images/doc_A/` 路径下）；
- 图片保存在本地的文件名称需参考源文档中图的说明，或基于对图片内容的理解，使用简短且有识别性的英文名称；

## Checklist

1. 检查核对批次内容在源文档与目标文档中的内容一致性，如中英文内容是否对等，翻译得是否准确和完整；
2. 检查核对批次内容在源文档与目标文档中的布局一致性，如目录结构是否一致，整体排版格式是否相同，图片、公式、表格等的引用位置是否一致，显示格式是否显示正确；
3. 考虑 Markdown 格式语法与排版因素，如使用 Markdown 语法组织源文档中的表格内容，使用 LateX 语法组织源文档中的数学公式内容；
4. 考虑单次能够处理的内容最大长度因素（建议最多每次处理 30 Pages，或者 6000 Words）；
5. 可借助 zai-mcp-server 工具理解图片内容；
6. 不要在其他路径创建路径或文件，临时的文件要及时清理；

无论源文件多大，坚持处理完其中全部内容。
