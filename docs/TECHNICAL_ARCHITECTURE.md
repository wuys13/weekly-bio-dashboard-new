# 🏗️ Weekly Bio Dashboard - 技术架构详解

## 概述

Weekly Bio Dashboard 是一个自动化论文发现系统，通过**关键词评分**将最新的科研论文智能分类、排序，并以网页仪表盘形式展示。

**核心特点**：
- ✅ 无需爬虫（使用公开 API）
- ✅ 实时更新（每次访问获取最新论文）
- ✅ 智能评分（多维加权，考虑标题、摘要、跨域相关性）
- ✅ 完全可定制（编辑一个 config.py 文件即可）

---

## 架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  数据源 API            数据处理         用户界面            │
│  ─────────────────  ─────────────────  ───────────────      │
│                                                              │
│  Crossref API          fetchers.py      Streamlit Web       │
│  bioRxiv API     →     scoring.py    →  (HTML/JS)          │
│  medRxiv API           config.py        @ localhost:8501   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 第一步：数据爬取 (fetchers.py)

### 1.1 数据源

系统使用 **3 个公开 API**（无需爬虫，合法且稳定）：

#### Crossref API - 学术期刊

```
URL: https://api.crossref.org/works
目的: 获取已发表的学术论文
特点: 权威、质量有保证

查询条件:
  • 期刊: 通过 ISSN (International Standard Serial Number) 精确匹配
    例: Cell ISSN = 0092-8674
  • 时间: 最近 15 天发布的论文 (from-online-pub-date, until-online-pub-date)
  • 排序: 按发布日期降序 (最新优先)
  • 字段: DOI, title, abstract, published-online date, URL, container-title

速率限制: 0.15 秒/请求 (遵守 API 礼仪)
监管期刊: 21 个顶级期刊 (Cell, Nature, Science, Cancer Cell, etc.)
典型结果: ~200-300 篇/期刊
```

**例子请求**：
```
GET https://api.crossref.org/works
  ?filter=from-online-pub-date:2026-03-01,until-online-pub-date:2026-03-16,type:journal-article,issn:0092-8674
  &rows=200
  &sort=published-online
  &order=desc
  &select=DOI,title,issued,abstract,...
```

#### bioRxiv API - 生物学预印本

```
URL: https://api.biorxiv.org/details/biorxiv
目的: 获取最新的生物学预印本 (未正式发表)
特点: 发表速度快 (~1-2 小时)，但未经同行评审

时间范围: 最近 7 天
分页: 最多 6 页 (~100 篇/页)
典型结果: 500-1000 篇/周
```

#### medRxiv API - 医学预印本

```
URL: https://api.biorxiv.org/details/medrxiv
目的: 获取最新的医学相关预印本
用法: 与 bioRxiv 相同的 API 架构
典型结果: 200-500 篇/周
```

### 1.2 爬取流程

```python
def crossref_fetch(journal: str, days: int = 15) -> tuple[list[dict], str]:
    """
    获取某期刊的最新论文
    返回: (论文列表, 状态)
    """
    # 1️⃣  定义时间范围
    end = datetime.now(timezone.utc).date()          # 今天
    start = end - timedelta(days=days)               # N天前
    base_filter = f"from-online-pub-date:{start},until-online-pub-date:{end}"
    
    # 2️⃣  获取期刊 ISSN (精确匹配)
    issns = JOURNAL_ISSN.get(journal, [])            # 例: ["0092-8674", "1097-4172"]
    
    # 3️⃣  发送 HTTP 请求 + 错误重试
    for attempt in range(3):  # 最多 3 次
        try:
            response = requests.get(
                "https://api.crossref.org/works",
                params={
                    "filter": f"{base_filter},issn:{issn}",
                    "rows": 200,
                    "sort": "published-online",
                    "order": "desc",
                    "select": "DOI,title,issued,abstract,URL,container-title"
                },
                headers={"User-Agent": "weekly-bio-dashboard/3.0"},
                timeout=30
            )
            response.raise_for_status()
            break
        except RequestException:
            time.sleep(0.6 * (2 ** attempt))  # 指数退避: 0.6s, 1.2s, 2.4s
    
    # 4️⃣  解析 JSON
    items = response.json().get("message", {}).get("items", [])
    
    # 5️⃣  提取关键字段
    papers = []
    for item in items:
        paper = {
            "source": "Journal",
            "journal": item.get("container-title", [""])[0],
            "title": item.get("title", [""])[0],
            "abstract": item.get("abstract", ""),
            "doi": item.get("DOI", ""),
            "url": item.get("URL", ""),
            "date": parse_crossref_date(item)
        }
        papers.append(paper)
    
    return papers, "ok"
```

### 1.3 数据结果

```
输入: 21 个期刊 × 15 天 + bioRxiv/medRxiv × 7 天
      │
      ↓
输出: DataFrame (1505 行, 7 列)

┌──────────┬──────────────┬─────────────────────────┬──────────┬─────┬──────────┐
│ source   │ journal      │ title                   │ abstract │ doi │ date     │
├──────────┼──────────────┼─────────────────────────┼──────────┼─────┼──────────┤
│ Journal  │ Cell         │ "Visium reveals..."    │ "We show"│ ... │ 2026-... │
│ Journal  │ Nature       │ "Deep learning for..." │ "Methods"│ ... │ 2026-... │
│ Preprint │ bioRxiv      │ "Single-cell RNA-seq"  │ "Prelim" │ --- │ 2026-... │
├──────────┼──────────────┼─────────────────────────┼──────────┼─────┼──────────┤
│ ... 1502 more rows ...                                                       │
└──────────┴──────────────┴─────────────────────────┴──────────┴─────┴──────────┘
```

---

## 第二步：数据处理 (scoring.py + config.py)

### 2.1 去重

**问题**: 同一篇论文可能从多个来源重复获取

**解决方案** (三层):
```
第1层 (最准确): DOI 去重
  ✓ DOI (Digital Object Identifier) 是全球唯一标识
  ✓ 准确率 99%
  例: 10.1038/s41586-021-03819-2

第2层 (备选): 标题 + 期刊 MD5 哈希
  ✓ 当 DOI 缺失时使用
  例: md5("Visium paper" + "Cell") = a1b2c3d4...

第3层 (最后): 按来源优先级排序
  ✓ 期刊 > 预印本 (同一篇优先保留期刊版本)
```

**结果**:
```
原始: 1505 篇
去重后: 1200 篇 (删除 305 个重复)
```

### 2.2 关键词匹配

**配置** (config.py):
```python
CORE_KEYWORDS = {
    # 你的研究领域的关键词集合
    "spatial_transcriptomics": [
        "spatial transcriptomics",  # 长词 (优先匹配)
        "visium",
        "merfish",
        "seqfish",
        "stereo-seq",
        # ... 共 14 个关键词
    ],
    "ai_ml": [
        "deep learning",
        "neural network",
        "transformer",
        # ... 共 15 个关键词
    ],
    "tumor_microenvironment": [
        "tumor microenvironment",
        "immune infiltration",
        "macrophage",
        # ... 共 15 个关键词
    ],
    # ... 共 14 个类别，56 个关键词
}
```

**匹配算法** (scoring.py - contains_any):

```python
def contains_any(text: str, keywords: list[str]) -> int:
    """
    统计文本中有多少个不同的关键词被匹配到
    """
    t = text.lower()
    
    # 1️⃣  按长度排序 (最长优先 - 避免重复计数)
    sorted_keywords = sorted(keywords, key=len, reverse=True)
    
    # 2️⃣  扫描并计数
    hit_count = 0
    matched_spans = []  # 记录已匹配的文本位置
    
    for keyword in sorted_keywords:
        # 对于短词 (<= 3 字母): 词边界匹配 (避免误匹配)
        if len(keyword) <= 3:
            pattern = rf"\b{re.escape(keyword)}\b"  # 正则: \bGWAS\b
            match = re.search(pattern, t)
        else:
            # 对于长词: 子字符串匹配
            idx = t.find(keyword)
            match = idx >= 0
        
        # 检查是否与已匹配区间重叠
        if match and not _overlaps(match_span, matched_spans):
            hit_count += 1
            matched_spans.append(match_span)
    
    return hit_count

# 【例子】
text = "We used visium spatial transcriptomics to map tumor microenvironment"

contains_any(text, ["spatial transcriptomics", "spatial", "visium"]):
  ✓ "spatial transcriptomics" (最长) → 匹配 → hit_count = 1
  ✗ "spatial" (重叠，被跳过)
  ✓ "visium" → 匹配 → hit_count = 2
  返回: 2
```

**关键点**:
- ✅ 长词优先：避免 "spatial" 和 "spatial transcriptomics" 重复计数
- ✅ 词边界：短词用 `\bGWAS\b` 避免误匹配 "gwass"
- ✅ 无重叠：同一位置的文本只计数一次

### 2.3 评分算法

**核心思路**: 多维加权评分，反映论文与你研究领域的相关性

```
评分 = 0

FOR 每个 TECH 类别 (权重 w_tech = 3):
  effective_hits = min(6, 该类别在文本中的匹配数)  # 上限 6，避免某类别垄断分数
  title_bonus = min(3, 该类别在标题中的匹配数)      # 标题更重要
  评分 += effective_hits * 3 + title_bonus * 2

FOR 每个 BIO 类别 (权重 w_bio = 2):
  effective_hits = min(6, 该类别在文本中的匹配数)
  title_bonus = min(3, 该类别在标题中的匹配数)
  评分 += effective_hits * 2 + title_bonus * 1.5

# 特殊加成项
评分 += min(8, 方法论词数 * 2)  # "assay", "platform", "technology", "method"...
if has_TECH_keyword AND has_BIO_keyword:
  评分 += 6  # 跨领域相关性加成 (最有价值的论文)

评分 *= journal_multiplier(journal)  # 期刊调整 (nature communications 0.5x)
```

**【完整例子】**

论文: "Deep Learning for Spatial Transcriptomics in Tumor Microenvironment"

```
标题匹配:
  - ai_ml: 2 个词 (deep, learning)
  - spatial_transcriptomics: 2 个词 (spatial, transcriptomics)

摘要匹配 (假设摘要有):
  - tumor_microenvironment: 3 个词

关键词类别分类:
  - ai_ml 属于 TECH (权重 3)
  - spatial_transcriptomics 属于 TECH (权重 3)
  - tumor_microenvironment 属于 BIO (权重 2)

评分计算:
  ai_ml (TECH):
    = min(6, 2) * 3 + min(3, 2) * 2
    = 2 * 3 + 2 * 2
    = 10

  spatial_transcriptomics (TECH):
    = min(6, 2) * 3 + min(3, 2) * 2
    = 2 * 3 + 2 * 2
    = 10

  tumor_microenvironment (BIO):
    = min(6, 3) * 2 + min(3, 0) * 1.5
    = 3 * 2 + 0 * 1.5
    = 6

  方法论加成 (假设有 "model" 等词):
    = min(8, 2 * 2)
    = 4

  Tech + Bio 加成 (两者都有):
    = 6

总分: 10 + 10 + 6 + 4 + 6 = 36 分 ✅ (高相关性)
```

**权重解释**:
- TECH (权重 3) > BIO (权重 2)：因为你是技术驱动的研究者
- 标题匹配 (2x) > 摘要匹配 (1x)：标题更能反映核心内容
- Tech + Bio 同时出现 (+6)：这是最有价值的论文

### 2.4 分类

按评分和关键词分类：

```python
# 分类逻辑
for idx, row in df.iterrows():
    score = row["score"]
    is_tech = any(row["hits"].get(k, 0) > 0 for k in TECH_KEYS)
    is_bio = any(row["hits"].get(k, 0) > 0 for k in BIO_KEYS)
    
    # Must-Read Tech: 高分 + 有 TECH 关键词
    if score > 20 and is_tech:
        df.loc[idx, "category"] = "must_read_tech"
    
    # Must-Read Bio: 中等分 + 有 BIO 关键词
    elif score > 15 and is_bio:
        df.loc[idx, "category"] = "must_read_bio"
    
    # Focus Area 1: 包含 FOCUS_AREA_1_KEYS 中的词
    elif has_focus_keywords(row, FOCUS_AREA_1_KEYS):
        df.loc[idx, "category"] = "focus_1"
    
    # Focus Area 2: 包含 FOCUS_AREA_2_KEYS 中的词
    elif has_focus_keywords(row, FOCUS_AREA_2_KEYS):
        df.loc[idx, "category"] = "focus_2"
    
    # 默认: 其他相关论文
    else:
        df.loc[idx, "category"] = "other"

# 每个类别内部排序
df.groupby("category").apply(lambda x: x.sort_values("score", ascending=False))
```

---

## 第三步：可视化 (app.py + Streamlit)

### 3.1 Streamlit 框架

**什么是 Streamlit？**
```
Streamlit 是 Python 框架，将 Python 代码直接转换为网页应用
无需 HTML/JavaScript/CSS - 纯 Python
```

**执行流程**:
```
1. streamlit run app.py
   ↓
2. Streamlit 启动 Web 服务器 (localhost:8501)
   ↓
3. 首次访问: 执行全部 Python 代码
   ↓
4. 用户交互 (点击、输入): 重新执行 Python，刷新显示
```

### 3.2 UI 组件

```python
import streamlit as st
import pandas as pd
from fetchers import crossref_fetch, biorxiv_fetch
from scoring import score_and_tags

# 1️⃣  获取数据
st.title("📊 Weekly Bio Dashboard")

all_papers = []
for journal in JOURNALS:
    papers, status = crossref_fetch(journal, days=15)
    all_papers.extend(papers)

preprints, status = biorxiv_fetch(days=7)
all_papers.extend(preprints)

df = pd.DataFrame(all_papers)

# 2️⃣  评分
scores, tags, hits = [], [], []
for _, row in df.iterrows():
    s, t, h = score_and_tags(row["title"], row["abstract"])
    scores.append(s)
    tags.append(t)
    hits.append(h)

df["score"] = scores
df["tags"] = tags
df["hits"] = hits

# 3️⃣  显示表格
st.subheader("🎯 Must-Read Tech (20 papers)")
tech_papers = df[df["score"] > 20].head(20)
st.table(tech_papers[["title", "journal", "score", "tags"]])

st.subheader("🔬 Must-Read Bio (20 papers)")
bio_papers = df[df["score"] > 15].head(20)
st.table(bio_papers[["title", "journal", "score", "tags"]])

# 4️⃣  搜索框 (交互)
query = st.text_input("🔍 Search papers...")
if query:
    filtered = df[df["title"].str.contains(query, case=False, na=False)]
    st.write(f"Found {len(filtered)} papers:")
    st.table(filtered[["title", "journal", "score"]])

# 5️⃣  趋势分析
trends = trend_summary(df, top_k=5)
st.subheader("📈 Research Trends")
for trend_name, description, examples in trends:
    st.write(f"**{trend_name}**: {description}")

# 6️⃣  数据源状态
st.subheader("📊 Data Source Status")
status_data = {
    "Source": ["Crossref", "bioRxiv", "medRxiv"],
    "Count": [237, 856, 412],
    "Status": ["✓ OK", "✓ OK", "✓ OK"]
}
st.table(pd.DataFrame(status_data))
```

### 3.3 显示内容

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📊 Weekly Bio Dashboard                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 Must-Read Tech (20 papers)
┌────────────────────────────────────────────────────────┐
│ Title                      │ Journal │ Score │ Tags   │
├────────────────────────────────────────────────────────┤
│ Visium-based spatial TR... │ Cell    │ 42    │ spatial│
│ Deep learning for TR...    │ Nature  │ 38    │ ai/ml  │
│ Tumor immunity mapping...  │ Cancer  │ 35    │ tumor  │
└────────────────────────────────────────────────────────┘

🔬 Must-Read Bio (20 papers)
┌────────────────────────────────────────────────────────┐
│ Title                      │ Journal │ Score │ Tags   │
├────────────────────────────────────────────────────────┤
│ Immune cell infiltration.. │ Immunity│ 28    │ immune │
└────────────────────────────────────────────────────────┘

🌟 Focus 1: Spatial Transcriptomics + Tumor Immunity (15)
🌟 Focus 2: AI/ML for Transcriptomics (15)
🌟 Focus 3: AI/ML in Bio Data Analysis (15)

📈 Research Trends
  • Spatial Transcriptomics ↑ (256 papers, up 45%)
  • Tumor Microenvironment ↑ (189 papers, up 32%)
  • AI/ML Methods ↑ (412 papers, up 28%)

📊 Data Source Status
  Crossref: 237 papers (OK)
  bioRxiv: 856 papers (OK)
  medRxiv: 412 papers (OK)
```

---

## 完整数据流

```
┌─────────────────────────────────────────────────────────────┐
│                     数据源 (API)                             │
│  Crossref (21 期刊)  bioRxiv   medRxiv                      │
│  ~200 篇            ~500 篇    ~200 篇                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
                 获取 1505 篇论文
                          ↓
                  去重 → 1200 篇
                          ↓
          关键词匹配 + 评分 (56 个关键词)
          每篇论文: score + tags + hits
                          ↓
            按类别分类 + 排序
            ├─ Must-Read Tech (score > 20)
            ├─ Must-Read Bio (score > 15)
            ├─ Focus 1 (空间转录 + 肿瘤)
            ├─ Focus 2 (AI/ML 转录组)
            ├─ Focus 3 (AI/ML 数据分析)
            └─ Trends (热点检测)
                          ↓
                Streamlit 渲染 HTML
                          ↓
                  浏览器显示
                http://localhost:8501
```

---

## 关键技术点

| 层级 | 技术 | 说明 |
|------|------|------|
| **数据源** | 公开 API | Crossref、bioRxiv、medRxiv (无爬虫) |
| **获取** | HTTP GET + JSON | requests 库，错误重试 (指数退避) |
| **去重** | DOI + MD5 哈希 | 三层去重策略 |
| **文本分析** | 正则 + 子字符串 | 长词优先，词边界匹配 |
| **评分** | 多维加权 | TECH (3x) > BIO (2x)，标题 2x 加成 |
| **分类** | 阈值 + 关键词 | score > 20 / 15，Focus 区域 |
| **可视化** | Streamlit | Python → HTML，交互式表格 |

---

## 配置文件 (config.py)

所有参数都在 `config.py` 中，可随时修改：

```python
# 期刊
JOURNALS = ["Cell", "Nature", "Science", ...]

# 关键词类别 (14 个)
CORE_KEYWORDS = {
    "spatial_transcriptomics": [...],
    "ai_ml": [...],
    ...
}

# 分类
TECH_KEYS = ["spatial_transcriptomics", "ai_ml", ...]
BIO_KEYS = ["tumor_microenvironment", ...]

# Focus 区域
FOCUS_AREA_1_KEYS = [...]  # 空间转录 + 肿瘤免疫
FOCUS_AREA_2_KEYS = [...]  # AI/ML 转录组

# 趋势
TREND_LEXICON = {
    "Spatial Transcriptomics": [...],
    "Tumor Microenvironment": [...],
    ...
}

# 参数
MUST_READ_N = 20           # 每个类别最多显示 20 篇
MAX_PER_JOURNAL_MUST_READ = 3  # 每个期刊最多 3 篇
```

---

## 总结

**数据流三步**:
1. **爬取** → 公开 API 获取 ~1500 篇论文
2. **处理** → 去重 → 关键词匹配 → 多维评分 → 分类
3. **可视化** → Streamlit 网页展示

**核心创意**:
- ✅ 无爬虫，使用公开 API
- ✅ 智能评分，TECH 权重高于 BIO
- ✅ 跨域加成，Tech + Bio 同时出现的论文最有价值
- ✅ 实时更新，每次访问都是最新数据
- ✅ 完全可定制，编辑 config.py 即可调整

