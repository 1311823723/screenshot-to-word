# 结构设计与参考

参考了 [Agent Skills 开放规范](https://agentskills.io/specification) 和 [Anthropic 官方 Skill 模板](https://github.com/anthropics/skills/tree/main/template)。仅参考组织方式，没有复制其功能实现或许可条款。

采用单技能仓库：根目录名与 frontmatter 的 name 都是 screenshot-to-word；SKILL.md 负责触发范围、关键流程与约束。scripts 放可执行工具，references 放运行时按需读取的细节。没有必要的 assets 不建立空目录。

README、贡献说明、CI、路线图和合成示例服务于 GitHub 使用者与维护者，不要求代理执行每个任务前全部阅读。agents/openai.yaml 是可选的宿主元数据，不是跨宿主安装协议；不借它预先授予网络上传、购买软件等权限。

共享边界：模型类型、识别结果、Word 文件与真实源图之间应保留可复查关系。自动检查用于防止已知结构损坏及旧报告误用，不能替代语义核验。不同宿主或渲染器必须分别验证，不按“能读取 SKILL.md”推导为整个流程兼容。
