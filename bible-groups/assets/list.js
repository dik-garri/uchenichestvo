async function initList(testament) {
  const root = document.getElementById('topicList');
  const search = document.getElementById('search');
  const res = await fetch('topics.json', { cache: 'no-store' });
  const topics = (await res.json()).filter(t => t.testament === testament);

  function escapeHtml(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}

  function iconsFor(media) {
    const out = [];
    if (media && media.audio && media.audio.length) out.push('<i class="fa-solid fa-headphones" title="Аудио"></i>');
    if (media && media.image && media.image.length) out.push('<i class="fa-solid fa-image" title="Картинки"></i>');
    return out.join('');
  }

  function render(filter) {
    const q = (filter || '').trim().toLowerCase();
    root.innerHTML = '';
    let currentSection = null;
    let sectionUl = null;
    for (const t of topics) {
      const matches = !q
        || String(t.number).includes(q)
        || t.title.toLowerCase().includes(q)
        || t.reference.toLowerCase().includes(q);
      if (!matches) continue;
      if (t.section !== currentSection) {
        currentSection = t.section;
        const h = document.createElement('div');
        h.className = 'section-title';
        h.textContent = t.section;
        root.appendChild(h);
        sectionUl = document.createElement('ul');
        sectionUl.className = 'topics';
        root.appendChild(sectionUl);
      }
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `topic.html?id=${t.id}`;
      a.innerHTML = `
        <span class="topic-num">${t.number}</span>
        <span class="topic-title">${escapeHtml(t.title)}</span>
        <span class="topic-ref">${escapeHtml(t.reference)}</span>
        <span class="topic-icons">${iconsFor(t.media)}</span>
      `;
      li.appendChild(a);
      sectionUl.appendChild(li);
    }
    if (!root.children.length) {
      root.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px 0;">Ничего не найдено</p>';
    }
  }

  render('');
  search.addEventListener('input', e => render(e.target.value));
}
