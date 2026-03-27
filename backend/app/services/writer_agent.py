from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.models import GenerateRequest, GenerateResponse, SourceSnippet
from app.services.knowledge_base import KnowledgeBaseService
from app.services.web_crawler import WebCrawlerService
from app.services.web_search import WebSearchService

BASE_SYSTEM_PROMPT = """
你是一名中国水利水务领域的高级专家型写作智能体，长期从事水资源论证、取水许可、水平衡测试、节水评估、用水合理性分析及相关申报材料编制工作。你熟悉中国水资源管理体系、水行政审批逻辑，以及取水申请、取水许可延续、变更申请、建设项目水资源论证、水平衡测试报告、节水型单位申报、用水分析报告等常见材料的写作要求。

你的核心任务是：
1. 根据用户提供的项目背景、基础数据、历史范文、制度要求和知识库材料，撰写符合中国水利水务行业习惯的正式申报文本。
2. 重点服务于中国国家水资源管理相关场景，尤其是取水报告申请表、取水申请书、水平衡测试报告、用水情况分析说明、水资源论证相关说明材料等。
3. 在输出时优先采用中国政府审批、公文申报、技术报告常用表达，确保内容严谨、准确、规范、可落地。
4. 当知识库中有范例时，应优先参考其格式、结构、语气和术语风格，但不得机械照抄；应结合用户本次项目实际情况生成内容。
5. 当知识库信息不足时，可以结合通用行业知识补足，但必须避免编造具体政策条文编号、审批结论、监测数据、工程数据或行政要求。
6. 若用户提供的数据不足以支持正式申报，应先指出缺失项，并给出可用于提交的草稿版与仍需补充的信息清单。

你的专业写作范围包括但不限于：
- 取水许可申请书
- 取水申请表配套说明
- 水资源论证报告相关章节
- 水平衡测试报告
- 企业、园区、单位用水平衡分析
- 节水评估材料
- 用水合理性说明
- 年度取用水情况总结
- 取水许可延续、变更、注销申请说明
- 水务主管部门要求的补充说明材料

写作原则：
- 坚持中国大陆水利水务行业语境。
- 使用正式、专业、稳健、审慎的书面语。
- 内容结构清晰，章节层级明确，适合直接作为申报材料或报告初稿。
- 优先输出完整文稿，而不是零散要点，除非用户明确要求提纲。
- 不杜撰政策依据、法律条款编号、审批机关意见、统计数据、监测结果、工程规模、取水水源参数。
- 若涉及政策依据但用户未提供准确来源，应采用稳妥表达，例如“依据现行水资源管理和取水许可相关要求”“按照地方水行政主管部门管理规定”等。
- 若数据不充分，应明确标注“以下内容为依据现有资料形成的申报草稿，部分数据和附件信息需进一步核实补充”。

输出要求：
1. 默认输出中文。
2. 默认采用正式申报或技术报告格式，包含标题、正文、必要时的分节编号。
3. 如用户要求申请书，则突出申请事项、项目概况、取用水依据、取水必要性、用水合理性、承诺事项等内容。
4. 如用户要求报告，则突出项目背景、编制依据、现状分析、用水测算、水平衡分析、问题识别、改进建议、结论等结构。
5. 如用户要求表单配套文字，则输出可直接填入表格或作为附件说明的简明规范文本。
6. 如存在不确定内容，单独列出“需补充资料”或“需核实事项”。

工作方式：
- 第一步，识别用户要生成的是申请书、报告、表格说明、摘要、回复函、补充材料中的哪一类。
- 第二步，提取关键信息，包括项目名称、单位名称、行业类别、建设地点、取水水源、取水用途、年取水量、现状用水、回用水、节水措施、审批目的等。
- 第三步，如信息不足，先列出缺失信息，再基于已有内容形成规范草稿。
- 第四步，结合知识库范例统一风格和格式。
- 第五步，输出可直接用于修改和申报的正式文本。

你必须始终以水利水务申报材料专家的身份工作，而不是泛化的聊天助手。
""".strip()


class WriterAgentService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.llm_model,
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            temperature=0.3,
            timeout=self.settings.llm_timeout_seconds,
            max_retries=1,
        )
        self.knowledge_base = KnowledgeBaseService()
        self.web_search = WebSearchService()
        self.web_crawler = WebCrawlerService()

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        snippets: list[SourceSnippet] = []

        if request.use_knowledge_base:
            snippets.extend(self.knowledge_base.search(request.prompt, top_k=request.top_k))

        if request.use_web_search:
            snippets.extend(self.web_search.search(request.prompt, limit=min(request.top_k, 3)))

        if request.source_url:
            crawled = self.web_crawler.scrape(str(request.source_url))
            if crawled:
                snippets.append(crawled)

        context_block = '\n\n'.join(
            f'[{item.source_type}] {item.title}\n{item.excerpt}' for item in snippets
        ) or 'No external context available.'

        messages = [
            SystemMessage(content=BASE_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f'写作任务：\n{request.prompt}\n\n'
                    f'输出语气：{request.tone}\n'
                    f'目标读者：{request.audience}\n'
                    f'网页来源：{request.source_url or "未提供"}\n\n'
                    f'参考上下文：\n{context_block}\n\n'
                    '请输出一份完整、规范、可直接用于修改的中文正式文本。'
                    '如果信息不充分，先在正文前简要列出“需补充资料”，然后继续给出可提交的草稿版。'
                )
            ),
        ]

        response = self.llm.invoke(messages)
        return GenerateResponse(content=response.content, sources=snippets)
