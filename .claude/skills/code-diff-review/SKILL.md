---
name: code-diff-review
description: Use when reviewing local git changes for UI/style/logic impact, and when generating or updating a shared local test report for other agent sessions.
---

# Code Diff Review (测试角色)

## 职责
检查代码修改，生成测试报告，根据结果触发下一个角色（开发修复或验收通过）。

## 执行流程

### 1. 读取 task.json
```bash
cat .agent-communication/task.json
```

确认 action 为 `test_requested` 再继续。
提取 `acceptance_criteria` 作为验收标准。

### 2. 检查现有报告
```bash
cat .code-review-reports/latest-report.md 2>/dev/null
```

- status `⚠️ 待修复`：更新报告
- status `✅ 已修复` 或 `✅ 可以提交`：归档后生成新报告

### 3. 执行代码检查
```bash
git status
git diff --stat
git diff --name-only
# 按需检查具体文件
git diff <file>
npm run lint
npm run type-check
```

检查重点：
- 样式：是否硬编码颜色、CSS变量复用、主题一致性
- 组件：仅样式变化还是含逻辑变化、是否引入新风险
- 质量：lint / type-check 结果

### 4. 生成/更新报告
写入 `.code-review-reports/latest-report.md`：

```markdown
---
generated: <ISO时间>
commit: <hash>
branch: <branch>
status: ⚠️ 待修复 | ✅ 可以提交
---

# 代码修改检查报告

## 修改概览
## 详细检查结果
### 样式文件
### 组件文件
### 质量检查
### 依赖变更

## 修复建议
## 结论
```

### 5. 根据结果更新 task.json

**发现问题（status: ⚠️ 待修复）**：
```json
{
  "action": "dev_requested",
  "from": "test-agent",
  "to": "dev-agent",
  "iteration": "<当前iteration>",
  "priority_issues": [
    { "id": 1, "severity": "high", "description": "...", "files": ["..."] }
  ]
}
```
写完后立即调用 `code-fix` skill 切换为开发角色。

**验收通过（status: ✅ 可以提交）**：
```json
{
  "action": "approved",
  "from": "test-agent",
  "to": "orchestrator",
  "iteration": "<当前iteration>"
}
```
归档任务：
```bash
mkdir -p .agent-communication/history
timestamp=$(date +%Y%m%d-%H%M%S)
cp .agent-communication/task.json .agent-communication/history/task-$timestamp.json
```

## 注意事项
- 不读旧报告直接重跑 → 重复劳动
- 报告必须写 status，后续角色靠它决策
- iteration 超过 5 还未通过 → 将 action 写为 `blocked`，说明卡点，等待 orchestrator 介入
