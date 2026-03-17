# Weekly Bio Dashboard — 周刊式生物论文仪表盘

自动获取、评分、策展最新生物学研究论文的 Streamlit 仪表盘。从顶级期刊（Nature、Science、Cell系列）和预印本库（bioRxiv/medRxiv）实时获取数据，通过多维度关键词匹配和智能评分系统帮助你快速找到相关论文。

**特点**：无需 API 密钥 • 完全本地运行 • 配置驱动 • 支持邮件摘要

---

## 🎯 核心能力

### 数据获取
- 📰 **21个顶级期刊** 通过 Crossref API
- 📄 **bioRxiv / medRxiv** 预印本库（可选）
- ⚡ 智能重试 + 速率限制 + 去重（DOI、标题、期刊）
- 🔍 1周内 ~700-1000 篇论文自动获取

### 智能评分
- 🏷️ **多维关键词匹配**：标题 2x、摘要 1x、跨域加成 +6
- ⚖️ **Tech vs Bio 分割**：自动分类为技术/生物学论文
- 📊 **期刊调整因子**：防止高产出期刊（Nature Communications）垄断
- 🎯 **"Big deal"检测**：识别突破性论文

### 可视化
- 📋 **Must-read 排序**：按分数+发布日期排序，每期刊限3篇
- 🔬 **Focus 区域**：3个自定义专题（如"空间转录组+肿瘤微环境"）
- 📈 **趋势检测**：自动识别最热研究方向（基于关键词频度）
- 📥 **书签 + CSV 导出**：保存感兴趣论文，导入 Excel/Zotero

### 邮件摘要（可选）
- 📧 周报模式：自动生成 HTML 邮件
- ⏰ macOS launchd / cron 定时运行
- 🎨 美观的 HTML 格式，支持所有邮箱

---

## 🚀 快速开始

### 1. 环境准备
```bash
git clone https://github.com/huiliwang312/weekly-bio-dashboard-new.git
cd weekly-bio-dashboard-new

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动仪表盘
```bash
streamlit run app.py
```
打开浏览器：`http://localhost:8501`

### 3. 自定义配置（只需编辑一个文件）
编辑 `config.py`：

```python
# 添加你的期刊
JOURNALS = ["Nature", "Science", "Cell", ...]

# 定义关键词类别（每个类别自动成为标签）
CORE_KEYWORDS = {
    "spatial_transcriptomics": ["spatial transcriptomics", "visium", "merfish", ...],
    "ai_ml": ["deep learning", "transformer", ...],
    "tumor_microenvironment": ["tumor microenvironment", "immune infiltration", ...],
}

# 分配到 Tech / Bio 类别
TECH_KEYS = ["spatial_transcriptomics", "ai_ml", ...]
BIO_KEYS = ["tumor_microenvironment", ...]

# 定义专题聚焦区域
FOCUS_AREA_1_KEYS = ["spatial transcriptomics", "tumor", ...]  # 自动生成第一个专题
FOCUS_AREA_2_KEYS = ["machine learning", "deep learning", ...]  # 第二个专题
```

修改后无需重启，刷新页面自动生效。

---

## 📊 工作原理

### 数据流
```
┌─────────────────────────────────────────────────┐
│ 1. 获取阶段                                      │
│ • Crossref API: 按ISSN查询21个期刊               │
│ • bioRxiv/medRxiv API: 获取预印本                │
│ • 指数退避重试 + 0.15s 速率限制                  │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 2. 清洗阶段                                      │
│ • 三层去重: DOI → 标题+期刊 → 人工               │
│ • 日期标准化 (处理缺失/格式不一致)               │
│ • 摘要清理 (移除HTML标签)                        │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 3. 评分阶段 (scoring.py)                        │
│ • 多维关键词匹配（最长优先，避免重复计算）       │
│ • 标题权重2x，摘要权重1x                         │
│ • Tech标签 3x, Bio标签 2x                       │
│ • Tech+Bio协同加成 +6                           │
│ • 期刊调整因子（Nature Comm 0.5x）              │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 4. 可视化阶段 (app.py)                          │
│ • 按分数 + 发布日期排序                          │
│ • 分割: Tech论文 / Bio论文 / 预印本              │
│ • 自定义Focus区域（最多3个）                    │
│ • 趋势分析 (top 3 research directions)          │
│ • CSV导出 + 书签保存                            │
└─────────────────────────────────────────────────┘
```

### 核心算法：关键词匹配
```python
# ✓ 最长优先匹配：避免"spatial transcriptomics"被拆分
sorted_terms = sorted(terms, key=len, reverse=True)

# ✓ 标题vs摘要分化：标题hit加权2倍
hits_title = contains_any(title, keywords)      # 更重要
hits_abstract = contains_any(abstract, keywords)  # 次要

# ✓ 跨域加成：同时出现TECH和BIO关键词
if has_tech and has_bio:
    score += 6  # 这类论文通常最相关
```

---

## 📖 文档导览

| 文档 | 用途 |
|------|------|
| [**TECHNICAL_ARCHITECTURE.md**](docs/TECHNICAL_ARCHITECTURE.md) | 详细架构：API设计、去重策略、评分公式、数据流图 |
| [**SOP_WORKFLOW_PRINCIPLES.md**](docs/SOP_WORKFLOW_PRINCIPLES.md) | 工作心法：经验教训、问题诊断树、前后端调试、常见陷阱规避 |
| [**START_HERE.md**](docs/START_HERE.md) | 新手入门：5分钟快速设置 |
| [**SETUP_COMPLETE.md**](docs/SETUP_COMPLETE.md) | 完整配置：包含统计数据和深度自定义指南 |

---

## 🔧 配置详解

### 场景 1: 追踪特定领域（如"空间转录组"）
```python
# config.py
JOURNALS = [
    "Nature Biotechnology",  # 发表方法论
    "Nature Methods",        # 发表工具
    "Nature Communications", # 发表应用案例
    # ... 加20+个相关期刊
]

CORE_KEYWORDS = {
    "spatial_transcriptomics": [
        "spatial transcriptomics", "visium", "merfish", "seqfish",
        "stereo-seq", "slide-seq", "imaging-based", "resolved"
    ],
    # ... 其他关键词类别
}

TECH_KEYS = ["spatial_transcriptomics", ...]
FOCUS_AREA_1_KEYS = ["spatial transcriptomics", "tumor", ...]
```
结果：仪表盘自动识别空间转录组论文，Must-read会优先推荐。

### 场景 2: 追踪多个领域
```python
# Tech 类（技术方向）
TECH_KEYS = ["spatial_transcriptomics", "ai_ml", "single_cell"]

# Bio 类（生物学方向）
BIO_KEYS = ["tumor_microenvironment", "immunology"]

# Focus 专题
FOCUS_AREA_1_KEYS = [...]  # 空间转录组 + 肿瘤
FOCUS_AREA_2_KEYS = [...]  # AI在转录组学中
FOCUS_AI_KEYS = [...]       # AI/ML 通用
```

### 场景 3: 添加新期刊
```python
# 获取期刊的 ISSN（from https://portal.issn.org）
JOURNALS.append("新期刊名称")
JOURNAL_ISSN["新期刊名称"] = ["1234-5678", "9012-3456"]  # 可能有多个ISSN
```

---

## 📧 邮件摘要（可选）

### 启用邮件功能

1. 创建 `.env.digest` 文件：
```ini
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_TO=recipient@example.com
```

2. 测试邮件：
```bash
python send_digest.py --dry-run
# 生成 digest_preview.html，在浏览器打开预览
```

3. 实际发送：
```bash
python send_digest.py
```

4. 定时运行（macOS）：
```bash
# 编辑 scripts/com.huiliw.weekly-bio-digest.plist
# 修改路径和标签
cp scripts/com.huiliw.weekly-bio-digest.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.yourname.weekly-bio-digest.plist

# 验证：
launchctl list | grep weekly-bio-digest
```

每周自动发送论文摘要邮件！

---

## 🏗️ 项目结构

```
weekly-bio-dashboard-new/
├── config.py                    ← 【编辑这个！】所有配置
├── app.py                       ← Streamlit 仪表盘UI
├── scoring.py                   ← 评分 + 关键词匹配逻辑
├── fetchers.py                  ← API数据获取 (Crossref/bioRxiv/medRxiv)
├── send_digest.py               ← 邮件摘要生成器
├── requirements.txt             ← Python 依赖
│
├── docs/
│   ├── TECHNICAL_ARCHITECTURE.md     ← 详细架构文档
│   ├── SOP_WORKFLOW_PRINCIPLES.md    ← 工作原则与诊断
│   ├── START_HERE.md                 ← 快速开始
│   └── SETUP_COMPLETE.md             ← 完整设置指南
│
├── scripts/
│   ├── run_digest.sh                 ← 邮件摘要启动脚本
│   └── com.huiliw.weekly-bio-digest.plist  ← macOS定时任务配置
│
└── logs/
    └── streamlit.log            ← 运行日志
```

---

## 📊 仪表盘布局

### 上半部分
- **控制面板**：时间窗口、数据源选择、阈值调整、显示选项
- **Fetch Status**：每个数据源的论文计数和状态
- **全局统计**：总论文数、去重后数量、刷新时间

### 中间部分
- **Must-read排序**（3个列表）
  - Journals - Tech Top 20
  - Journals - Bio Top 20
  - Preprints - Top 20
- 每个列表可 CSV 导出

### 下半部分
- **Focus 专题**（3个，2列布局）
  - Focus 1: 你的专题 1
  - Focus 2: 你的专题 2
  - Focus 3: AI/ML 专题
- **趋势分析**：当周top 3研究方向

### 右侧
- **搜索框**：按标题/摘要/期刊/标签搜索
- **书签计数**：已保存论文数

---

## 🔍 常见问题

### Q: 为什么有些期刊显示 0 论文？
**A**: 这是正常的。Crossref 和 bioRxiv 的索引延迟 24-48 小时。尝试：
- 扩大时间窗口（7天 → 30天）
- 检查 Fetch Status 表格，如果状态是 ✓ 表示 API 正常，只是最近没有新论文

### Q: 评分分数怎么计算的？
**A**: 见 [TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md) 的评分公式。简单说：
```
分数 = TECH标签匹配数 × 3 + BIO标签匹配数 × 2 + 标题奖励 + 期刊调整
```

### Q: 能改变排序方式吗？
**A**: 目前固定为"分数+日期"排序。如需自定义，可修改 `app.py` 的排序逻辑或使用 CSV 导出在 Excel 中自由排序。

### Q: 搜索功能支持正则表达式吗？
**A**: 目前只支持简单的子串匹配。如需高级搜索，导出 CSV 后用 Excel/Python 处理。

### Q: 怎么添加我自己的论文源？
**A**: 修改 `fetchers.py` 添加新的 `*_fetch()` 函数，按相同的数据结构返回。见 `TECHNICAL_ARCHITECTURE.md` 的扩展指南。

---

## 💡 性能参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 数据获取耗时 | 60-120s | 首次加载：1505篇→1200篇（去重）×56个关键词评分 |
| 缓存 TTL | 3600s | 1小时内无需重新获取；超过1小时自动刷新 |
| 期刊数 | 21个 | 21个顶级期刊（不含预印本） |
| 预印本源 | 2个 | bioRxiv + medRxiv（可选） |
| 关键词总数 | 56个 | 分布在14个类别中 |
| API 速率限制 | 0.15s 间隔 | 约 6.7 req/sec（Crossref 建议 10 req/sec） |

---

## 📚 经验与陷阱

### ✅ 做这些

- 定期调整关键词（基于实际阅读体验）
- 使用 CSV 导出到 Excel/Zotero 做二次分析
- 定期查看"Trends"，了解领域最新方向
- 根据你的反馈调整 TECH_KEYS 和 BIO_KEYS 权重

### ❌ 避免这些

- ❌ 不要相信第一版配置的完美性 → 需要迭代改进
- ❌ 不要忽视"0论文"现象 → 先检查 Fetch Status，再判断
- ❌ 不要让Must-read列表超过50篇 → 阅读效率会下降
- ❌ 不要用"完美"的关键词 → 70%覆盖率就够好

---

## 🐛 故障排除

### 网页打不开
```bash
# 1. 检查进程是否运行
ps aux | grep streamlit

# 2. 检查端口是否被占用
lsof -i :8501

# 3. 查看错误日志
tail -50 /tmp/streamlit.log

# 4. 重启
pkill -f "streamlit run"
echo "" | nohup streamlit run app.py > /tmp/streamlit.log 2>&1 &
```

### 论文数量不对
```bash
# 1. 单独测试 API
python3 -c "from fetchers import crossref_fetch; print(crossref_fetch('Nature', 7))"

# 2. 检查配置是否加载
python3 -c "from config import JOURNALS; print(JOURNALS)"

# 3. 查看去重后的数据
# 在 app.py 中添加调试输出：
# st.write("Raw papers:", len(all_items), "After dedup:", len(df))
```

### 分数异常高/低
```bash
# 1. 查看关键词是否正确加载
python3 -c "from config import CORE_KEYWORDS; print(len(CORE_KEYWORDS))"

# 2. 测试单篇论文的评分
from scoring import score_and_tags
score, tags, hits = score_and_tags("Your paper title", "Your abstract")
print(f"Score: {score}, Tags: {tags}, Hits: {hits}")
```

---

## 🤝 贡献指南

欢迎 Fork 和 Pull Request！特别关注：

1. **新的关键词策略** - 提交你验证过的关键词配置
2. **新的数据源** - 添加 PubMed、Nature 等新 API
3. **UI/UX 改进** - 更好的排序、搜索、可视化
4. **算法优化** - 更智能的评分、去重、趋势检测

---

## 📜 许可证

MIT License - 自由使用和修改

---

## 🙏 致谢

- **Crossref** - 免费学术出版元数据 API
- **bioRxiv/medRxiv** - 免费生物医学预印本库
- **Streamlit** - 快速构建数据应用框架

---

**最后更新**：2026-03-17
**维护者**：Weekly Bio Dashboard 社区
