import { ChangeEvent, FormEvent, useEffect, useState } from "react";

type SourceSnippet = {
  source_type: "knowledge_base" | "web";
  title: string;
  excerpt: string;
};

type GenerateResponse = {
  content: string;
  sources: SourceSnippet[];
};

type KnowledgeDocument = {
  id: string;
  file_name: string;
  stored_name: string;
  chunks_indexed: number;
  uploaded_at: string;
};

const API_BASE = "http://localhost:8000";
const REQUEST_TIMEOUT_MS = 90000;

function getErrorMessage(error: unknown) {
  if (error instanceof Error) return error.message;
  return "未知错误";
}

async function fetchWithDiagnostics(input: RequestInfo | URL, init?: RequestInit) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(input, {
      ...init,
      signal: controller.signal,
    });

    if (!response.ok) {
      let detail = `${response.status} ${response.statusText}`;
      try {
        const data = (await response.json()) as { detail?: string };
        if (data.detail) detail = `${detail}: ${data.detail}`;
      } catch {
        const text = await response.text();
        if (text) detail = `${detail}: ${text}`;
      }
      throw new Error(detail);
    }

    return response;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`请求超时，${REQUEST_TIMEOUT_MS / 1000} 秒内未收到响应`);
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export function App() {
  const [prompt, setPrompt] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [tone, setTone] = useState("professional");
  const [audience, setAudience] = useState("general");
  const [useKnowledgeBase, setUseKnowledgeBase] = useState(true);
  const [useWebSearch, setUseWebSearch] = useState(true);
  const [uploadStatus, setUploadStatus] = useState("");
  const [knowledgeDocs, setKnowledgeDocs] = useState<KnowledgeDocument[]>([]);
  const [knowledgeLoading, setKnowledgeLoading] = useState(false);
  const [knowledgeAction, setKnowledgeAction] = useState("");
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    void loadKnowledgeDocuments();
  }, []);

  async function loadKnowledgeDocuments() {
    setKnowledgeLoading(true);
    try {
      const response = await fetchWithDiagnostics(`${API_BASE}/api/knowledge/documents`);
      const data = (await response.json()) as { items: KnowledgeDocument[] };
      setKnowledgeDocs(data.items);
      setKnowledgeAction("");
    } catch (error) {
      setKnowledgeAction(`知识库列表加载失败：${getErrorMessage(error)}`);
    } finally {
      setKnowledgeLoading(false);
    }
  }

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    const body = new FormData();
    body.append("file", file);
    setUploadStatus("上传中...");

    try {
      const response = await fetchWithDiagnostics(`${API_BASE}/api/knowledge/upload`, {
        method: "POST",
        body,
      });
      const data = (await response.json()) as KnowledgeDocument;
      setUploadStatus(`已入库：${data.file_name}，切分 ${data.chunks_indexed} 段`);
      await loadKnowledgeDocuments();
      event.target.value = "";
    } catch (error) {
      setUploadStatus(`上传失败：${getErrorMessage(error)}`);
    }
  }

  async function handleDelete(documentId: string) {
    setKnowledgeAction("删除中...");
    try {
      await fetchWithDiagnostics(`${API_BASE}/api/knowledge/documents/${documentId}`, {
        method: "DELETE",
      });
      setKnowledgeAction("文档已删除，索引已重建。");
      await loadKnowledgeDocuments();
    } catch (error) {
      setKnowledgeAction(`删除失败：${getErrorMessage(error)}`);
    }
  }

  async function handleRebuild() {
    setKnowledgeAction("重建索引中...");
    try {
      await fetchWithDiagnostics(`${API_BASE}/api/knowledge/rebuild`, {
        method: "POST",
      });
      setKnowledgeAction("知识库索引已重建。");
      await loadKnowledgeDocuments();
    } catch (error) {
      setKnowledgeAction(`索引重建失败：${getErrorMessage(error)}`);
    }
  }

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetchWithDiagnostics(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          tone,
          audience,
          source_url: sourceUrl || undefined,
          use_knowledge_base: useKnowledgeBase,
          use_web_search: useWebSearch,
        }),
      });
      const data = (await response.json()) as GenerateResponse;
      setResult(data);
    } catch (error) {
      setResult({
        content: `生成失败：${getErrorMessage(error)}`,
        sources: [],
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-shell">
      <aside className="side-panel">
        <div>
          <p className="eyebrow">Knowledge-guided writing</p>
          <h1>Document Writing Agent</h1>
          <p className="intro">
            上传你的范文、制度文档或历史材料，让模型在保留外部信息扩展能力的前提下，优先沿用你的内容风格与知识边界。
          </p>
        </div>

        <label className="upload-card">
          <span>上传知识库文档</span>
          <input type="file" accept=".pdf,.doc,.docx,.txt,.md" onChange={handleUpload} />
          <small>{uploadStatus || "支持 PDF、Word、TXT、Markdown"}</small>
        </label>

        <section className="knowledge-card">
          <div className="knowledge-header">
            <strong>知识库文档</strong>
            <button type="button" className="ghost-button" onClick={handleRebuild}>
              重建索引
            </button>
          </div>
          <small>{knowledgeAction || (knowledgeLoading ? "正在读取文档列表..." : `共 ${knowledgeDocs.length} 个文档`)}</small>
          <div className="knowledge-list">
            {knowledgeDocs.length ? (
              knowledgeDocs.map((doc) => (
                <article className="knowledge-item" key={doc.id}>
                  <div>
                    <strong>{doc.file_name}</strong>
                    <p>{new Date(doc.uploaded_at).toLocaleString("zh-CN")}</p>
                    <small>{doc.chunks_indexed} 个片段</small>
                  </div>
                  <button type="button" className="danger-button" onClick={() => handleDelete(doc.id)}>
                    删除
                  </button>
                </article>
              ))
            ) : (
              <p className="empty-text">还没有文档，先上传一个范例或制度文件。</p>
            )}
          </div>
        </section>

        <div className="feature-list">
          <div>
            <strong>私有知识检索</strong>
            <p>基于上传文档分块检索，优先回收内部范例与语料。</p>
          </div>
          <div>
            <strong>网页正文抓取</strong>
            <p>可填写指定网页链接，抓取正文并作为写作辅助上下文。</p>
          </div>
          <div>
            <strong>结构化写作输出</strong>
            <p>针对目标受众和语气控制，直接生成可继续编辑的完整文稿。</p>
          </div>
        </div>
      </aside>

      <main className="workspace">
        <form className="editor-card" onSubmit={handleGenerate}>
          <div className="toolbar">
            <div>
              <label>语气</label>
              <select value={tone} onChange={(e) => setTone(e.target.value)}>
                <option value="professional">专业正式</option>
                <option value="friendly">友好自然</option>
                <option value="executive">高管摘要</option>
              </select>
            </div>
            <div>
              <label>读者</label>
              <select value={audience} onChange={(e) => setAudience(e.target.value)}>
                <option value="general">通用读者</option>
                <option value="management">管理层</option>
                <option value="customers">客户/外部对象</option>
              </select>
            </div>
          </div>

          <label className="url-field">
            <span>网页链接（可选）</span>
            <input
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://example.com/policy-or-reference-page"
            />
          </label>

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="例如：请基于已上传的取水申请范本，并参考指定网页中的政策背景，撰写一份取水许可申请说明，面向地方水行政主管部门。"
          />

          <div className="toggle-row">
            <label>
              <input
                type="checkbox"
                checked={useKnowledgeBase}
                onChange={(e) => setUseKnowledgeBase(e.target.checked)}
              />
              使用知识库
            </label>
            <label>
              <input
                type="checkbox"
                checked={useWebSearch}
                onChange={(e) => setUseWebSearch(e.target.checked)}
              />
              使用网站检索
            </label>
          </div>

          <button type="submit" disabled={loading || prompt.trim().length < 10}>
            {loading ? "生成中..." : "生成文档"}
          </button>
        </form>

        <section className="result-card">
          <div className="result-header">
            <h2>生成结果</h2>
            <span>{result?.sources.length ? `引用 ${result.sources.length} 条上下文` : "等待生成"}</span>
          </div>
          <article className="draft-output">{result?.content || "文稿内容会显示在这里。"}</article>
          <div className="source-grid">
            {result?.sources.map((source, index) => (
              <div className="source-card" key={`${source.title}-${index}`}>
                <small>{source.source_type === "web" ? "Web" : "Knowledge Base"}</small>
                <strong>{source.title}</strong>
                <p>{source.excerpt}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
