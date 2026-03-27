---
name: code-fix
description: 开发工程师读取测试报告并修复问题，完成后通知测试agent复测
---

# Code Fix (开发角色)

## 职责
读取 task.json 和测试报告，执行代码修复，完成后切换为测试角色触发复测。

## 执行流程

### 1. 读取任务
```bash
cat .agent-communication/task.json
```

确认 action 为 `dev_requested` 或 `retest_requested` 再继续。

### 2. 读取测试报告（非首次时）
```bash
cat .code-review-reports/latest-report.md
```

提取：
- `priority_issues`（从 task.json）
- 修复建议（从报告的"修复建议"章节）
- 影响文件列表

### 3. 执行修复

按优先级处理：
1. `severity: high` 优先
2. 参考报告中具体的修复建议
3. 保持现有代码风格

### 4. 本地验证
```bash
npm run lint
npm run type-check
git diff --stat
```

### 5. 更新 task.json → 触发测试角色
```json
{
  "version": "1.0",
  "timestamp": "<ISO时间>",
  "action": "test_requested",
  "from": "dev-agent",
  "to": "test-agent",
  "iteration": "<上次iteration + 1>",
  "branch": "<当前分支>",
  "commit": "<当前commit>",
  "report_path": ".code-review-reports/latest-report.md",
  "fixed_issues": [1, 2],
  "message": "已修复问题ID 1、2，请复测"
}
```

写完后，立即调用 `code-diff-review` skill 切换为测试角色。

## 注意事项
- 修复时不引入新问题
- 不自行 commit，等测试通过后由 orchestrator 决定
- 若某问题无法修复，将 action 写为 `blocked` 并说明原因
