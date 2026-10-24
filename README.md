# Screenshot to Word

将一组有序文档截图还原成可编辑 Word 的 Agent Skill。正文、标题和普通表格保留原生编辑能力，目录使用真实 TOC 域，监控图和表内图片按来源恢复。

An Agent Skill for reconstructing editable Word documents from ordered screenshots, with source review and final artifact verification.

**状态：本地开发，尚未发布到 GitHub，尚未选定开放许可证。** 当前已实现 Windows x64 + Python 3.12 + MinerU 4.0.12 + Microsoft Word 桌面版流程。它不是免核对的一键转换器，不保证任意宿主、操作系统或硬件开箱即用。

## 使用

将整个技能目录交给支持本地文件与命令执行的代理，直接说：

> 请读取这个目录里的 SKILL.md，把我指定图片目录中的图片还原为可编辑 Word，按技能完成源图核对、目录刷新和最终验收。

图片路径和技能路径直接写在消息里即可，配置由代理根据源图填写。支持技能导入的宿主可按自身规则导入该目录；本项目不承诺所有宿主都有同一安装命令。

首次运行依照 [环境与安装](references/environment.md) 部署免费依赖和本地模型。Word 须合法安装并允许本地自动化。默认不上传原始资料，也不把模型下载当作文档上传授权。

详细可复制提示词见 [中文提示词](docs/prompts.zh-CN.md)。

## 核心处理

- 自然排序、长图分片并保存源文件及纵向位置映射。
- 用结构识别结果恢复标题、正文、合并表格和图片。
- 每个表格候选先对照原图，避免把监控图误作虚假数据表。
- 表内小图映射回对应原生单元格，不以空白格冒充恢复完成。
- 实际 Office 引擎刷新目录，渲染逐页核验。
- 最终统计重新读取交付文件，报告与 Word/PDF 哈希绑定；源资料缺失单独说明。

## 仓库结构

```text
screenshot-to-word/
├── SKILL.md                 # 代理入口
├── agents/openai.yaml       # 可选的宿主界面元数据
├── scripts/                 # 分片、构建、检查、安装与打包工具
├── references/              # 环境、配置、内容核对和交付规则
├── examples/                # 合成数据生成器与示例配置
├── tests/                   # 内容丢失和旧报告等回归测试
├── docs/                    # 设计依据、提示词、路线图、发布流程
└── .github/                 # CI 与问题反馈模板
```

## 开发检查

在独立 Python 3.12 环境中：

```powershell
python -m pip install -r requirements-dev.txt
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

普通开发检查不下载 OCR 模型、不启动 Word、不上传文档。CI 配置包含 Windows 和 Linux 的纯 Python 检查；这不代表 Linux 的 OCR/Office 全流程已支持。CI 尚需推送后在 GitHub 上实际验证。

生成完全合成的演示输入：

```powershell
python examples/make_demo.py --output work/demo
```

演示直接提供结构数据，用于测试构建环节，不冒充实际 OCR；生成后仍需人工核对。详见 [示例](examples/README.md) 与 [贡献指南](CONTRIBUTING.md)。

## 发布准备

打包前运行检查，再执行：

```powershell
python scripts/package_skill.py --output dist
```

打包只收录技能入口、脚本、参考资料和必要元数据；会生成文件校验清单。发布前仍需选定许可证、完成新设备冷安装与完整文档验证，见 [发布清单](docs/releasing.md) 和 [路线图](docs/roadmap.md)。

## 限制与许可

源图模糊、遮挡、缺页以及模型错误需要代理对照图片判断；程序无法证明代理真的看过图，也无法自动证明语义完全准确。`replacement_characters=0` 不等于没有缺字。报告只对实际核验的文件版本有效。

本仓库暂未授予开放许可证；正式公开分享前由维护者选定。第三方工具、模型、字体和 Office 分别遵守其自身许可，打包本技能不包含这些第三方二进制。研究依据见 [结构设计](docs/design.md)。
