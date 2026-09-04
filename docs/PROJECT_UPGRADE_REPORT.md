# Project Upgrade Report

## 升级前后差异

升级前以独立证券研究原型为叙事中心，容易与腾讯自选股现有行情、AI 搜索、个股解释和比较能力重叠。升级后命名为 **WealthGuard Proofline / WealthGuard 证据防线**，并明确为 **宿主证券产品的证据核验与质量运营增强层**：研究入口展示“补充而非替代”的三段式集成关系，并新增可运行的坏案例后台。名称对应完整产品故事：答案可信之前先核验证据，答案出错之后把失败变成改进。

## 已实现能力与证据

| 能力 | 证据 |
| --- | --- |
| 16 类统一错误分类（条件、严重度、责任层、修复、是否阻断、人工复核） | `backend/wealthguard/quality.py`、`tests/test_quality_console.py` |
| 匿名合成坏案例数据与 API 筛选 | `/api/quality/taxonomy`、`/api/quality/cases` |
| 质量运营页面 | `frontend/src/App.tsx` 的 `QualityView`；支持 5 类筛选、详情和 JSON 导出 |
| 腾讯生态互补定位 | 首页 `IntegrationPanel`、`docs/TENCENT_PORTFOLIO_COMPLEMENT_RESEARCH.md` |
| 面向该定位的 PRD | `docs/PRD_TENCENT_ENHANCEMENT.md` |
| 移动端适配 | `frontend/src/styles.css` 中质量页、集成流和 7 项底部导航断点 |

## 评测结果

项目原有固定种子评测产物为 126/126，官方引用轨迹产物为 39/39；这些是合成回归与资料完整性检查，不是用户准确率。本轮新增 3 个自动测试，覆盖分类完整性、匿名化/筛选和 API 行为。最终命令结果以本次交付说明为准。

本轮验证（2026-09-04）：

- `python -m ruff format --check backend tests scripts`：通过；
- `python -m ruff check backend tests scripts`：通过；
- `python -m pytest`：73 passed，另有 2 条来自 Starlette/TestClient 依赖的弃用警告；
- `python -m wealthguard.evaluation.runner`：126/126；
- `python scripts/run_citation_evaluation.py`：39/39，覆盖 13 份文件；
- `pnpm --dir frontend typecheck`：通过；
- `pnpm --dir frontend build`：通过；
- `pnpm --dir frontend qa:visual`：通过；390 px 中英文页面无横向溢出，桌面双语、证据打开和反馈持久化通过。

## 用户测试状态

**待执行。** 未虚构参与者、完成率、信任分或商业结果。下一步应让 5–8 名金融专业学生或证券产品用户完成财报核验、公告时效核验和条件化比较三项任务。

## 已知限制

- 未连接腾讯自选股、元宝、StockBuddy、微信、券商账户或生产 API；
- StockBuddy 能力来自 2026 年媒体报道，不能视为腾讯正式全量产品承诺；
- 坏案例均为匿名合成评测案例，不代表线上错误分布；
- 修复状态存于代码夹具，尚无持久化工单、权限、多人协作和线上版本对比；
- 当前页面导出 JSON，未实现 CSV/XLSX；
- 用户测试与腾讯内部业务验证均待执行。

## 可安全写入简历的表述

> 基于公开产品资料设计 WealthGuard Proofline（证据防线），将其从独立证券问答原型定位为腾讯自选股/StockBuddy 的证据核验与 AI 质量运营增强层；实现 16 类金融 AI 错误分类、可筛选坏案例后台、匿名导出与回归关联，并以自动测试和可复现评测验证确定性边界。

对应证据：产品研究文档、`quality.py`、质量运营页、自动测试和生成评测产物。

## 不能写入简历的主张

- 已与腾讯、微信、元宝、StockBuddy 或券商完成集成；
- 获得腾讯产品团队认可、上线、灰度或商业转化；
- 真实用户准确率、满意度、节省工时或风险下降；
- 已通过监管、法律、生产安全或投顾合规审查；
- StockBuddy 已向全部用户正式开放。
