/* ==========================================
   蜉蝣阁 · 博客数据加载器
   统一管理诗词与散文的加载、合并、渲染
   2026.06.23 / 作者：蜉蝣
   ========================================== */

const DATA_PATHS = {
  poem: '/knowledge-base/original-works/poetry/诗词.json',
  essay: '/knowledge-base/original-works/articles/散文.json',
  poemImg: '/knowledge-base/original-works/poetry/images/',
  essayImg: '/knowledge-base/original-works/articles/images/',
};

// ── 日期解析：支持多种格式 ──
function parseDate(raw) {
  // 移除后缀
  let s = raw.replace(/[晌上中下]午/g, '').replace(/[时分秒]/g, '').trim();
  // "2022年10月31日" → "2022-10-31"
  s = s.replace(/(\d{4})年(\d{1,2})月(\d{1,2})日/, (_, y, m, d) =>
    `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`);
  // "2024.5.9" → "2024-05-09"
  s = s.replace(/(\d{4})\.(\d{1,2})\.(\d{1,2})/, (_, y, m, d) =>
    `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`);
  const d = new Date(s);
  return isNaN(d.getTime()) ? new Date(0) : d;
}

// ── 提取图像文件名 ──
function resolveImage(type, imagePath) {
  if (!imagePath) return '';
  const base = type === 'poem' ? DATA_PATHS.poemImg : DATA_PATHS.essayImg;
  const name = imagePath.replace(/^images[\\/]?/, '');
  return base + name;
}

// ── 格式化日期显示 ──
function fmtDate(raw) {
  return raw.replace('晌午', '').replace('上午', '').replace('下午', '').replace('中午', '');
}

// ── 截取摘要 ──
function snippet(text, len = 100) {
  const s = text.replace(/\n/g, ' ').trim();
  return s.length > len ? s.slice(0, len) + '…' : s;
}

// ── 渲染卡片列表到容器 ──
function renderCards(items, targetId, showImage = true) {
  const el = document.getElementById(targetId);
  if (!el) return;

  if (!items.length) {
    el.innerHTML = '<div class="empty"><div class="icon">📭</div><p>暂无内容</p></div>';
    return;
  }

  el.innerHTML = items.map(item => {
    const badgeCls = item.type === 'poem' ? 'poem' : 'essay';
    const badgeTxt = item.type === 'poem' ? '诗' : '文';
    const imgUrl = resolveImage(item.type, item.image);
    const contentHtml = item.content.replace(/\n/g, '<br>');

    return `
    <article class="card">
      ${showImage && imgUrl ? `<img class="card-img" src="${imgUrl}" alt="${item.title}" loading="lazy" onerror="this.style.display='none'">` : ''}
      <div class="card-body">
        <div class="card-meta">
          <span class="card-badge ${badgeCls}">${badgeTxt}</span>
          <span class="card-date">${fmtDate(item.date)}</span>
        </div>
        <h2 class="card-title">${item.title}</h2>
        <p class="card-snippet">${contentHtml}</p>
      </div>
    </article>`;
  }).join('');
}

// ── 加载所有数据并渲染博客主页 ──
async function loadBlog(targetId, limit = 0) {
  const el = document.getElementById(targetId);
  if (!el) return;
  el.innerHTML = '<p style="text-align:center;color:#9ca3af;padding:40px;">载入中…</p>';

  try {
    const [poemsResp, essaysResp] = await Promise.all([
      fetch(DATA_PATHS.poem),
      fetch(DATA_PATHS.essay),
    ]);
    const poems = await poemsResp.json();
    const essays = await essaysResp.json();

    // 合并并标记类型
    const all = [
      ...poems.map(p => ({ ...p, type: 'poem' })),
      ...essays.map(e => ({ ...e, type: 'essay' })),
    ];

    // 按日期倒序
    all.sort((a, b) => parseDate(b.date) - parseDate(a.date));

    const list = limit > 0 ? all.slice(0, limit) : all;
    renderCards(list, targetId, true);
  } catch (e) {
    el.innerHTML = '<div class="empty"><div class="icon">⚠️</div><p>加载失败，请刷新重试</p></div>';
    console.error('blog-loader:', e);
  }
}

// ── 加载单类型列表 ──
async function loadSection(type, targetId) {
  const el = document.getElementById(targetId);
  if (!el) return;
  el.innerHTML = '<p style="text-align:center;color:#9ca3af;padding:40px;">载入中…</p>';

  const path = type === 'poem' ? DATA_PATHS.poem : DATA_PATHS.essay;

  try {
    const resp = await fetch(path);
    const data = await resp.json();
    const items = data.map(d => ({ ...d, type }));

    // 按日期倒序
    items.sort((a, b) => parseDate(b.date) - parseDate(a.date));

    // 渲染时显示大图
    renderCards(items, targetId, true);
  } catch (e) {
    el.innerHTML = '<div class="empty"><div class="icon">⚠️</div><p>加载失败，请刷新重试</p></div>';
    console.error('blog-loader section:', e);
  }
}
