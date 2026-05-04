# moying-agent
基于 Dramatica 故事工程学的网文全流程自动化 Agent。大纲→写作→审计→发布→评论→数据 全闭环。
# 墨影 Moying - 网文全流程自动化 Agent
🔥 基于 **Dramatica 故事工程学** 的顶级网文创作 AI | 番茄/起点通用 | 大纲→写作→发布→评论→数据 全闭环

## 🎯 核心特性
✅ **Dramatica-Flow 闭环创作**：故事骨架 → 约束生成 → 自动审计 → 自动修订 → 确认通过才下一章
✅ **长篇永久记忆**：Chroma 轻量向量库，1000章不崩人设、不忘伏笔、剧情连贯
✅ **三重零AI味引擎**：规则清洗（删除AI模板词）+ AI润色（模拟真人）+ 格式校准（1句1段）
✅ **番茄/起点自动发布**：模糊匹配选择器（防改版）+ Cookie加密持久化（免登录）+ 人类行为模拟（防封号）
✅ **智能评论分析**：情绪分类 + 角色偏好 + 剧情优化建议
✅ **数据监控分析**：爬取数据中心 + 生成带图表的Excel报告 + 基于数据的写作建议
✅ **FastAPI 接口服务**：Swagger 文档 + 后台任务 + 状态查询
✅ **工业级稳定性**：自动重试 + 详细日志 + 文件备份 + 断点续传

## 🚀 快速启动
### 1. 环境要求
- Python 3.9 ~ 3.12（推荐3.10）
- 6.5GB+ 内存（无本地大模型，仅调用API）
- Windows/Mac/Linux全平台支持

### 2. 安装依赖
```bash
# 克隆项目
git clone https://github.com/wulaotou-bit/moying-agent.git
cd moying-agent

# 安装Python依赖
pip install -r requirements.txt

# 安装浏览器内核
playwright install chromium
