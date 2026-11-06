'use strict';

const guide = window.FIELD_GUIDE;
const ui = guide.ui;
function format(template, values) {
  return template.replace(/\{(\w+)\}/g, (_, key) => String(values[key]));
}
const panel = document.querySelector('#recipe-panel');
const recipeButtons = [...document.querySelectorAll('[data-recipe]')];

function showRecipe(id) {
  const recipe = guide.recipes.find(item => item.id === id);
  recipeButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.recipe === id)));
  panel.querySelector('h3').textContent = recipe.title;
  const columns = panel.querySelectorAll('.recipe-columns p');
  [recipe.context, recipe.verify, recipe.trim].forEach((text, index) => columns[index].textContent = text);
  const badge = panel.querySelector('.recipe-badge');
  badge.replaceChildren();
  const label = document.createElement('b');
  label.textContent = ui.artifact_label;
  badge.append(label, ' · ' + recipe.artifact);
}
recipeButtons.forEach(button => button.addEventListener('click', () => showRecipe(button.dataset.recipe)));

const cards = [...document.querySelectorAll('.source-card')];
const search = document.querySelector('#source-search');
const platform = document.querySelector('#source-platform');
const recency = document.querySelector('#source-recency');
const topic = document.querySelector('#source-topic');
const results = document.querySelector('#source-results');
const more = document.querySelector('#load-more');
const editionDay = Date.parse(guide.edition + 'T00:00:00Z');
let limit = 12;

function filterSources() {
  const query = search.value.trim().toLocaleLowerCase();
  const matched = cards.filter(card => {
    if (query && !card.dataset.search.toLocaleLowerCase().includes(query)) return false;
    if (platform.value !== 'all' && card.dataset.platform !== platform.value) return false;
    if (topic.value !== 'all' && card.dataset.topic !== topic.value) return false;
    if (recency.value === 'unknown') return !card.dataset.published;
    if (recency.value !== 'all') {
      if (!card.dataset.date) return false;
      const age = (editionDay - Date.parse(card.dataset.date + 'T00:00:00Z')) / 86400000;
      return age >= 0 && age < Number(recency.value);
    }
    return true;
  });
  const shown = new Set(matched.slice(0, limit));
  cards.forEach(card => card.hidden = !shown.has(card));
  results.textContent = format(ui.results, {matched: matched.length, shown: shown.size, edition: guide.edition});
  more.hidden = matched.length <= limit;
  more.textContent = format(ui.load_more, {count: Math.min(12, Math.max(0, matched.length - limit))});
}
[search, platform, recency, topic].forEach(control => control.addEventListener('input', () => {
  limit = 12;
  filterSources();
}));
more.addEventListener('click', () => { limit += 12; filterSources(); });
filterSources();

const toast = document.querySelector('#toast');
let toastTimer;
function showToast(message) {
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, 3000);
}
document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
  const text = document.getElementById(button.dataset.copy).textContent;
  try {
    await navigator.clipboard.writeText(text);
    showToast(ui.copied);
  } catch {
    showToast(ui.copy_failed);
  }
}));
