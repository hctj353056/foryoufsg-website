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

## 添加新内容

- **古诗**：编辑 `knowledge-base/original-works/poetry/诗词.json`，追加条目即可
- **散文**：编辑 `knowledge-base/original-works/articles/散文.json`，追加条目即可
- **链接**：编辑 `social/index.html`，追加 `<a>` 标签

## 技术栈

- HTML5 + CSS3
- 原生 JavaScript（ES6+，fetch + 模板渲染）
- GitHub Pages 托管

## 部署

推送 `main` 分支后 GitHub Pages 自动部署。

## 许可证

个人网站不开源

***

蜉蝣子 ♡

***

*蜉蝣阁 · foryoufsg-website*
