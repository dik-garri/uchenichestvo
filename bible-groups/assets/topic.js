(async function () {
  const params = new URLSearchParams(location.search);
  const id = params.get('id');
  const titleEl = document.getElementById('topicTitle');
  if (!id) { titleEl.textContent = 'Тема не указана'; return; }

  const topics = await fetch('topics.json', { cache: 'no-store' }).then(r => r.json());
  const topic = topics.find(t => t.id === id);
  if (!topic) { titleEl.textContent = 'Тема не найдена'; return; }

  document.title = `${topic.number}. ${topic.title} – Изучение Библии`;
  titleEl.textContent = `${topic.number}. ${topic.title}`;
  document.getElementById('topicRef').textContent = topic.reference;
  document.getElementById('backLink').href = topic.testament === 'ot' ? 'ot.html' : 'nt.html';

  let textRendered = false;
  async function ensureText() {
    if (textRendered) return;
    await renderSynodal(document.getElementById('panel-text'), topic.refStructured);
    textRendered = true;
  }

  // Stubs for later tasks
  let questionsLoaded = false;
  async function ensureQuestions() {
    if (questionsLoaded) return;
    questionsLoaded = true;
    const dir = topic.testament; // 'ot' or 'nt'
    const mineUrl = `${dir}/${topic.slug}-mine.md`;
    const hagenUrl = `${dir}/${topic.slug}-hagen.md`;

    const [mineRes, hagenRes] = await Promise.all([
      fetch(mineUrl),
      fetch(hagenUrl),
    ]);

    const mineMd = mineRes.ok ? await mineRes.text() : '_Вопросы недоступны._';
    document.getElementById('questionsMine').innerHTML = marked.parse(mineMd);

    if (!hagenRes.ok) {
      // No Hagenhans for this topic — hide sub-tabs, show mine only
      document.getElementById('questionsSubtabs').style.display = 'none';
      document.getElementById('questionsHagen').style.display = 'none';
      document.getElementById('questionsMine').style.display = '';
      return;
    }

    const hagenMd = await hagenRes.text();
    document.getElementById('questionsHagen').innerHTML = marked.parse(hagenMd);

    const subtabs = document.querySelectorAll('.subtab-btn');
    function activateSub(name) {
      subtabs.forEach(b => b.classList.toggle('active', b.dataset.subtab === name));
      document.getElementById('questionsMine').style.display = name === 'mine' ? '' : 'none';
      document.getElementById('questionsHagen').style.display = name === 'hagen' ? '' : 'none';
      localStorage.setItem('bibleGroupsQuestionsTab', name);
    }
    subtabs.forEach(b => b.addEventListener('click', () => activateSub(b.dataset.subtab)));
    activateSub(localStorage.getItem('bibleGroupsQuestionsTab') || 'mine');
  }
  let prepLoaded = false;
  function ensurePrep() {
    if (prepLoaded) return;
    prepLoaded = true;
    const target = document.getElementById('panel-prep');
    const media = topic.media || {};
    const audio = media.audio || [];
    const image = media.image || [];
    if (!audio.length && !image.length) {
      target.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px 0;">Подготовительные материалы пока не добавлены.</p>';
      return;
    }
    function esc(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
    const base = `media/${encodeURIComponent(topic.slug)}/`;
    const parts = [];
    function stripExt(s) { return s.replace(/\.[^.]+$/, ''); }
    if (audio.length) {
      parts.push('<div class="media-block"><h3><i class="fa-solid fa-headphones"></i> Аудио</h3>');
      for (const name of audio) {
        parts.push(`<div class="media-item"><div style="font-size:14px;color:var(--text-secondary);margin-bottom:6px;font-weight:600;">${esc(stripExt(name))}</div>`);
        parts.push(`<audio class="media-audio" controls preload="none" src="${base}${encodeURIComponent(name)}"></audio></div>`);
      }
      parts.push('</div>');
    }
    if (image.length) {
      parts.push('<div class="media-block"><h3><i class="fa-solid fa-image"></i> Картинки</h3>');
      for (const name of image) {
        parts.push(`<img class="media-image" loading="lazy" src="${base}${encodeURIComponent(name)}" alt="${esc(name)}">`);
      }
      parts.push('</div>');
    }
    target.innerHTML = parts.join('');

    const lb = document.getElementById('lightbox');
    const lbImg = document.getElementById('lightboxImg');
    target.querySelectorAll('.media-image').forEach(img => {
      img.addEventListener('click', () => { lbImg.src = img.src; lb.classList.add('open'); });
    });
    lb.addEventListener('click', () => lb.classList.remove('open'));
  }

  const panels = { text: 'panel-text', questions: 'panel-questions', prep: 'panel-prep' };
  const mainTabs = document.querySelectorAll('.tab-btn');
  function activateTab(name) {
    mainTabs.forEach(b => b.classList.toggle('active', b.dataset.tab === name));
    for (const [k, pid] of Object.entries(panels)) {
      document.getElementById(pid).classList.toggle('active', k === name);
    }
    localStorage.setItem('bibleGroupsMainTab', name);
    if (name === 'text') ensureText();
    if (name === 'questions') ensureQuestions();
    if (name === 'prep') ensurePrep();
  }
  mainTabs.forEach(b => b.addEventListener('click', () => activateTab(b.dataset.tab)));

  const initial = localStorage.getItem('bibleGroupsMainTab') || 'text';
  activateTab(initial);

  // Expose for Tasks 9 and 10 to extend without re-fetching
  window._topic = topic;
})();
