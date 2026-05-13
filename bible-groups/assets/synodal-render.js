// bible-groups/assets/synodal-render.js
// Renders one or more Bible passages from data/synodal.json (cached after first load).

let _synodalCache = null;

async function loadSynodal() {
  if (_synodalCache) return _synodalCache;
  const res = await fetch('../data/synodal.json');
  if (!res.ok) throw new Error('Failed to load synodal.json');
  _synodalCache = await res.json();
  return _synodalCache;
}

function findBook(synodal, abbrev) {
  return synodal.find(b => b.abbrev === abbrev);
}

function bookTitleRu(abbrev) {
  const M = {
    gn:'Бытие', ex:'Исход', lv:'Левит', nm:'Числа', dt:'Второзаконие',
    js:'Иисус Навин', jud:'Книга Судей', rt:'Руфь',
    '1sm':'1 Царств','2sm':'2 Царств','1kg':'3 Царств','2kg':'4 Царств',
    '1ch':'1 Паралипоменон','2ch':'2 Паралипоменон',
    ezr:'Ездра', ne:'Неемия', et:'Есфирь', jb:'Иов', ps:'Псалтирь',
    prv:'Притчи', ec:'Екклесиаст', so:'Песнь Песней',
    is:'Исаия', jr:'Иеремия', lm:'Плач Иеремии', ezk:'Иезекииль',
    dn:'Даниил', ho:'Осия', jl:'Иоиль', am:'Амос', ob:'Авдий',
    jn:'Иона', mi:'Михей', na:'Наум', hk:'Аввакум', zp:'Софония',
    hg:'Аггей', zc:'Захария', ml:'Малахия',
    mt:'Матфея', mk:'Марка', lk:'Луки', jo:'Иоанна', act:'Деяния',
    rm:'Римлянам','1co':'1 Коринфянам','2co':'2 Коринфянам',
    gl:'Галатам', eph:'Ефесянам', ph:'Филиппийцам', cl:'Колоссянам',
    '1ts':'1 Фессалоникийцам','2ts':'2 Фессалоникийцам',
    '1tm':'1 Тимофею','2tm':'2 Тимофею', tt:'Титу', phm:'Филимону',
    hb:'Евреям', jm:'Иакова','1pe':'1 Петра','2pe':'2 Петра',
    '1jo':'1 Иоанна','2jo':'2 Иоанна','3jo':'3 Иоанна', jd:'Иуды',
    rev:'Откровение'
  };
  return M[abbrev] || abbrev;
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderPassage(synodal, p) {
  const book = findBook(synodal, p.book);
  if (!book) return `<p class="error">Книга «${p.book}» не найдена.</p>`;
  const [ch1, v1Raw] = p.from;
  const [ch2, v2Raw] = p.to;
  let html = '';
  for (let ch = ch1; ch <= ch2; ch++) {
    const chapter = book.chapters[ch - 1];
    if (!chapter) continue;
    const vStart = (ch === ch1) ? Math.max(1, v1Raw) : 1;
    const vEnd = (ch === ch2) ? (v2Raw === -1 ? chapter.length : Math.min(v2Raw, chapter.length)) : chapter.length;
    html += `<div class="chapter-heading">${bookTitleRu(p.book)} ${ch}</div>`;
    html += '<p>';
    for (let v = vStart; v <= vEnd; v++) {
      const verse = chapter[v - 1];
      if (!verse) continue;
      html += `<span class="verse-num">${v}</span>${escapeHtml(verse)} `;
    }
    html += '</p>';
  }
  return html;
}

window.renderSynodal = async function renderSynodal(target, refStructured) {
  if (!refStructured || !refStructured.passages) {
    target.innerHTML = '<p class="error">Ссылка отсутствует.</p>';
    return;
  }
  try {
    const synodal = await loadSynodal();
    target.classList.add('passage');
    target.innerHTML = refStructured.passages.map(p => renderPassage(synodal, p)).join('');
  } catch (e) {
    target.innerHTML = `<p class="error">Не удалось загрузить текст: ${e.message}</p>`;
  }
};
