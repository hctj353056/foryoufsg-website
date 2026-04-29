const PAGE_SIZE = 10;
let allData = [];
let currentPage = 0;

document.addEventListener('DOMContentLoaded', () => {
  fetch('诗词.json')
    .then(r => r.json())
    .then(data => {
      allData = data;
      renderPage();
      window.addEventListener('scroll', handleScroll);
    });
});

function renderPage() {
  const container = document.getElementById('poem-list');
  const start = currentPage * PAGE_SIZE;
  const end = start + PAGE_SIZE;
  const pageData = allData.slice(start, end);
  
  pageData.forEach(poem => {
    const card = document.createElement('div');
    card.className = 'poem-card';
    card.innerHTML = `
      <div class="poem-title">${poem.title}</div>
      <div class="poem-meta">${poem.date}</div>
      <p>${poem.content.replace(/\n/g, '<br>')}</p>
    `;
    container.appendChild(card);
  });
  
  currentPage++;
}

function handleScroll() {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
    if (currentPage * PAGE_SIZE < allData.length) {
      renderPage();
    }
  }
}