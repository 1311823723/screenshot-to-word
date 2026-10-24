# 发布步骤

开发源码已推送到 GitHub，采用 MIT 许可证；尚未发布正式 release。

1. 核实 LICENSE、版权人、所含内容来源和第三方许可边界；保持 README、Skill 元数据及分发包一致。当前经维护者指定采用 MIT，版权人为 1311823723。
2. 确定实际版本，更新 VERSION、CHANGELOG、Skill metadata，保留未完成项与已知限制。
3. 完成 roadmap 的首次公开验证项，记录实际命令、平台与人工验收范围。
4. 执行结构检查、回归测试和 PowerShell 语法检查，检查 git diff 与待上传文件列表。
5. 执行 python scripts/package_skill.py --output dist，查看 ZIP 文件清单与 checksum。
6. 推送到已配置的 GitHub 远程仓库；不能在文档里虚构仓库 URL 或已通过的 Actions 徽章。
7. 在 GitHub 实际检查 CI，通过后创建相应标签和 release，上传已核验的 ZIP；包含新设备运行说明和限制。

打包工具采用白名单，不包括工作目录、真实资料、测试产物、模型、虚拟环境和个人路径。打包白名单不等于允许忽视源文件内的敏感内容，发布前仍检查文本。
