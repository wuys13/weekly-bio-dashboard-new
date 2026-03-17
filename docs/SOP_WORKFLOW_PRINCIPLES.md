# 论文项目与泛化任务 SOP — 工作心法与最佳实践

> 本文档总结了在开发 Weekly Bio Dashboard 及类似项目中学到的核心原则和工作流程

## 📋 目录
1. [核心心法](#核心心法)
2. [数据获取与集成](#数据获取与集成)
3. [问题诊断流程](#问题诊断流程)
4. [前后端交互](#前后端交互)
5. [需求理解与迭代](#需求理解与迭代)
6. [常见陷阱与规避](#常见陷阱与规避)
7. [文档与透明度](#文档与透明度)

---

## 核心心法

### 1. **不要假设，要验证** ⚠️
**原则**：当看到异常结果时，不要立即修复或移除；先诊断根本原因。

**案例**：
- ❌ **错误做法**：看到 Cell、Cancer Cell 等期刊返回 0 论文 → 立即从配置中删除
- ✅ **正确做法**：
  1. 先确认 API 是否真的失败（status = "ok"）
  2. 检查 ISSN 是否正确（去 ISSN 官方数据库验证）
  3. 理解为什么没有结果（Crossref 索引问题 vs 期刊真没有发表）
  4. **最终决定**：保留配置，但在 UI 中添加诊断信息让用户了解

**教训**：
- 0 论文 ≠ 配置错误
- API 成功 ≠ 数据完整
- 需要多维度验证

---

### 2. **透明度优先于隐藏问题** 🔍

**原则**：用户应该理解系统为什么返回某个结果，而不是被迫猜测。

**应用**：
```
坏例子：
  Cell → 0 papers (用户不知道为什么)

好例子：
  Cell → 0 papers | Status: ✓ | Detail: "ok (no recent publications in index)"
  (用户立即明白：API 正常，只是这个期刊最近没发表)
```

**为什么重要**：
- 减少用户困惑
- 建立信任
- 帮助诊断真正的问题

---

### 3. **配置即文档** 📝

**原则**：让配置文件本身说话，使用清晰的注释和分组。

**好的配置示例**：
```python
JOURNAL_ISSN = {
    # ✓ Reliably indexed in Crossref
    "Nature": ['0028-0836', '1476-4687'],
    "Science": ['0036-8075', '1095-9203'],

    # ✗ NOT reliably indexed (returns 0 results)
    # "Cell": ['0092-8674'],  # Crossref metadata issue
}
```

**为什么重要**：
- 未来维护者（包括自己）能快速理解决策
- 减少重复工作（不会再问"为什么移除了 Cell？"）

---

### 4. **分层诊断** 🔬

**原则**：从外到内，逐层诊断问题。

**诊断金字塔**：
```
┌─────────────────────────────────┐
│  用户看到的现象                   │ ← "网页打不开" / "0 论文显示"
├─────────────────────────────────┤
│  前端状态 (Dashboard)             │ ← Streamlit 是否运行？UI 是否加载？
├─────────────────────────────────┤
│  数据流层 (Data Pipeline)         │ ← API 是否调用？数据是否获取？
├─────────────────────────────────┤
│  外部依赖 (External APIs)         │ ← Crossref/bioRxiv 是否可用？
├─────────────────────────────────┤
│  配置和业务逻辑 (Config Logic)    │ ← ISSNs 是否正确？过滤规则对吗？
└─────────────────────────────────┘
```

**诊断时的顺序**：
1. **进程层**：`ps aux | grep streamlit` → 进程是否存在？
2. **网络层**：`curl http://localhost:8501` → 服务是否响应？
3. **日志层**：`tail logs/` → 是否有错误信息？
4. **业务层**：单元测试 API 调用 → 数据是否正确？
5. **配置层**：验证 ISSNs、keyword 等 → 配置是否有效？

---

### 5. **数据流不对称理解** 🔄

**原则**：理解数据从哪里来、到哪里去、在哪里可能丢失。

**Weekly Bio Dashboard 的数据流**：
```
Crossref API (1505 papers)
    ↓ [去重：3层策略]
bioRxiv/medRxiv APIs
    ↓ [合并]
1200 papers (after dedup)
    ↓ [评分：56 keywords × 1200 papers]
Tagged & Scored
    ↓ [过滤：按阈值]
Dashboard Display
```

**关键问题**：
- 何处数据丢失最多？(dedup 那一层)
- 何处数据有偏差？(评分权重)
- 何处用户感知最强？(Dashboard 显示)

---

## 数据获取与集成

### 6. **API 集成最佳实践** 🔌

#### 重试策略
```python
for attempt in range(MAX_RETRIES):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        break
    except RequestException:
        time.sleep(0.6 * (2 ** attempt))  # 指数退避
```

**为什么**：
- 网络瞬时故障很常见
- 指数退避避免压垮 API
- timeout=30 防止无限等待

#### 速率限制
```python
CROSSREF_MIN_INTERVAL_S = 0.15  # 每个请求间隔 150ms
time.sleep(CROSSREF_MIN_INTERVAL_S)
```

**为什么**：
- 尊重 API 提供商
- 避免 IP 被封
- 是长期稳定的基础

#### 错误处理的三个层次
```python
# 1. API 网络错误
except requests.exceptions.RequestException:
    time.sleep(...)

# 2. HTTP 状态错误
if r.status_code >= 400:
    status = f"error (HTTP {r.status_code})"

# 3. JSON 解析错误
try:
    items = r.json().get("message", {}).get("items", [])
except Exception:
    status = "error (JSON parse)"
```

---

### 7. **去重策略** 🎯

**问题**：从多个 API 获取的论文可能重复。

**三层去重策略**（优先级从高到低）：
```python
# 第一层：DOI 去重（最准确）
df_with_doi = df[df["_has_doi"]].drop_duplicates(subset=["doi_norm"])

# 第二层：标题+期刊去重（次准确）
df = df.drop_duplicates(subset=["journal_norm", "title_norm"])

# 第三层：人工审查后修复
```

**关键点**：
- DOI 优先（唯一标识符）
- 保留第一次出现（Journals 优先于 Preprints）
- 可视化重复率监控

---

### 8. **缓存策略** ⏱️

**原则**：缓存 I/O 密集操作，但要设置合理的 TTL。

```python
@st.cache_data(show_spinner=True, ttl=3600)  # 1小时缓存
def refresh(journal_days, preprint_days, ...):
    # 获取 + 评分 + 去重
    return df, fetch_status, timestamp
```

**为什么 1 小时？**
- 新论文发布延迟 2-48 小时（Crossref 索引延迟）
- 1 小时内用户访问：秒级响应 (<2s)
- 超过 1 小时：自动刷新，无缝体验

---

## 问题诊断流程

### 9. **"网页打不开"的诊断树** 🌳

```
网页打不开
├── [1] 进程检查
│   ├── ps aux | grep streamlit
│   │   ├── ✓ 进程运行 → 进入 [2]
│   │   └── ✗ 进程不存在 → 检查启动错误
│   │       └── 查看 nohup.out / tail logs/
│   │
├── [2] 网络连接
│   ├── curl http://localhost:8501
│   │   ├── ✓ 返回 HTML → 进入 [3]
│   │   └── ✗ 连接拒绝 → 检查端口
│   │       └── lsof -i :8501 / netstat
│   │
├── [3] 前端加载
│   ├── 浏览器检查 Network/Console
│   │   ├── ✓ JS 加载成功 → 进入 [4]
│   │   └── ✗ JS 加载失败 → 检查静态资源
│   │       └── Streamlit 版本问题？
│   │
├── [4] 后端数据流
│   ├── 查看 app.py 日志
│   │   ├── ✓ 数据加载成功 → 进入 [5]
│   │   └── ✗ 数据加载失败 → 检查 API 调用
│   │       ├── 检查 config.py 是否有错误
│   │       ├── 检查 JOURNAL_ISSN 是否正确
│   │       └── 单独测试 crossref_fetch()
│   │
└── [5] 渲染层
    └── Streamlit 是否成功将数据渲染到 UI
```

**实战例子**：
```bash
# Step 1: 进程
ps aux | grep streamlit
→ 找到进程 PID 27820

# Step 2: 网络
curl http://localhost:8501
→ 返回 HTML（✓ 服务正常）

# Step 3: 前端（用户浏览器）
# 打开浏览器 DevTools → Network tab
# 检查是否有 failed requests

# Step 4: 后端
tail -f /tmp/streamlit.log
# 查看是否有 Python 异常

# Step 5: 业务逻辑
python3 -c "from fetchers import crossref_fetch; print(crossref_fetch('Nature', 7))"
# 测试 API 是否工作
```

---

### 10. **异常结果的诊断** 🔍

**场景**：显示数据但结果不对（如论文计数错误）

**诊断清单**：

| 检查项 | 方法 | 目的 |
|-------|------|------|
| API 数据 | `python fetchers.py` 单独运行 | 确认 API 返回正确数据 |
| 去重逻辑 | 检查 dedup 后的 DataFrame | 是否误删论文？ |
| 评分逻辑 | `scoring.py` 单元测试 | 关键词匹配是否正确？ |
| 配置 | 打印 CORE_KEYWORDS、ISSNs | 配置是否被正确加载？ |
| 缓存 | 清空 `.streamlit/cache/` | 是否用了过期的缓存数据？ |

---

## 前后端交互

### 11. **Streamlit 特有陷阱** ⚠️

#### 陷阱 1：重运行（Rerun）
**问题**：Streamlit 在任何交互时重新运行整个脚本。

```python
# ❌ 常见错误
search_query = st.text_input("搜索")  # 用户输入 → 整个脚本重新运行！

# ✅ 解决方案
@st.cache_data(ttl=3600)  # 缓存数据获取
def fetch_data():
    return ...

df = fetch_data()  # 第一次 3600s，之后立即返回
filtered = df[df["title"].str.contains(search_query)]  # 快速过滤
```

#### 陷阱 2：交互式输入阻塞
**问题**：如果用户在终端被提示输入（如邮箱），整个进程会阻塞。

```python
# ❌ Streamlit 启动时不要有交互式输入
# (这是为什么我们用 echo "" | nohup streamlit run app.py)

# ✅ 如果需要配置，放在 .env 文件或命令行参数
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
```

#### 陷阱 3：Session State
**问题**：`st.session_state` 用于维护状态，但每次重运行会重置。

```python
# ✅ 正确用法：跨重运行保持状态
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment"):
    st.session_state.counter += 1
st.write(st.session_state.counter)
```

---

### 12. **前端调试技巧** 🐛

#### 检查 1：网络请求
```bash
# 在浏览器 DevTools → Network 中查看
# 每个 Streamlit 请求的状态码是什么？

# 通常：
# - 初次加载：200 OK
# - 交互时：WebSocket 连接，数据流通过 ws://

# 如果看到 5xx：后端有异常
# 如果看到连接超时：后端数据取太久
```

#### 检查 2：控制台错误
```javascript
// 浏览器 DevTools → Console 中查看
// 是否有 JS 错误？

// 常见错误：
// 1. "Uncaught SyntaxError" → Streamlit 版本问题
// 2. "Cannot read property of undefined" → 数据格式不对
// 3. "WebSocket connection failed" → 后端断开连接
```

#### 检查 3：后端日志
```bash
tail -f /tmp/streamlit.log
# 查看实时日志，看是否有 Python traceback

# 添加调试输出：
import streamlit as st
st.write("DEBUG: df shape =", df.shape)  # 会显示在前端
```

---

## 需求理解与迭代

### 13. **"显示 0 论文"问题的完整迭代** 📊

**第一版理解**（错误）：
> "这些期刊返回 0 论文，说明配置有问题，删除它们吧"

↓ 验证后发现：
- ISSNs 是正确的（去 ISSN.org 验证）
- API 调用是成功的（status="ok"）
- 0 论文是正常现象（期刊最近没发表）

**第二版理解**（部分正确）：
> "所有返回 0 论文的期刊都应该被删除"

↓ 用户反馈：
- 不，这些期刊是有的，只是最近没有新论文
- 保留配置，但让我知道为什么显示 0

**第三版理解**（正确）✅：
> "保留所有配置，但在 UI 中显示诊断信息，告诉用户：
> - 如果是 status='ok' 且 count=0：说明 API 正常但期刊最近没发表
> - 如果是 status='error'：说明 API 出问题了，需要检查"

**关键教训**：
- 验证需求前问用户，不要自己假设
- 一个"异常"可能其实是正常行为
- UI 透明度可以消除用户困惑

---

### 14. **迭代反馈循环** 🔄

**正确的流程**：
```
1. 用户报告问题
   ↓
2. 诊断根本原因（不假设）
   ↓
3. 向用户解释（透明度）
   ↓
4. 提出 2-3 个解决方案
   ↓
5. 用户选择
   ↓
6. 实施并验证
   ↓
7. 文档更新（写到配置注释中）
```

**坏的流程** ❌：
```
用户说"这不对" → 直接改代码 → 推送
(用户后来说"不对，我要那个功能回来")
```

---

## 常见陷阱与规避

### 15. **数据驱动的三个层次** 📊

#### 第一层：看结果
```python
# ❌ 只看结果
papers_count = 1200
# "太好了，数据很多"
```

#### 第二层：检查过程
```python
# ✅ 检查数据来源
papers_from_crossref = 1505  # 原始
papers_after_dedup = 1200    # 去重后
dedup_rate = (1505 - 1200) / 1505 * 100  # 20.3% 被删除

# 问题：是否删除太多了？
```

#### 第三层：验证准确性
```python
# ✅✅ 抽样验证
# 检查被删除的 305 篇论文中：
# - 有多少是真正的重复？
# - 有多少是假阳性（不应该删）？
# - 有多少缺少 DOI 因此可能误删？

sample_removed = df_removed.sample(20)
# 手动审查这 20 篇是否应该被删
```

---

### 16. **外部依赖的脆弱性** 🌐

**问题**：依赖外部 API（Crossref、bioRxiv）。

**规避方法**：

| 策略 | 实施 | 成本 |
|-----|------|------|
| **重试** | 指数退避 + 多次尝试 | 低 ✅ |
| **缓存** | 1 小时 TTL | 低 ✅ |
| **降级** | API 失败时显示旧数据 | 中 ⚠️ |
| **本地备份** | 定期保存到 DB | 高 ❌ |
| **多源** | 添加备选 API | 高 ❌ |

**推荐**：前两种足够。

---

### 17. **配置管理** ⚙️

**反面例子**：
```python
# ❌ 硬编码
JOURNALS = ["Cell", "Nature", "Science", ...]
KEYWORDS = {...}

# 修改需要改代码 → 重新部署
```

**正面例子**：
```python
# ✅ 配置文件
# config.py - 单一修改点
JOURNALS = [...]
CORE_KEYWORDS = {...}

# 用户修改配置.py → 重启应用 → 自动生效

# 甚至可以：
# config.toml → CLI 读取 → 无需重启
```

---

## 文档与透明度

### 18. **代码注释的三个层次** 💬

#### 第一层：为什么（最重要）
```python
# 为什么用 0.15s 的间隔？
# Crossref API 建议最少 10 requests/sec，我们选择更保守的 ~6.7 req/sec
# 这样既不会被限流，也不会对服务造成压力
CROSSREF_MIN_INTERVAL_S = 0.15
```

#### 第二层：怎么做
```python
# 指数退避重试
for attempt in range(MAX_RETRIES):
    try:
        r = requests.get(...)
        break
    except:
        time.sleep(0.6 * (2 ** attempt))  # 0.6s, 1.2s, 2.4s
```

#### 第三层：是什么
```python
time.sleep(CROSSREF_MIN_INTERVAL_S)  # 等待 API 频率限制
```

**优先级**：为什么 > 怎么做 > 是什么

---

### 19. **诊断信息的质量** 🎯

**差**：
```
Status: error
Detail: HTTP 500
```

**好**：
```
Status: ⚠
Detail: HTTP 500 (Crossref API unavailable; retrying...)
```

**更好**：
```
Status: ⚠
Detail: HTTP 500 - Crossref API returned error on attempt 2/3;
        will retry in 1.2s (exponential backoff)
```

**原则**：
- 用户应该理解发生了什么
- 用户应该知道系统是否在恢复
- 用户应该知道何时预期恢复

---

### 20. **版本控制与提交信息** 📝

**差的提交**：
```
git commit -m "fix stuff"
```

**好的提交**：
```
git commit -m "fix: add diagnostic details to fetch status

- Show 'ok (no recent publications)' when journal returns 0 papers
- Helps users understand why certain journals show 0 results
- Visual indicators: ✓ for success, ⚠ for error
- No API issues, just normal publishing schedule variation"
```

**为什么重要**：
- 6 个月后的你需要理解你做了什么
- 团队成员需要理解变更原因
- 问题诊断时可以查看 git log 理解历史决策

---

## 总结：快速参考

### ✅ 做这些

| 做法 | 理由 |
|------|------|
| 验证假设 | 0 论文不一定是配置错误 |
| 显示诊断信息 | 用户应该理解为什么 |
| 测试单个组件 | 分层诊断效率高 |
| 保留配置注释 | 文档即代码 |
| 使用缓存 | 加速常见操作 |
| 指数退避重试 | 尊重 API，避免限流 |

### ❌ 避免这些

| 反面 | 危害 |
|------|------|
| 立即删除"异常"的配置 | 可能删除有效配置 |
| 隐藏错误信息 | 用户困惑 |
| 硬编码配置 | 修改困难，易出错 |
| 忽视外部 API 可靠性 | 系统脆弱 |
| 模糊的提交信息 | 难以追踪历史 |
| 过度设计 | 复杂性超过价值 |

---

## 实战案例分析

### 案例：Weekly Bio Dashboard 的完整迭代

**第一周**：
- 实现基础的论文获取 + Streamlit UI
- 用户发现某些期刊显示 0 论文

**第二周**（我的错误方案）：
- 直接删除这些期刊
- 推送到 master
- 用户：不对，保留这些期刊

**第三周**（正确方案）：
- 恢复配置
- 理解根本原因（ISSNs 正确，只是期刊最近没发表）
- 增强 UI：显示诊断信息
- 文档更新：解释为什么保留这些期刊

**结果**：
- ✅ 用户满意
- ✅ 代码更健壮
- ✅ 知识积累到文档

---

## 下次做类似项目时的检查清单

### 项目启动
- [ ] 充分理解需求（不要假设）
- [ ] 确认外部 API 的可靠性
- [ ] 设计缓存策略
- [ ] 计划错误处理

### 开发中
- [ ] 分层测试（单元 → 集成 → 端到端）
- [ ] 添加诊断输出
- [ ] 写清楚注释（特别是"为什么"）
- [ ] 定期检查 git log 的提交信息质量

### 部署前
- [ ] 手动测试完整流程
- [ ] 检查所有错误情况（网络超时、API 失败等）
- [ ] 验证缓存行为
- [ ] 确保 UI 显示有意义的信息

### 部署后
- [ ] 监控日志
- [ ] 收集用户反馈
- [ ] 迭代改进（不是修复，是理解 + 改进）

---

## 最后的话

> "一个异常结果不一定意味着配置错误；可能只是数据在某一层的正常表现。"
>
> "用户困惑通常源于信息不透明，而不是功能不对。"
>
> "代码的可维护性不在于有多精妙，而在于有多清楚。"

---

**文档版本**：1.0
**最后更新**：2026-03-17
**应用项目**：Weekly Bio Dashboard v3.0+
