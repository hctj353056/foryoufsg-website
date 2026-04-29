document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('poem-list');
  if (!container) return;

  fetch('诗词.json')
    .then(r => {
      if (!r.ok) throw new Error('加载失败');
      return r.json();
    })
    .then(data => {
      container.innerHTML = '';
      data.forEach(poem => {
        const card = document.createElement('div');
        card.className = 'poem-card';
        card.innerHTML = `
          <div class="poem-title">${poem.title}</div>
          <div class="poem-meta">${poem.date}</div>
          <p>${poem.content.replace(/\n/g, '<br>')}</p>
        `;
        container.appendChild(card);
      });
    })
    .catch(err => {
      container.innerHTML = `<p style="color:#9ca3af;">暂无内容</p>`;
    });
});