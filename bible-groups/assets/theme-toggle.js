(function () {
  const toggle = document.getElementById('themeToggle');
  if (!toggle) return;
  const icon = toggle.querySelector('i');
  const saved = localStorage.getItem('theme');

  if (saved !== 'dark') {
    document.documentElement.classList.add('light');
    icon.classList.replace('fa-sun', 'fa-moon');
  }

  toggle.addEventListener('click', () => {
    const isLight = document.documentElement.classList.toggle('light');
    icon.classList.replace(isLight ? 'fa-sun' : 'fa-moon', isLight ? 'fa-moon' : 'fa-sun');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
  });
})();
