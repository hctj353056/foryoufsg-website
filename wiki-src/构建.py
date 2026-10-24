#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蜉蝣阁 · 词库生成器
==================
wiki-src/内容/**/*.md  ──本脚本──▶  wiki/**/*.html

约定
----
1. 内容/ 下任意层级放 .md，文件夹名即分组
2. 文件开头可写 front matter：标题 / 别名 / 标签 / 摘要
3. 正文用 [[词条名]] 互链；指向尚不存在的词条会自动渲染为红链
4. 每次构建会清空并重建 wiki/ —— 只改 wiki-src/，别手改产物

零第三方依赖，Python 3.8+
"""

import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

# ═══════════════ 配置 ═══════════════
站点名 = "蜉蝣阁"
分类名 = "词库"
站点说明 = "按文件夹分类、靠双链互引、可全文检索的静态知识库。每一条都是独立的 Markdown 文件，改动即刻可查。"

索引上限 = 160        # 索引里每篇正文最多存多少字，控制首页体积
最多结果 = 40         # 搜索结果最多显示几条

源码目录 = Path(__file__).resolve().parent
内容目录 = 源码目录 / "内容"
素材目录 = 源码目录 / "素材"
仓库根 = 源码目录.parent
输出目录 = 仓库根 / "wiki"


# ═══════════════ 读取 ═══════════════
def 拆前言(原文):
    元 = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", 原文, re.S)
    if not m:
        return 元, 原文
    for 行 in m.group(1).splitlines():
        行 = 行.strip()
        if not 行 or 行.startswith("#") or ":" not in 行:
            continue
        键, 值 = 行.split(":", 1)
        元[键.strip()] = 值.strip()
    return 元, m.group(2)


def 拆列表(值):
    return [x.strip() for x in re.split(r"[,，、;；]", 值 or "") if x.strip()]


def 去标记(文本):
    t = re.sub(r"```.*?```", " ", 文本, flags=re.S)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]",
               lambda m: m.group(2) or m.group(1), t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.M)
    t = re.sub(r"[`*_>|~]+", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def 取摘要(正文):
    for 段 in re.split(r"\n\s*\n", 正文):
        段 = 段.strip()
        if not 段 or 段.startswith(("#", "```", "|")):
            continue
        干净 = 去标记(段)
        if len(干净) >= 12:
            return 干净[:110] + ("…" if len(干净) > 110 else "")
    return ""


def 读全部词条():
    词条们 = []
    for 路径 in sorted(内容目录.rglob("*.md")):
        原文 = 路径.read_text(encoding="utf-8")
        元, 正文 = 拆前言(原文)
        相对 = 路径.relative_to(内容目录)
        分组 = str(相对.parent).replace(os.sep, "/")
        if 分组 == ".":
            分组 = "未分类"
        纯文 = 去标记(正文)
        词条们.append({
            "编号": str(相对.with_suffix("")).replace(os.sep, "/"),
            "标题": 元.get("标题") or 路径.stem,
            "别名": 拆列表(元.get("别名")),
            "标签": 拆列表(元.get("标签")),
            "分组": 分组,
            "文件": 路径.name,
            "路径": str(相对.with_suffix(".html")).replace(os.sep, "/"),
            "摘要": 元.get("摘要") or 取摘要(正文),
            "正文": 纯文[:索引上限],
            "全文": 纯文,
            "源": 正文,
        })
    return 词条们


# ═══════════════ Markdown ═══════════════
def 建名表(词条们):
    表 = {}
    for 条 in 词条们:
        表[条["标题"].lower()] = 条
        表[条["编号"].lower()] = 条
        for a in 条["别名"]:
            表.setdefault(a.lower(), 条)
    return 表


def 拼句(a, b):
    if not a:
        return b
    if not b:
        return a
    if ("\u4e00" <= a[-1] <= "\u9fff") or ("\u4e00" <= b[0] <= "\u9fff"):
        return a + b
    return a + " " + b


def 行内(文本, 当前条, 名表):
    s = html.escape(文本, quote=False)
    占位 = []

    def 存(片段):
        占位.append(片段)
        return "\x00%d\x00" % (len(占位) - 1)

    s = re.sub(r"`([^`]+)`", lambda m: 存("<code>%s</code>" % m.group(1)), s)

    def 换双链(m):
        目标名 = m.group(1).strip()
        显示 = (m.group(2) or 目标名).strip()
        目标 = 名表.get(目标名.lower())
        if 目标:
            相对 = os.path.relpath(目标["路径"], os.path.dirname(当前条["路径"]) or ".")
            return '<a class="双链" href="%s">%s</a>' % (
                re.sub(r"\\", "/", 相对), 显示)
        return '<span class="红链" title="尚未创建：%s">%s</span>' % (目标名, 显示)

    s = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", 换双链, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)

    for i, 片 in enumerate(占位):
        s = s.replace("\x00%d\x00" % i, 片)
    return s


def 渲染(源文, 当前条, 名表):
    行们 = 源文.replace("\r\n", "\n").split("\n")
    结果 = []
    i, n = 0, len(行们)

    while i < n:
        去空 = 行们[i].strip()

        if 去空.startswith("```"):
            i += 1
            块 = []
            while i < n and not 行们[i].strip().startswith("```"):
                块.append(行们[i])
                i += 1
            i += 1
            结果.append("<pre><code>%s</code></pre>" % html.escape("\n".join(块)))
            continue

        if not 去空:
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", 去空):
            结果.append("<hr>")
            i += 1
            continue

        # 表格
        if 去空.startswith("|") and i + 1 < n and re.match(
                r"^\|?[\s:\-|]+\|?$", 行们[i + 1].strip()) and "-" in 行们[i + 1]:
            表头 = [c.strip() for c in 去空.strip("|").split("|")]
            i += 2
            行集 = []
            while i < n and 行们[i].strip().startswith("|"):
                行集.append([c.strip() for c in 行们[i].strip().strip("|").split("|")])
                i += 1
            片段 = ["<table><thead><tr>"]
            片段 += ["<th>%s</th>" % 行内(c, 当前条, 名表) for c in 表头]
            片段.append("</tr></thead><tbody>")
            for r in 行集:
                片段.append("<tr>" + "".join(
                    "<td>%s</td>" % 行内(c, 当前条, 名表) for c in r) + "</tr>")
            片段.append("</tbody></table>")
            结果.append("".join(片段))
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", 去空)
        if m:
            级 = min(len(m.group(1)) + 1, 6)
            结果.append("<h%d>%s</h%d>" % (级, 行内(m.group(2), 当前条, 名表), 级))
            i += 1
            continue

        if 去空.startswith(">"):
            段 = []
            while i < n and 行们[i].strip().startswith(">"):
                段.append(行们[i].strip().lstrip(">").strip())
                i += 1
            结果.append("<blockquote><p>%s</p></blockquote>" %
                        " ".join(行内(x, 当前条, 名表) for x in 段 if x))
            continue

        m = re.match(r"^([-*+]|\d+\.)\s+", 去空)
        if m:
            有序 = m.group(1)[0].isdigit()
            标签名 = "ol" if 有序 else "ul"
            项 = []
            while i < n:
                当前 = 行们[i].strip()
                mm = re.match(r"^([-*+]|\d+\.)\s+(.*)$", 当前)
                if not mm:
                    if 当前.startswith("  ") and 项:
                        项[-1] += " " + 当前
                        i += 1
                        continue
                    break
                if mm.group(1)[0].isdigit() != 有序:
                    break
                项.append(mm.group(2))
                i += 1
            结果.append("<%s>%s</%s>" % (
                标签名, "".join("<li>%s</li>" % 行内(x, 当前条, 名表) for x in 项), 标签名))
            continue

        段 = [去空]
        i += 1
        while i < n:
            下 = 行们[i].strip()
            if not 下 or re.match(r"^(#{1,6}\s|[-*+]\s|\d+\.\s|>|\||```|-{3,}$)", 下):
                break
            段.append(下)
            i += 1
        合并 = ""
        for x in 段:
            合并 = 拼句(合并, x)
        结果.append("<p>%s</p>" % 行内(合并, 当前条, 名表))

    return "\n".join(结果)


# ═══════════════ 骨架 ═══════════════
词条们全局 = []
当前编号全局 = None


def 侧栏(前缀, 当前编号=None):
    分组表 = {}
    for 条 in 词条们全局:
        分组表.setdefault(条["分组"], []).append(条)

    片段 = ['<div class="侧栏题">%s·%s</div>' % (站点名, 分类名)]
    for 组 in sorted(分组表):
        片段.append('<div class="分类块">')
        片段.append('<div class="分类标题">%s<em>%d</em></div>' % (
            html.escape(组), len(分组表[组])))
        for 条 in sorted(分组表[组], key=lambda x: x["标题"]):
            类 = ' class="当前"' if 条["编号"] == 当前编号 else ""
            片段.append('<a href="%s%s"%s>%s</a>' % (
                前缀, re.sub(r"\\", "/", 条["路径"]), 类, html.escape(条["标题"])))
        片段.append("</div>")
    return "\n".join(片段)


def 顶栏(站根前缀):
    return (
        '<div class="顶栏">'
        '<a class="站名" href="%sindex.html">%s<span>·%s</span></a>'
        '<div class="搜索盒"><input id="搜" placeholder="搜索词条" autocomplete="off" spellcheck="false">'
        '<span class="键位">Ctrl K</span></div>'
        '<nav class="顶导航">'
        '<a href="%sindex.html">博客</a>'
        '<a href="%spoetry/">古诗</a>'
        '<a href="%sessays/">散文</a>'
        '<a href="%ssocial/">链接</a>'
        '</nav>'
        '</div>' % (站根前缀, html.escape(站点名), html.escape(分类名),
                    站根前缀, 站根前缀, 站根前缀, 站根前缀)
    )


def 页面(标题, 主体, 深, 额外脚本="", 是首页=False):
    css = (素材目录 / "样式.css").read_text(encoding="utf-8")
    js = (素材目录 / "检索.js").read_text(encoding="utf-8")
    站根前缀 = "../" * (深 + 1)
    词库前缀 = "../" * 深
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<style>
%s
</style>
</head>
<body>
%s
<div class="外壳">
<aside class="侧栏">%s</aside>
<main class="主区">
%s
</main>
</div>
<script>window.站根前缀=%s;window.词库前缀=%s;window.是首页=%s;%s</script>
<script>
%s
</script>
</body>
</html>""" % (
        标题 + " · " + 站点名 + 分类名,
        css,
        顶栏(站根前缀),
        侧栏(词库前缀, 当前编号全局),
        主体,
        json.dumps(站根前缀), json.dumps(词库前缀),
        "true" if 是首页 else "false",
        额外脚本,
        js,
    )


# ═══════════════ 构建 ═══════════════
def 构建():
    global 词条们全局, 当前编号全局

    if not 内容目录.is_dir():
        print("找不到内容目录：", 内容目录)
        return 1

    词条们 = 读全部词条()
    if not 词条们:
        print("内容目录里没有 .md 文件。")
        return 1
    词条们全局 = 词条们
    名表 = 建名表(词条们)

    反链 = {条["编号"]: [] for 条 in 词条们}
    for 条 in 词条们:
        for 名 in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", 条["源"]):
            目标 = 名表.get(名.strip().lower())
            if 目标 and 目标["编号"] != 条["编号"]:
                if 条["标题"] not in 反链[目标["编号"]]:
                    反链[目标["编号"]].append(条["标题"])

    if 输出目录.exists():
        shutil.rmtree(输出目录)
    输出目录.mkdir(parents=True)

    # ── 词条页 ──
    for 条 in 词条们:
        当前编号全局 = 条["编号"]
        深 = len(Path(条["路径"]).parts) - 1
        前缀 = "../" * 深         # 回到词库根
        站根 = "../" * (深 + 1)   # 回到仓库根

        正文 = 渲染(条["源"], 条, 名表)
        面包 = '<a href="%sindex.html">%s</a> / <a href="%sindex.html#%s">%s</a>' % (
            前缀, 分类名, 前缀, html.escape(条["分组"]), html.escape(条["分组"]))

        标签 = ""
        if 条["标签"]:
            标签 = '<div class="标签行">%s</div>' % "".join(
                '<span class="标签">%s</span>' % html.escape(t) for t in 条["标签"])

        反链块 = ""
        if 反链[条["编号"]]:
            项 = []
            for 名 in 反链[条["编号"]]:
                目标 = next(x for x in 词条们 if x["标题"] == 名)
                项.append('<li><a href="%s%s">%s</a></li>' % (
                    前缀, re.sub(r"\\", "/", 目标["路径"]), html.escape(名)))
            反链块 = '<div class="反链区"><h3>被以下词条引用</h3><ul>%s</ul></div>' % "".join(项)

        主体 = """<div id="正文区">
<article>
<h1>%s</h1>
<div class="面包屑">%s</div>
%s
%s
%s
</article>
<div class="页脚"><a href="%sindex.html">← 返回%s</a></div>
</div>
<div class="搜面板" id="搜面板">
<div class="搜提示" id="搜提示"></div>
<div id="结果列表"></div>
</div>""" % (html.escape(条["标题"]), 面包, 正文, 标签, 反链块, 前缀, 分类名)

        目标 = 输出目录 / 条["路径"]
        目标.parent.mkdir(parents=True, exist_ok=True)
        目标.write_text(页面(条["标题"], 主体, 深), encoding="utf-8")

    # ── 首页 ──
    当前编号全局 = None
    分组表 = {}
    for 条 in 词条们:
        分组表.setdefault(条["分组"], []).append(条)

    卡片 = []
    for 组 in sorted(分组表):
        卡片.append('<div class="分组标题" id="%s">%s<em>%d 条</em></div>' % (
            html.escape(组), html.escape(组), len(分组表[组])))
        for 条 in sorted(分组表[组], key=lambda x: x["标题"]):
            卡片.append(
                '<a class="词条卡" href="%s"><div class="题">%s</div>'
                '<div class="摘">%s</div></a>' % (
                    re.sub(r"\\", "/", 条["路径"]),
                    html.escape(条["标题"]),
                    html.escape(条["摘要"] or "（还没写摘要）")))

    已建 = set(x["标题"] for x in 词条们)
    全链 = set(re.findall(r"\[\[([^\]|]+)", "".join(x["源"] for x in 词条们)))
    红链数 = len(全链 - 已建)

    主体 = """<div id="正文区">
<div class="首页头">
<h1>%s<span>·%s</span></h1>
<p>%s</p>
</div>
<div class="统计行">
<div class="统计"><b>%d</b><span>词条</span></div>
<div class="统计"><b>%d</b><span>分组</span></div>
<div class="统计"><b>%d</b><span>待建</span></div>
</div>
%s
</div>
<div class="搜面板" id="搜面板">
<div class="搜提示" id="搜提示"></div>
<div id="结果列表"></div>
</div>""" % (站点名, 分类名, html.escape(站点说明),
             len(词条们), len(分组表), 红链数, "\n".join(卡片))

    索引 = [{
        "标题": 条["标题"], "别名": 条["别名"], "标签": 条["标签"],
        "分组": 条["分组"], "文件": 条["文件"], "路径": 条["路径"],
        "摘要": 条["摘要"], "正文": 条["正文"],
    } for 条 in 词条们]

    额外 = "window.词库=%s;" % json.dumps(索引, ensure_ascii=False, separators=(",", ":"))

    (输出目录 / "index.html").write_text(
        页面("首页", 主体, 0, 额外, 是首页=True), encoding="utf-8")

    print("词库构建完成：%d 条词条 / %d 个分组 / %d 处待建" % (len(词条们), len(分组表), 红链数))
    print("输出：", 输出目录)
    return 0


if __name__ == "__main__":
    sys.exit(构建())
