document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('article-list');
  if (!container) return;

  fetch('散文.json')
    .then(r => {
      if (!r.ok) throw new Error('加载失败');
      return r.json();
    })
    .then(data => {
      container.innerHTML = '';
      data.forEach(article => {
        const card = document.createElement('div');
        card.className = 'poem-card';
        const imageHtml = article.image ? `<img src="${article.image}" class="poem-image" alt="${article.title}">` : '';
        card.innerHTML = `
          <div class="poem-title">${article.title}</div>
          <div class="poem-meta">${article.date}</div>
          <p>${article.content.replace(/\n/g, '<br>')}</p>
          ${imageHtml}
        `;
        container.appendChild(card);
      });
    })
    .catch(err => {
      container.innerHTML = `<p style="color:#9ca3af;">暂无内容</p>`;
    });
});