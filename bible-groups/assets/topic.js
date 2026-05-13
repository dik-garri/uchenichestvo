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
  async function ensureQuestions() { /* Task 9 */ }
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
