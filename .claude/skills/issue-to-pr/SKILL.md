---
name: issue-to-pr
description: 自动拉取 GitHub issue，驱动开发-测试闭环，验收通过后自动 commit 并创建 PR
---

# Issue to PR (自动化流程)

## 职责
从 GitHub issue 到 PR 的全自动流程：拉取 issue → 开发 → 测试 → 修复 → commit → PR。

## 前置条件
- 已安装 `gh` CLI 并完成认证
- 当前分支干净或已 stash
- 有权限创建分支和 PR

## 执行流程

### 1. 拉取待处理 issue
```bash
# 获取标签为 "bug" 或 "enhancement" 且未分配的 issue
gh issue list --label "bug,enhancement" --state open --json number,title,body,labels --limit 5
```

选择策略：
- 优先处理 `priority:high` 标签
- 或让用户选择具体 issue

### 2. 解析 issue 内容
提取：
- issue number
- title（作为分支名和 commit message 前缀）
- body（作为需求描述）
- acceptance criteria（如果 body 中有明确的验收标准）

### 3. 创建功能分支
```bash
git checkout -b fix/issue-<number>-<sanitized-title>
# 或 feature/issue-<number>-<sanitized-title>
```

### 4. 初始化任务并驱动闭环
调用 `orchestrator` skill：
```json
{
  "requirement": "<issue body>",
  "acceptance_criteria": ["从 issue 提取的验收标准"],
  "issue_number": <number>
}
```

orchestrator 驱动 dev → test → fix 循环，直到 `action: approved`。

### 5. 验收通过后自动 commit
```bash
git add .
git commit -m "fix(#<number>): <issue title>

<issue body 摘要>

Closes #<number>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

### 6. 推送并创建 PR
```bash
git push -u origin fix/issue-<number>-<sanitized-title>

gh pr create \
  --title "Fix #<number>: <issue title>" \
  --body "$(cat <<'EOF'
## 解决的问题
Closes #<number>

## 变更说明
<从测试报告提取的修改概览>

## 测试结果
✅ 代码检查通过
✅ 功能验收通过

详见测试报告：`.code-review-reports/latest-report.md`

🤖 Generated with Claude Code
EOF
)" \
  --base main
```

### 7. 返回 PR URL
输出 PR 链接供用户查看。

## 错误处理

- issue 无法解析 → 跳过，处理下一个
- 开发-测试闭环超过 5 次迭代未通过 → 标记 issue 为 `blocked`，添加评论说明卡点
- commit 或 PR 创建失败 → 保留分支，输出错误信息

## 使用示例

```bash
# 用户发起
"请用 issue-to-pr skill 自动处理待办 issue"
```

Agent 自动完成：拉取 → 开发 → 测试 → commit → PR，全程无需人工介入。
