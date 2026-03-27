# Document Writing Agent MVP

一个基于 React + FastAPI + LangChain 的文档撰写 Agent 骨架，支持：

- 上传本地文档作为私有知识库
- 对知识库做向量检索，回收范例与参考片段
- 可选接入网站检索补充外部资料
- 可选抓取指定网页正文作为写作上下文
- 根据写作目标、语气和受众生成结构化文稿
- 列出、删除、重建知识库文档索引

## Repository Layout

```text
backend/   FastAPI + LangChain service
frontend/  React + Vite web app
```

## Backend

1. 创建虚拟环境并安装依赖

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. 配置环境变量

```powershell
Copy-Item .env.example .env
```

至少填写：

- `DASHSCOPE_API_KEY`
- `FIRECRAWL_API_KEY`（如果需要网页正文抓取）
- `TAVILY_API_KEY`（如果需要网站检索）

默认已经切到千问兼容接口：

- `QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`
- `QWEN_MODEL=qwen-plus`
- `QWEN_EMBEDDING_MODEL=text-embedding-v3`

3. 启动服务

```powershell
uvicorn app.main:app --reload --port 8000
```

## Frontend

1. 安装依赖

```powershell
cd frontend
npm install
```

2. 启动开发服务器

```powershell
npm run dev
```

默认前端访问 `http://localhost:5173`，后端访问 `http://localhost:8000`。

## API

- `GET /api/knowledge/documents` 获取知识库文档列表
- `POST /api/knowledge/upload` 上传文档并写入索引
- `DELETE /api/knowledge/documents/{document_id}` 删除文档并重建索引
- `POST /api/knowledge/rebuild` 手动重建整个知识库索引
- `POST /api/generate` 生成文档，可选传 `source_url`

## Current MVP Flow

1. 上传文档到 `/api/knowledge/upload`
2. 文档元数据写入 `storage/knowledge_registry.json`
3. 文档被切分并写入本地 FAISS 向量索引
4. 提交写作请求到 `/api/generate`
5. 后端从知识库、网站检索和可选网页抓取中提取上下文
6. LangChain 调用千问模型生成最终文稿

## Current Constraints

- 未配置 `DASHSCOPE_API_KEY` 时，后端无法调用千问模型或 embedding。
- 未配置 `FIRECRAWL_API_KEY` 时，网页正文抓取会自动跳过。
- 未配置 `TAVILY_API_KEY` 时，网站检索会自动跳过。
- 当前知识库仍是单库模式，但已经有独立文档元数据注册表，便于后续做多空间隔离。

## Next Recommended Steps

- 增加文档标签、项目空间和权限隔离
- 增加引用溯源和片段定位
- 增加流式输出和编辑器富文本能力
- 补充异步任务队列处理大文件解析
- 为上传、删除、重建、网页抓取接口补测试
