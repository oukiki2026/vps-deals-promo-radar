const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(require('node:path').join(__dirname, '../assets/analytics.js'), 'utf8');
function setup(savedChoice) {
  const nodes = [], handlers = {};
  function element(tag) {
    const node = {tag, dataset: {}, textContent: '', hidden: false, children: [], handlers: {},
      setAttribute() {}, append(...items) {this.children.push(...items);},
      prepend(...items) {this.children.unshift(...items);},
      appendChild(item) {this.children.push(item);},
      addEventListener(name, fn) {this.handlers[name] = fn;}, focus() {}, scrollIntoView() {}};
    nodes.push(node); return node;
  }
  const footer = element('footer'), links = element('nav'), head = element('head');
  const document = {currentScript: {dataset: {measurementId: 'G-TEST123'}}, cookie: '', head,
    referrer: 'https://example.org/private?secret=never-send', createElement: element,
    querySelector(selector) {return selector === 'footer' ? footer : links;},
    addEventListener(name, fn) {handlers[name] = fn;}};
  const window = {};
  const location = {origin: 'https://kikomono.com', pathname: '/ai-tools/', search: '?secret=hidden', hash: '#private',
    hostname: 'kikomono.com', reload() {}};
  const localStorage = {getItem() {return savedChoice ? JSON.stringify({choice:savedChoice,time:Date.now()}) : null;}, setItem() {}};
  vm.runInNewContext(source, {document, window, location, localStorage, Date, URL});
  function trigger({placement='lumo-affiliate', trusted=true, sponsored=true, type='click', button=0}={}) {
    const section = {id: placement};
    const link = {closest() {return section;}};
    handlers[type]({type, button, isTrusted: trusted, target: {closest() {return sponsored ? link : null;}}});
  }
  function events() {return (window.dataLayer || []).filter(args => args[0] === 'event');}
  return {nodes, window, head, trigger, events};
}
const fresh = setup();
fresh.trigger(); assert.equal(fresh.events().length, 0); assert.equal(fresh.head.children.length, 0);
fresh.nodes.find(n => n.textContent === 'Allow analytics').handlers.click();
fresh.trigger(); assert.equal(fresh.events().length, 1);
const payload = JSON.stringify(fresh.events()[0][2]);
assert.equal(fresh.events()[0][1], 'affiliate_click');
assert.ok(payload.includes('proton_lumo')); assert.ok(!payload.includes('secret')); assert.ok(!payload.includes('https://'));
fresh.trigger({trusted:false}); fresh.trigger({sponsored:false}); fresh.trigger({placement:'unknown'});
fresh.trigger({type:'auxclick',button:2}); assert.equal(fresh.events().length, 1);
fresh.trigger({type:'auxclick',button:1}); assert.equal(fresh.events().length, 2);
fresh.nodes.find(n => n.textContent === 'Decline analytics').handlers.click();
fresh.trigger(); assert.equal(fresh.events().length, 2);
const declined = setup('denied'); declined.trigger(); assert.equal(declined.events().length, 0);
const granted = setup('granted'); granted.trigger({placement:'ww-affiliate-pdf'});
assert.equal(granted.events().length, 1); assert.equal(granted.events()[0][2].merchant, 'wondershare');
console.log('Consent, withdrawal, safe parameters, existing placements and trusted clicks passed; no network requests made.');
