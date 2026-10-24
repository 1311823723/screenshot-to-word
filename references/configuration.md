# document.json 配置

配置中的页码均指 `pages.json` 的 **1 起始片段号**，不指原始截图号、PDF 印刷页码或最终 Word 页码。`page` 与 `block_index` 共同定位原始 MinerU 块；`block_index` 使用块的 `index` 字段，不是数组下标。

以下只是字段示例，不能照搬标题、排除页或续表关系。先阅读图像和 `inventory.md` 再填写。

```json
{
  "title": "从封面读取的真实文档标题",
  "company": "从封面读取的机构名称",
  "cover": {"source_page": 1, "logo_bbox": [0.12, 0.01, 0.48, 0.10]},
  "exclude_pages": [1, 3],
  "toc_before_page": 4,
  "toc_levels": 3,
  "table_joins": [],
  "heading_overrides": [],
  "text_replacements": [],
  "ignore_blocks": [],
  "min_figure_area": 0.0
}
```

- `title`：必填，精确保留原文，可用 `\n` 表示封面换行。
- `company`：可省略，不能编造。`cover`：可省略；提供时绘制可编辑封面，`source_page` 为封面图源，`logo_bbox` 是相对该片段宽高的归一化裁框。没有 logo 不填裁框。封面片段必须同时放进 `exclude_pages`，避免重复。
- 不创建封面时，输入中的 `doc_title` 会原位保留为 Title 样式。若不需要目录，不填 `toc_before_page`；文档存在目录时原则上重建。
- `exclude_pages`：只排除确认的旧封面/旧目录等整片段。若同一片段同时含目录和正文，不得整片排除，应通过 `ignore_blocks` 仅排除旧目录/旧标题块。
- `toc_before_page`：在该源片段开始之前插入真实目录，之后正文自然流排。不要每个片段插分页。
- `table_joins`：经看图核实后填写，例如 `{"page":5,"block_index":0,"reason":"上页同一表格的续表，列关系一致"}`。脚本还要求它紧接前一表格且列数一致，否则报错。不同网格的续表需人工修订网格后重建，不得强行合并。
- `heading_overrides`：识别器误判时指定，例如 `{"page":9,"block_index":3,"level":2,"reason":"原目录列为二级章节"}`。普通文本、table_caption 等叶块可覆盖；表格主体不能直接当标题。
- `text_replacements`：仅限对照原图确认的字符纠正，格式为 `{"page":32,"old":"被误识别的文字","new":"原图清晰可见的文字","reason":"对照裁图核实"}`。默认只作用于该页的可编辑文本，不改图片。涉及跨两页同一单元格的断词、断行应通过局部结构修订处理，不能盲目全局替换。
- `ignore_blocks`：排除核实过的拼接残边或重复块，格式为 `{"page":3,"block_index":0,"reason":"旧目录标题"}`。排除会写入报告，不能为了消除报错排除真正内容。
- `min_figure_area`：默认 0，即不按面积静默丢图。只有确认大量小块是边框碎片时才配置阈值，并核对被跳过的列表。

可选版式字段：`page_width_cm` 默认21、`page_height_cm` 默认29.7、`margin_cm` 默认2、`body_font_pt` 默认11、`figure_max_height_cm` 默认20.5。A4 是这组中文办公文档的已验证惯例，其他源文件可按实际调整。表格宽度自动从纸张和边距计算，不写固定网格宽度。

自动标题识别先使用原目录对应关系，再参考 `paragraph_title` 的数字层级；数字列表不自动提升为标题。原目录与正文不一致时要看图确认，不能擅自重编号。

## 正式版生成要求

调用 build_docx.py 必须另传 --reviews content_review.json。它来自 inspect_result.py 的模板，需逐个看图完成，[格式与判断规则](content-review.md) 不放进 document.json 内。源码表格禁止通过 ignore_blocks 直接跳过，必须使用有证据的表格处理决定。

可选 east_asia_font 指定本设备已安装且覆盖原文的字体；修改字体应在刷新目录之前完成。对内容和结构作修订时优先改配置/识别修订副本并重新构建，保留原始识别结果。直接改最终 Word 之后必须重做验收；若改变表格顺序或表内图位置，还要同步其来源记录，不能留下过期的表号/图号。
