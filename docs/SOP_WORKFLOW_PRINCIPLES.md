# 论文项目与泛化任务 SOP — 工作心法与最佳实践

> 本文档总结了在开发 Weekly Bio Dashboard 及类似项目中学到的核心原则和工作流程

## 📋 目录
1. [数据获取与集成](#数据获取与集成)
3. [问题诊断流程](#问题诊断流程)
4. [前后端交互](#前后端交互)
5. [需求理解与迭代](#需求理解与迭代)
6. [常见陷阱与规避](#常见陷阱与规避)
7. [文档与透明度](#文档与透明度)



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

