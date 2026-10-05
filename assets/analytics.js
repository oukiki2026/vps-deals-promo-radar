/* Optional GA4: no Google tag or request until affirmative analytics consent. */
(() => {
  'use strict';
  const id = document.currentScript.dataset.measurementId;
  if (!/^G-[A-Z0-9]+$/.test(id)) return;
  const key = 'kikomono-analytics-v1';
  const lifetime = 180 * 24 * 60 * 60 * 1000;
  let started = false;
  let choice = '';
  try {
    const saved = JSON.parse(localStorage.getItem(key) || 'null');
    if (saved && Date.now() - saved.time < lifetime) choice = saved.choice;
  } catch (_) {}
  function clearCookies() {
    document.cookie.split(';').forEach(pair => {
      const name = pair.trim().split('=')[0];
      if (!/^_ga(?:_|$)/.test(name)) return;
      ['', '; domain=' + location.hostname, '; domain=.' + location.hostname].forEach(domain => {
        document.cookie = name + '=; Max-Age=0; path=/' + domain + '; SameSite=Lax; Secure';
      });
    });
  }
  function start() {
    if (started) return;
    started = true;
    window['ga-disable-' + id] = false;
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('consent', 'default', {analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied'});
    gtag('js', new Date());
    let referral = '';
    try { referral = document.referrer ? new URL(document.referrer).origin + '/' : ''; } catch (_) {}
    gtag('config', id, {
      page_location: location.origin + location.pathname,
      page_referrer: referral,
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(tag);
  }
  const panel = document.createElement('section');
  panel.className = 'section analytics-preferences';
  panel.setAttribute('aria-label', 'Analytics preferences');
  const heading = document.createElement('h2');
  heading.textContent = 'Optional analytics';
  const text = document.createElement('p');
  text.textContent = 'Allow Google Analytics cookies to help us improve these guides? Your choice does not affect access. Cloudflare aggregate statistics remain separate.';
  const status = document.createElement('p');
  status.setAttribute('role', 'status');
  const actions = document.createElement('div');
  const allow = document.createElement('button');
  allow.type = 'button'; allow.className = 'button'; allow.textContent = 'Allow analytics';
  const decline = document.createElement('button');
  decline.type = 'button'; decline.className = 'button'; decline.textContent = 'Decline analytics';
  const close = document.createElement('button');
  close.type = 'button'; close.textContent = 'Close preferences';
  const policy = document.createElement('a');
  policy.href = '/privacy/#google-analytics'; policy.textContent = 'Privacy details';
  function save(value) {
    choice = value;
    try { localStorage.setItem(key, JSON.stringify({choice: value, time: Date.now()})); } catch (_) {}
    if (value === 'granted') start();
    else {
      window['ga-disable-' + id] = true;
      if (window.gtag) window.gtag('consent', 'update', {analytics_storage: 'denied'});
      clearCookies();
    }
    status.textContent = value === 'granted' ? 'Analytics allowed.' : 'Analytics declined.';
    panel.hidden = true;
    if (value === 'denied' && started) location.reload();
  }
  allow.addEventListener('click', () => save('granted'));
  decline.addEventListener('click', () => save('denied'));
  close.addEventListener('click', () => {panel.hidden = true;});
  actions.append(allow, decline, close);
  panel.append(heading, text, status, actions, policy);
  document.querySelector('footer').prepend(panel);
  const toggle = document.createElement('button');
  toggle.type = 'button'; toggle.textContent = 'Analytics preferences';
  toggle.addEventListener('click', () => {
    panel.hidden = false;
    status.textContent = choice === 'granted' ? 'Current choice: allowed.' : choice === 'denied' ? 'Current choice: declined.' : 'No choice saved.';
    panel.scrollIntoView({block: 'center'});
    allow.focus();
  });
  document.querySelector('.footer-links').append(toggle);
  if (choice === 'granted') {panel.hidden = true; start();}
  else if (choice === 'denied') {panel.hidden = true; clearCookies();}
})();
