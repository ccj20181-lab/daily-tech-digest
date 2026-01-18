# 2026年1月18日 科技简报

**导语：** 2026 年的 tech 圈依然喧嚣。jQuery 意外地发布了 4.0 大版本，而 AI 编程的讨论已从“能否替代”转向“如何烧钱”。Steve Yegge 甚至宣称 IDE 即将消亡。与此同时，国产手机出货量重回第一，开发者社区在探讨 RustDesk 被反诈中心联系的技术与法律边界。

### 1. 今日热点

*   **jQuery 4.0.0 正式发布** ([链接](https://blog.jquery.com/2026/01/17/jquery-4-0-0/))
    *   **为何重要：** 在前端框架日新月异的 2026 年，统治了 Web 十余年的 jQuery 发布了 4.0 大版本。这不仅是一次怀旧，更是为了维护庞大的遗留代码库。这一版本移除了对旧浏览器的支持，现代化了 API，证明了“古老”的技术仍有其生命力。

*   **Steve Yegge：2026 年是“IDE 消亡之年”** ([链接](https://www.infoq.cn/article/SJNt2c2Sh5AgO4LbiSC8?utm_source=rss&utm_medium=article))
    *   **为何重要：** 著名开发者 Steve Yegge 抛出惊人言论，认为传统 IDE 将被 AI 代理取代，并提出“每天烧掉 500-1000 美元 Token”才是合理的开发成本。这一激进观点引发了关于 AI 编程经济效益和工具演变的激烈辩论。

*   **RustDesk 用户遭遇反诈中心联系** ([链接](https://www.v2ex.com/t/1186463))
    *   **为何重要：** V2EX 热帖显示，使用开源远程控制软件 RustDesk 可能会触发国内反诈预警。这反映了在电信诈骗高压打击下，国产/开源网络工具在用户环境中的合规性挑战，引发了开发者对“技术中立”与“实际风控”的讨论。

*   **华为手机 2025 年出货量重回全球第一** ([链接](https://www.solidot.org/story?sid=83326))
    *   **为何重要：** 经历过多轮制裁后，华为在 2025 年实现了强势反弹，重新夺回全球出货量榜首。这一里程碑事件标志着国产供应链在极限施压下的韧性，以及全球智能手机市场格局的剧变。

*   **用 Claude Code 撰写《过山车大亨》** ([链接](https://labs.ramp.com/rct))
    *   **为何重要：** 这是一个极具观赏性的实验，展示了 Claude 3.5/4 等模型在理解复杂上下文、处理遗留代码库和实时协作方面的能力，被视作 AI 辅助游戏开发的最佳实践案例之一。

### 2. 技术趋势

*   **AI 编程进入“深水区”与“高消费”时代**
    *   从 Cursor“从零写浏览器”引发的争议，到业界探讨每天消耗数百美元 Token 的合理性，AI 编程正从“写函数”转向“构建系统”。InfoQ 分析指出，简单的代码拼装已成过去，现在比拼的是如何用 AI 管理复杂的工程架构。

*   **RISC-V 架构生态加速成熟**
    *   Anolis OS 23.4 发布，宣布全面支持 RVA23 RISC-V 架构。这一动态表明，除 x86 和 ARM 之外，开源指令集 RISC-V 在服务器和操作系统层面的支持正日益完善，国产芯片生态正借此加速布局。

*   **AI Agent 正在接管所有软件入口**
    *   腾讯云推出 AI 原生 Widget，百度文心内测“多人多 Agent”群聊。趋势显示，传统的 GUI（图形用户界面）正在与 CUI（对话用户界面）融合，Agent 不再是简单的 Chatbot，而是能够调用组件、执行任务的“数字员工”。

### 3. 产品观察

*   **Chrome 原生垂直标签页** ([链接](https://www.v2ex.com/t/1186536))
    *   Chrome 终于在原生层面推出了垂直标签页功能。虽然这只是一个 UI 调整，但对于超多标签页用户来说是生产力福音，也标志着浏览器在经过多年插件依赖后，开始回收核心体验的控制权。

*   **Pixel 网速显示神器** ([链接](https://sspai.com/post/104972))
    *   少数派推荐的一款与 Pixel 深度集成的网速显示工具。在 Android 15/16 时代，状态栏的极简主义与信息密度的平衡依然是痛点，这款工具通过“宛如原生”的设计解决了用户的电量与流量焦虑。

*   **Opera One R3：重构 AI 底层** ([链接](https://www.oschina.net/news/397195))
    *   Opera 浏览器发布 R3 更新，不仅优化了 AI 体验，还重构了浏览器底层架构。这预示着 2026 年的浏览器不再仅仅是网页渲染器，而是承载本地 LLM 和 AI 功能的操作系统雏形。

### 4. 推荐阅读

*   **ASCII characters are not pixels** ([链接](https://alexharri.com/blog/ascii-rendering))
    *   HN 高分文章。深入探讨了 ASCII 艺术的渲染原理，解释了为什么字符不仅仅是像素，以及如何正确处理字形网格。对于复古游戏爱好者和图形学开发者是极佳的科普。

*   **jQuery 4.0.0 Released** ([链接](https://blog.jquery.com/2026/01/17/jquery-4-0-0/))
    *   值得前端开发者一读的官方博文。看看这个改变了 Web 历史的库在 2026 年是如何做减法（移除旧 IE 支持）和做加法（现代化模块）的。

*   **The recurring dream of replacing developers** ([链接](https://www.caimito.net/en/blog/2025/12/07/the-recurring-dream-of-replacing-developers.html))
    *   深度思考文章。回顾了历史上无数次试图用“低代码”或“AI”取代开发者的失败尝试，冷静分析了当前 AI 编程浪潮的泡沫与现实。

*   **IDE消亡之年？** ([链接](https://www.infoq.cn/article/SJNt2c2Sh5AgO4LbiSC8?utm_source=rss&utm_medium=article))
    *   编译 Steve Yegge 的犀利观点。虽然观点偏激，但他关于 AI 代理将如何改变软件开发流程的推演极具启发性，值得一读。

*   **AI 的下一个十年：从技术拐点到工程落地的路线图** ([链接](https://www.infoq.cn/article/wLeViF4hSl0WQrw3r2cQ?utm_source=rss&utm_medium=article))
    *   InfoQ 深度报道。适合技术管理者阅读，探讨了 AI 从“玩具”走向“工程化”过程中必须解决的落地问题、成本控制与架构选型。