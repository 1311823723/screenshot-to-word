# 发布步骤

本地仓库先维护、测试；目前未创建远程仓库，未发布 release。

1. 维护者选定 LICENSE，核实所含内容来源和第三方许可边界；同步 README 与 Skill 元数据。当前没有擅自选择或授予开放许可。
2. 确定实际版本，更新 VERSION、CHANGELOG、Skill metadata，保留未完成项与已知限制。
3. 完成 roadmap 的首次公开验证项，记录实际命令、平台与人工验收范围。
4. 执行结构检查、回归测试和 PowerShell 语法检查，检查 git diff 与待上传文件列表。
5. 执行 python scripts/package_skill.py --output dist，查看 ZIP 文件清单与 checksum。
6. 用户决定发布时，再创建选定账号下的 GitHub 仓库、设置远程地址并推送；不能在文档里虚构仓库 URL 或已通过的 Actions 徽章。
7. 在 GitHub 实际检查 CI，通过后创建相应标签和 release，上传已核验的 ZIP；包含新设备运行说明和限制。

打包工具采用白名单，不包括工作目录、真实资料、测试产物、模型、虚拟环境和个人路径。打包白名单不等于允许忽视源文件内的敏感内容，发布前仍检查文本。
