# 内容核对记录

inspect_result.py 加 --pages 后生成 content_review.template.json 和 source_review 原表候选裁图。将模板复制为 content_review.json，在实际看过图片后填写。文件不是给用户的问卷，由代理完成。模板的待定项不是核对完成的证据。

每个未排除的源表格候选用 page（1 起始裁切片段号）与 block_index（MinerU 的 index）定位：

```json
{
  "schema_version": 1,
  "table_reviews": [
    {
      "page": 5,
      "block_index": 3,
      "source_checked": true,
      "decision": "native_table",
      "evidence": "原图确为两列测试配置表，第二行右侧有一张监控图，文字与列关系已核对",
      "visual_content": "present",
      "cell_images": [
        {
          "row": 1,
          "col": 1,
          "source_page": 5,
          "bbox": [0.45, 0.3, 0.8, 0.45],
          "evidence": "此框仅含该单元格原有监控图，未包含邻格文字"
        }
      ]
    }
  ]
}
```

这只是坐标格式示例，不能复制坐标用于新文档。row/col 为从0开始的**逻辑网格**，合并单元格指向左上角。source_page 与 bbox 指向 pages.json 中的原图裁切片段，bbox 为相对宽高的 0—1 坐标。一个格有多张图可多次指定；文字保留原生，图追加在该格内。图的高宽在排版后仍须目视核对。

三种决定：

- native_table：原图确为表格。visual_content 为 none 表示检查过且格内无图片；present 表示有图片，必须填写 cell_images。HTML 中即使没有 img 标签，也可能已在识别阶段丢失小图，所以必须看源图。
- figure：原图为图表/监控图，OCR 错当表格。使用原图裁框恢复图片，不创建假的原生表。必要时填 bbox 覆盖识别器错误边框。检查相邻 image/chart 块，避免重新裁全图后又保留重叠半图。
- omit_artifact：源图确认是重复识别、拼接残边等，不承载真实内容。必须说明证据，且确认该位置的真实图或文字已由其他块完整恢复。不能仅因内容可疑就删除。

source_checked 为 true、evidence 和 visual_content 必须真实填写。pending 或 unknown 会阻止生成。风险提示只是导航，不是“出现 Year 就必是假表”等内容删除规则。

全部表格候选均应核对，包括普通数值表和无风险提示的表。正文、标题、图片也有独立验收要求，这个表格核对文件不能代替整篇检查。缺失或遮挡原文的位置，写入最终 known_source_issues；源资料不足不能猜补。

命令或 SQL 跨截图接缝时，可能被标为 header、footer、equation，甚至没有生成块。过滤结构标签前对照原图上下边缘，核对语句起止、占位符及续行；有原图依据才合回原句。识别器可能为 `$` 添加转义，不能全局删反斜杠，应逐处辨别源代码本身与输出格式转义。架构图被识别成大量散落文字时，恢复原有图形关系，不能把标签顺次排成正文。

特别检查整段正文被吸收到表格首行合并单元格的情况：对照可见边框，必要时拆回表前正文。空白片段出现“图片为空、没有OCR结果”等说明时，核对是否由识别器生成；风险提示不能作为自动删文规则。整张监控看板被切成多个 chart、表格图例或文本时，应依据原图边界和分区标题确认组合，保留图例、坐标和相对位置；相邻不代表同一张图。表内监控图的列坐标必须按 colspan/rowspan 解析后的逻辑网格填写，不能按可见表头格数推断列号。
