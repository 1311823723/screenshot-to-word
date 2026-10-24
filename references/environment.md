# 新设备部署与运行

## 支持范围

自动安装和渲染脚本面向 **Windows 10/11 64 位桌面电脑**，不依赖 Codex、特定用户名、盘符或旧设备缓存。WorkBuddy 需要读写文件、执行 Python/PowerShell、查看图片和操作 Word 的能力。

macOS/Linux 可按官方方式安装 Python 和 MinerU，但本包的 Word COM 渲染仅适用于 Windows；其他系统须另外适配并验证 Office 引擎，不能宣称跨平台一键可用。

## 必装清单

| 工具或资源 | 版本/组合 | 官方来源及用途 |
|---|---|---|
| Python | 3.12，64 位 | https://www.python.org/downloads/windows/ ，或 WinGet 的 Python.Python.3.12；建立独立 venv |
| MinerU | 固定 mineru==4.0.12 | https://pypi.org/project/mineru/4.0.12/ ；本包结构接口已在此版本验证 |
| Pillow、numpy | 下限见 scripts/requirements.txt | PyPI；切图、像素检测、预览 |
| reportlab | 同上 | PyPI；生成识别用 PDF |
| python-docx、lxml | 同上 | PyPI；生成可编辑段落、标题与合并表格 |
| pypdfium2 | 同上 | PyPI；渲染检查 PDF，无需另装 Poppler |
| MinerU-4_models_onnx | 由固定 MinerU 下载并校验 | OCR、版面和小模型资源 |
| MinerU2.5-Pro-2605-1.2B-GGUF | 同上，包含要求的 GGUF/mmproj 文件 | standard 本地 VLM，llama-cpp 引擎 |
| Microsoft Word 桌面版 | 合法授权、可用 COM | https://www.microsoft.com/microsoft-365/word 或单位软件渠道；刷新目录、保存并导出 PDF |

只安装 Python 库不代表 OCR 已就绪，模型也必须下载和验证。MinerU 基础包支持本方案的 ONNX + llama-cpp；本流程不要求额外安装 PyTorch、CUDA、vLLM、LMDeploy、Tesseract、WPS 或整套 LibreOffice。依据：[官方发布说明](https://github.com/opendatalab/MinerU/releases)、[官方模型说明](https://github.com/opendatalab/MinerU/blob/master/docs/en/usage/model_source.md)。

模型、依赖及缓存需要数 GB 以上空间，具体随平台和版本变化。本次样本机器为 32GB 内存、8GB 显存，这不是通用最低配置。新设备先检查硬件、空间和图形驱动，再跑小样本；硬件不足时说明限制，不擅自转云端或把较低档结果称为同等质量。

## 安装步骤

从技能目录执行：

```powershell
& .\scripts\setup_windows.ps1
```

脚本先发现兼容的 Python，没有时尝试通过 WinGet 安装 Python 3.12 x64；再在当前用户 LocalAppData 下创建独立 DocRestoreTools 环境，从 PyPI 安装依赖和固定 MinerU，从 ModelScope 下载并校验 standard 模型。调用安装脚本意味着执行上述免费软件/模型下载，仍须符合设备实际权限；脚本不购买或安装 Word，不上传原图。

默认用户目录有中文时，使用一个实际可写的纯英文工具目录；路径和盘符由新设备决定，不是固定要求。例如：

```powershell
& .\scripts\setup_windows.ps1 -ToolsRoot 'D:\DocRestoreTools'
# Python 已安装但不在 PATH 时：
& .\scripts\setup_windows.ps1 -ToolsRoot 'D:\DocRestoreTools' -PythonExe '实际Python安装目录\python.exe'
```

没有 WinGet 时，从 Python 官方安装 3.12 x64 后重试。不要下载未知网站的工具合集，不修改机器范围执行策略绕过设备管理。国外网络可用 -ModelSource huggingface。安装失败保留缓存重试，不手工创建模型完成标记。

仅检查路径、不下载或安装：

```powershell
& .\scripts\setup_windows.ps1 -CheckOnly
```

-SkipModels 只用于分阶段安装，模型尚未验证时不能说 OCR 已就绪。离线部署应按官方流程先在联网设备下载校验模型；不同设备仍应创建各自环境，不直接复制整个 venv。

## 激活与处理

安装成功会打印当前设备生成的 Activate-DocumentTools.ps1 路径。每次新终端先点加载该文件，再执行本次任务，不需要改技能里的固定机器路径：

```powershell
. '安装脚本打印的工具目录\Activate-DocumentTools.ps1'
& $env:DOC_RESTORE_PYTHON .\scripts\doctor.py --mineru-exe $env:DOC_RESTORE_MINERU
& $env:DOC_RESTORE_PYTHON .\scripts\prepare_images.py --input '本次原图目录' --work '本次独立工作目录'
& $env:DOC_RESTORE_MINERU parse '工作目录\source_pages.pdf' -o '工作目录\full_result.json' --format middle_json --tier standard
& $env:DOC_RESTORE_PYTHON .\scripts\inspect_result.py --result '工作目录\full_result.json' --pages '工作目录\pages.json' --work '工作目录'
```

激活仅设置当前终端的环境变量，明确使用 ONNX、llama-cpp、local 模型源；不启动后台服务。后续命令保持相同环境。

根据原图完成 document.json 和 content_review.json 后：

```powershell
& $env:DOC_RESTORE_PYTHON .\scripts\build_docx.py --result '工作目录\full_result.json' --pages '工作目录\pages.json' --config '工作目录\document.json' --reviews '工作目录\content_review.json' --output '输出目录\文件_可编辑还原版.docx'
& .\scripts\render_word.ps1 -InputDoc '输出目录\文件_可编辑还原版.docx' -PdfPath '工作目录\final.pdf'
& $env:DOC_RESTORE_PYTHON .\scripts\qa_docx.py --docx '输出目录\文件_可编辑还原版.docx' --pdf '工作目录\final.pdf' --out '工作目录\qa'
```

最后按 [最终交付流程](delivery.md) 生成绑定当前文件的最终验收报告和交付说明。构建成功不代表验收通过。

## 中文字体

生成器会显式设置东亚字体并去掉模板的主题字体回退。仍要确认字体在新设备实际存在，不能靠名称相同猜测覆盖范围。默认宋体适用于具备该字体的 Windows；缺失时可通过系统的语言/字体功能或官方 [Noto CJK](https://github.com/notofonts/noto-cjk) 获取可用的简体中文字体，并在 document.json 的 east_asia_font 中填写安装后的实际字体名。安装或替换字体后重新渲染、刷新目录；不把系统字体二进制附带分享，不修改源文档。

## 故障处理

- 原生 VLM 的 Unicode 映射错误：把新建环境和模型部署在真实可写的 ASCII 路径，不依靠旧设备临时目录或目录联接；原文和输入目录仍可中文。
- 缺模型：使用同组合 models download/verify，不能把 pip 成功当成全部就绪。
- Vulkan/图形驱动错误：检查设备官方驱动和 MinerU 硬件支持，先小样本验证，不承诺任意设备同等速度。
- Word COM 权限或登录会话错误：确认桌面版已安装并激活、用户桌面会话可用、宿主允许 Office 自动化。只关闭脚本创建的实例，不终止用户已有的 Word。
- 缺 Word：从 Microsoft/单位渠道安装合法桌面版；网页版本不能直接替代 COM。其他渲染器须实际适配验收，未做到前只能报告未验收草稿。
