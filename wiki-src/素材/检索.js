/* ==========================================
   蜉蝣阁 · 词库检索
   子串加权为主，/正则/ 为高级模式
   零依赖，file:// 下亦可运行
   ========================================== */
(function () {
  "use strict";

  var 库 = window.词库 || [];
  var 首页 = !!window.是首页;
  var 前缀 = window.前缀 || "";

  var 输入框 = document.getElementById("搜");
  var 面板 = document.getElementById("搜面板");
  var 列表 = document.getElementById("结果列表");
  var 提示 = document.getElementById("搜提示");
  var 正文区 = document.getElementById("正文区");

  /* ── 工具 ── */
  function 转义(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function 分词(q) {
    return q.trim().toLowerCase().split(/\s+/).filter(Boolean);
  }

  function 高亮(已转义, 词) {
    if (!词 || !词.length) return 已转义;
    var 有序 = 词.slice().sort(function (a, b) { return b.length - a.length; });
    var 段 = 有序.map(function (w) {
      return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }).filter(Boolean).join("|");
    if (!段) return 已转义;
    try {
      return 已转义.replace(new RegExp("(" + 段 + ")", "gi"), "<mark>$1</mark>");
    } catch (e) {
      return 已转义;
    }
  }

  function 摘录(正文, 词, 长度) {
    if (!正文) return "";
    长度 = 长度 || 88;
    var 低 = 正文.toLowerCase(), 位 = -1;
    for (var i = 0; i < 词.length; i++) {
      var p = 低.indexOf(词[i]);
      if (p !== -1 && (位 === -1 || p < 位)) 位 = p;
    }
    if (位 === -1) return 正文.slice(0, 长度) + (正文.length > 长度 ? "…" : "");
    var 起 = Math.max(0, 位 - 26);
    var 止 = Math.min(正文.length, 位 + 长度 - 26);
    return (起 > 0 ? "…" : "") + 正文.slice(起, 止) + (止 < 正文.length ? "…" : "");
  }

  /* ── 打分 ── */
  function 打分(条, 词) {
    var 标题 = (条.标题 || "").toLowerCase();
    var 别名 = (条.别名 || []).map(function (x) { return x.toLowerCase(); });
    var 标签 = (条.标签 || []).map(function (x) { return x.toLowerCase(); });
    var 摘要 = (条.摘要 || "").toLowerCase();
    var 正文 = (条.正文 || "").toLowerCase();
    var 总 = 0;

    for (var i = 0; i < 词.length; i++) {
      var w = 词[i], s = 0;
      if (标题 === w) s = 1000;
      else if (别名.indexOf(w) !== -1) s = 900;
      else if (标题.indexOf(w) !== -1) s = 620 - Math.min(标题.length, 120);
      else if (别名.some(function (a) { return a.indexOf(w) !== -1; })) s = 470;
      else if (标签.some(function (t) { return t.indexOf(w) !== -1; })) s = 330;
      else if (摘要.indexOf(w) !== -1) s = 180;
      else if (正文.indexOf(w) !== -1) s = 70;
      else return 0;
      总 += s;
    }
    return 总;
  }

  /* ── 搜索 ── */
  function 搜索(原串) {
    var q = (原串 || "").trim();
    if (!q) { 还原(); return; }

    var 结果 = [], 词 = [], 说明 = "";

    if (/^\/.+\/[gimsuy]*$/.test(q)) {
      var 末 = q.lastIndexOf("/");
      var 源 = q.slice(1, 末);
      var 旗 = q.slice(末 + 1) || "i";
      var 式;
      try { 式 = new RegExp(源, 旗); }
      catch (e) {
        提示.innerHTML = "正则写法有误：" + 转义(e.message);
        列表.innerHTML = "";
        显示面板();
        return;
      }
      词 = [源];
      库.forEach(function (条) {
        var 全 = [条.标题, (条.别名 || []).join(" "), (条.标签 || []).join(" "),
                  条.摘要, 条.正文].join("\n");
        if (式.test(全)) 结果.push({ 条: 条, 分: 100 });
      });
      说明 = "正则 <code>" + 转义(q) + "</code>";
    } else {
      词 = 分词(q);
      库.forEach(function (条) {
        var 分 = 打分(条, 词);
        if (分 > 0) 结果.push({ 条: 条, 分: 分 });
      });
      说明 = 词.map(function (w) { return "<b>" + 转义(w) + "</b>"; }).join(" + ");
    }

    结果.sort(function (a, b) { return b.分 - a.分; });

    if (!结果.length) {
      列表.innerHTML = '<div class="空态"><div>∅</div>没有词条命中「' + 转义(q) +
        '」<br>换个词，或者新建一条 .md —— 也能写成 <code>[[词条名]]</code> 留在正文里，它会变成红链待办。</div>';
      提示.innerHTML = "共 0 条";
      显示面板();
      return;
    }

    列表.innerHTML = 结果.slice(0, 40).map(function (r, i) {
      var 条 = r.条;
      var 片 = 摘录(条.正文, 词) || 条.摘要 || "";
      var 签 = (条.标签 || []).map(function (t) {
        return '<span class="标签">' + 转义(t) + "</span>";
      }).join("");
      return '<a class="结果卡' + (i === 0 ? " 选中" : "") + '" href="' +
        encodeURI(条.路径) + '">' +
        '<div class="结果题">' + 高亮(转义(条.标题), 词) + "</div>" +
        '<div class="结果径">' + 转义(条.分组 || "") + " · " + 转义(条.文件) + "</div>" +
        (片 ? '<div class="结果摘">' + 高亮(转义(片), 词) + "</div>" : "") +
        (签 ? '<div class="结果签">' + 签 + "</div>" : "") +
        "</a>";
    }).join("");

    提示.innerHTML = "共 <b>" + 结果.length + "</b> 条 · 匹配 " + 说明;
    显示面板();
  }

  function 显示面板() {
    if (面板) 面板.classList.add("显示");
    if (正文区) 正文区.style.display = "none";
  }
  function 还原() {
    if (面板) 面板.classList.remove("显示");
    if (正文区) 正文区.style.display = "";
    if (提示) 提示.innerHTML = "";
  }

  /* ── 键盘 ── */
  var 选中 = 0;
  function 移动(方向) {
    var 卡们 = 列表.querySelectorAll(".结果卡");
    if (!卡们.length) return;
    if (卡们[选中]) 卡们[选中].classList.remove("选中");
    选中 = (选中 + 方向 + 卡们.length) % 卡们.length;
    卡们[选中].classList.add("选中");
    卡们[选中].scrollIntoView({ block: "nearest" });
  }

  if (输入框) {
    输入框.addEventListener("input", function () { 选中 = 0; 搜索(输入框.value); });
    输入框.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); 移动(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); 移动(-1); }
      else if (e.key === "Enter") {
        var 卡 = 列表.querySelector(".结果卡.选中");
        if (卡) location.href = 卡.getAttribute("href");
      } else if (e.key === "Escape") { 输入框.value = ""; 还原(); 输入框.blur(); }
    });
  }

  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      if (输入框) { 输入框.focus(); 输入框.select(); }
      else location.href = 前缀 + "index.html";
    }
  });

  if (!首页) {
    /* 词条页不重复携带索引，搜索统一回首页做 */
    if (输入框) {
      输入框.addEventListener("focus", function () {
        输入框.blur();
        location.href = 前缀 + "index.html";
      });
    }
  } else {
    var m = location.search.match(/[?&]q=([^&]*)/);
    if (m && 输入框) {
      var 初 = decodeURIComponent(m[1]);
      输入框.value = 初;
      搜索(初);
    }
  }

  window.执行搜索 = 搜索;
})();
