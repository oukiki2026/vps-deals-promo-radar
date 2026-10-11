/* Local copy controls and session-only exercise checks; no network or storage. */
(() => {
  'use strict';
  const status = document.createElement('p');
  status.className = 'copy-status';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  document.querySelector('main')?.append(status);
  document.querySelectorAll('.prose blockquote, .prose pre').forEach((sample) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-button';
    button.textContent = sample.dataset.copyLabel || (sample.tagName === 'PRE' ? 'Copy example' : 'Copy notes');
    button.addEventListener('click', async () => {
      const text = sample.innerText.trim();
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(text);
        status.textContent = 'Copied. Paste it into your own document or AI tool.';
        button.textContent = 'Copied';
      } catch (_) {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(sample);
        selection?.removeAllRanges();
        selection?.addRange(range);
        status.textContent = 'Copy access is unavailable. The sample is selected; use your usual copy command.';
      }
    });
    sample.before(button);
  });
  document.querySelectorAll('[data-practice-checklist]').forEach((list) => {
    const note = document.createElement('p');
    note.className = 'practice-progress';
    note.setAttribute('role', 'status');
    const boxes = list.querySelectorAll('input[type="checkbox"]');
    const update = () => {
      const count = [...boxes].filter((box) => box.checked).length;
      note.textContent = `${count} of ${boxes.length} checks marked. Your marks reset when this page reloads.`;
    };
    boxes.forEach((box) => box.addEventListener('change', update));
    list.after(note);
    update();
  });
})();
