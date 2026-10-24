# 合成演示

make_demo.py 生成虚构的单页图片、来源清单、结构数据、配置与待核对内容记录。没有真实项目内容、客户信息或模型依赖。

从仓库根目录运行：

```powershell
python examples/make_demo.py --output work/demo
```

打开生成的 source.png，对照查看 content_review.json：图表位于 row=1、col=1，裁图坐标已提供，但 source_checked 仍为 false、decision 为 pending。只有实际核对后才能填写正确决定并生成 Word，示例不会自动“勾选通过”。

确认后构建：

```powershell
python scripts/build_docx.py --result work/demo/result.json --pages work/demo/pages.json --config work/demo/document.json --reviews work/demo/content_review.json --output work/demo/demo.docx
```

此示例直接提供结构数据，只演示原生表和表内图片恢复。它没有执行 OCR、不含目录，也不证明自动目录或新机器环境通过。完整识别流程和验收仍按 SKILL.md 执行。
