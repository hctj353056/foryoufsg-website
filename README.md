# 蜉蝣阁 · 个人博客

> 蜉蝣的个人博客，诗词文章与社交链接

## 在线访问

- 域名: <https://fsg.foryoufsg.com>
- GitHub Pages: <https://hctj353056.github.io/foryoufsg-website/>

## 项目结构

```
foryoufsg-website/
├── index.html              # 博客主页（诗+文按时间线合并）
├── poetry/
│   └── index.html          # 古诗板块
├── essays/
│   └── index.html          # 散文板块
├── social/
│   └── index.html          # 社交媒体链接页
├── wiki-src/               # 词库源（Markdown）
│   ├── 内容/               # 词条，文件夹即分组
│   ├── 素材/
│   │   ├── 样式.css        # 词库样式
│   │   └── 检索.js         # 检索引擎
│   └── 构建.py             # 生成器，零依赖
├── wiki/                   # 词库产物（构建生成，不入库）
├── css/
│   └── style.css           # 共享样式
├── js/
│   └── blog-loader.js      # 数据加载与渲染
├── knowledge-base/         # 数据存储
│   └── original-works/
│       ├── poetry/
│       │   ├── 诗词.json   # 诗词数据
│       │   └── images/     # 诗词配图
│       └── articles/
│           ├── 散文.json   # 散文数据
│           └── images/     # 散文配图
├── CNAME                   # 自定义域名
├── .github/workflows/      # GitHub Pages 自动部署
├── README.md
└── LICENSE
```

## 版块说明

| 版块 | 路径 | 说明 |
|------|------|------|
| 博客 | `/` | 诗词与散文按时间线合并展示 |
| 古诗 | `/poetry/` | 原创古诗词列表 |
| 散文 | `/essays/` | 原创散文列表 |
| 链接 | `/social/` | 社交媒体与外部链接 |
| 词库 | `/wiki/` | 词条式知识库，双链互引 + 全文检索 |

## 添加新内容

- **古诗**：编辑 `knowledge-base/original-works/poetry/诗词.json`，追加条目即可
- **散文**：编辑 `knowledge-base/original-works/articles/散文.json`，追加条目即可
- **链接**：编辑 `social/index.html`，追加 `<a>` 标签
- **词条**：见下节

## 词库

### 写一条词条

在 `wiki-src/内容/<分组>/` 下新建 `.md`，文件夹名即分组：

```markdown
---
标题: 模态逻辑
别名: Modal Logic, 必然算子
标签: 逻辑学, 哲学
---

正文里直接写 [[形式系统]]，或 [[形式系统|换个显示名]]。
```

`标题` 是唯一必填项，缺省时取文件名。`别名` 参与检索加权，`标签` 同时作为分类线索。

### 双链与红链

`[[词条名]]` 在构建时解析为相对路径，**改文件夹、改文件名都不会断链**。指向尚不存在的词条会渲染成红色虚线——它就是待办清单，首页统计里的「待建」数量即来自这里。

构建同时会统计反向链接，显示在词条页底部。

### 构建

```bash
python3 wiki-src/构建.py
```

产物写入 `wiki/`（已在 `.gitignore` 中）。**只改 `wiki-src/`，不要手改 `wiki/`**，每次构建都会清空重建。

推送到 `main` 后 Actions 会自动构建并部署，无需手动提交产物。

### 检索规则

| 输入 | 行为 |
|------|------|
| `形式` | 子串匹配，加权排序：标题 > 别名 > 标签 > 摘要 > 正文 |
| `形式 系统` | 空格分词，AND 语义 |
| `/证明.*验证/` | 正则模式，`try/catch` 兜住非法表达式 |

索引内嵌在首页，因此 `file://` 直接打开也能检索，不需要起服务器。

## 技术栈

- HTML5 + CSS3
- 原生 JavaScript（ES6+，fetch + 模板渲染）
- Python 3（词库构建，零外部依赖）
- GitHub Pages 托管

## 部署

推送 `main` 分支后 GitHub Pages 自动部署。

## 许可证

个人网站不开源

***

蜉蝣子 ♡

***

*蜉蝣阁 · foryoufsg-website*
