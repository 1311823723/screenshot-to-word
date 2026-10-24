# 最终交付流程

构建报告记录初稿来源与处理，最终验收报告反映交付的真实文件，两者作用不同。不能把修订前的统计或聊天描述当最终报告。

## 顺序

1. 完成内容、字体、单元格、图片和分页修订。
2. 用实际 Office 引擎刷新完整目录并保存 DOCX，导出同版 PDF。其他引擎不要仅转换出 PDF 就声称目录已更新。
3. qa_docx.py 对最终文件渲染与检查；每轮使用新 QA 目录，避免遗留页图混入。
4. 运行 finalize_delivery.py 的 --make-template 生成待填的验收记录。对照源图、每页成品和所有高风险项，实际核验后填写，不能把所有布尔值一键改真来通过检查。
5. 不带 --make-template 再运行，生成最终报告和随文件交付的说明；有阻断项则修订后重做，禁止把 needs_revision 交付为通过。

示例（从技能目录执行，路径按当前任务填写）：

```powershell
& $env:DOC_RESTORE_PYTHON .\scripts\finalize_delivery.py --docx '输出目录\文件_可编辑还原版.docx' --pdf '工作目录\final.pdf' --qa-report '工作目录\qa\qa_report.json' --build-report '输出目录\文件_可编辑还原版.build_report.json' --reviews '工作目录\content_review.json' --attestation '工作目录\acceptance.json' --out '输出目录' --make-template
# 按真实核验结果完成 acceptance.json，然后去掉 --make-template 再运行同一命令。
```

## acceptance.json 字段

- docx_sha256 / pdf_sha256：模板会记录当前文件。文件变了就重新验证并用新文件的模板，不能直接改哈希掩盖没有核验。
- source_tables_compared：所有表格候选已逐个对照源图。
- mixed_tables_preserved：表内图已逐格保留；若原文确无混合表，在证据中说明后可标完成。
- invented_content_checked：检查过 OCR 的表格和可疑内容，原图不存在的内容已处理，非简单关键词过滤。
- toc_page_numbers_checked：已核对本次实际渲染的目录目标和页码。点击测试或等效的书签目标与正文逐条匹配需有实际证据。
- visual_pages_reviewed：真正看过的最终 PDF 页号，从1开始，最终应覆盖全部页面。
- review_dispositions：每个 build_report 的 review_items 对应一个 item_index。status 为 resolved 或 source_limitation，evidence 写具体来源和处理。未看不能填完成。
- known_source_issues：源图确有缺失/遮挡时填写 title、source_location、description。缺失目录项的 title 必须与 build_report.unmatched_source_toc 对应；不擅自编造正文。
- unresolved_output_issues：还原自身造成的丢图、虚假表、错误目录等，必须修掉后才能通过，不得冒充源资料限制。

## 三种状态

- needs_revision：机械问题、核验未完成、图丢失、报告过期、输出缺陷等，待整改。
- accepted_with_source_limitations：检查记录完成，但有已定位的源图限制，交付时明确说明。
- accepted_with_agent_attestation：机械检查及本轮代理核验记录均完成；仍不能宣称自动逐字准确率100%。

finalize_delivery.py 从最终 DOCX 重新统计原生表格、图片和目录链接，检查 QA、核验记录是否对应当前 Word/PDF，也检查构建时声明的单元格图片在最终原生表格中仍存在。它**不能证明代理真的看了图，也不能自动识别所有模型幻觉**；哈希只能防止误用旧报告。

默认交付：最终 DOCX、“最终验收报告.json”、“交付与待核对说明.md”。用户另要预览时加 PDF。工作目录保存原图清单、切图、OCR、内容核对、构建报告、逐页 QA 图和人工核验记录，支持后续复查；不把这些全部打包给普通接收人。
