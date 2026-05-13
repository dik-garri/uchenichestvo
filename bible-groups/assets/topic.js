(async function () {
  const params = new URLSearchParams(location.search);
  const id = params.get('id');
  const titleEl = document.getElementById('topicTitle');
  if (!id) { titleEl.textContent = 'Тема не указана'; return; }

  const topics = await fetch('topics.json').then(r => r.json());
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
  async function ensurePrep() { /* Task 10 */ }

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
