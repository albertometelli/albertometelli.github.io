/* Static website interaction. Publication HTML is generated from canonical BibTeX at build time. */
(() => {
  'use strict';
  const root = document.documentElement;
  const liveStatus = document.getElementById('site-status');
  const announce = message => {
    if (!liveStatus) return;
    liveStatus.textContent = '';
    requestAnimationFrame(() => { liveStatus.textContent = message; });
  };
  const toggle = document.querySelector('.theme-toggle');
  if (toggle) {
    const isDark = () => root.dataset.theme === 'dark' || (!root.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
    const updateThemeControl = () => {
      const dark = isDark();
      toggle.setAttribute('aria-pressed', String(dark));
      toggle.setAttribute('aria-label', dark ? 'Use light theme' : 'Use dark theme');
      toggle.title = dark ? 'Use light theme' : 'Use dark theme';
    };
    updateThemeControl();
    toggle.addEventListener('click', () => {
      root.dataset.theme = isDark() ? 'light' : 'dark';
      try { localStorage.setItem('am-theme', root.dataset.theme); } catch (_) {}
      updateThemeControl();
      announce(`${root.dataset.theme[0].toUpperCase()}${root.dataset.theme.slice(1)} theme enabled.`);
    });
  }
  const menu = document.querySelector('.nav-toggle');
  const nav = document.getElementById('primary-nav');
  if (menu && nav) {
    const closeMenu = (restoreFocus = false) => {
      if (menu.getAttribute('aria-expanded') !== 'true') return;
      nav.classList.remove('open');
      menu.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-label', 'Open navigation');
      if (restoreFocus) menu.focus();
    };
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') === 'true';
      menu.setAttribute('aria-expanded', String(!open));
      menu.setAttribute('aria-label', open ? 'Open navigation' : 'Close navigation');
      nav.classList.toggle('open', !open);
    });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => closeMenu()));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') closeMenu(true);
    });
    document.addEventListener('click', event => {
      if (!nav.contains(event.target) && !menu.contains(event.target)) closeMenu();
    });
  }
  const copy = document.querySelector('.copy-email');
  if (copy) copy.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(copy.dataset.email);
      const prior = copy.textContent; copy.textContent = 'Copied ✓';
      announce('Email address copied to the clipboard.');
      setTimeout(() => { copy.textContent = prior; }, 2300);
    } catch {
      announce('Copy unavailable. Opening your email application.');
      window.location.href = `mailto:${copy.dataset.email}`;
    }
  });
  const yr = document.getElementById('copyright-year');
  if (yr) yr.textContent = String(new Date().getFullYear());

  const mapFrame = document.querySelector('.map-frame');
  const mapLoad = document.querySelector('.map-load');
  if (mapFrame && mapLoad) mapLoad.addEventListener('click', () => {
    const frame = mapFrame.querySelector('iframe[data-src]');
    if (!frame || mapLoad.disabled) return;
    mapLoad.disabled = true;
    mapLoad.textContent = 'Loading map…';
    mapFrame.classList.remove('has-error');
    announce('Loading the interactive map.');
    const finish = () => {
      clearTimeout(timeout);
      mapFrame.classList.add('is-loaded');
      mapLoad.textContent = 'Map loaded';
      announce('Interactive map loaded.');
    };
    const fail = () => {
      clearTimeout(timeout);
      frame.removeEventListener('load', finish);
      frame.removeEventListener('error', fail);
      frame.removeAttribute('src');
      mapFrame.classList.add('has-error');
      mapLoad.disabled = false;
      mapLoad.textContent = 'Try loading map again';
      announce('The map could not be loaded. You can try again or open Google Maps.');
    };
    const timeout = setTimeout(fail, 10000);
    frame.addEventListener('load', finish, { once: true });
    frame.addEventListener('error', fail, { once: true });
    frame.src = frame.dataset.src;
  });

  const pageList = document.getElementById('publications-list');
  if (!pageList) return;
  const normalize = s => String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const year=document.getElementById('pub-year');
  const search=document.getElementById('pub-search');
  const empty=document.getElementById('pub-empty');
  const tabs=[...document.querySelectorAll('.pub-tab')];
  const groups=[...pageList.querySelectorAll('.pub-group')];
  const items=[...pageList.querySelectorAll('.pub-item')];
  const params=new URLSearchParams(location.search);
  const validTypes=new Set(['all',...tabs.map(tab=>tab.dataset.filter)]);
  let type=validTypes.has(params.get('type'))?params.get('type'):'all';
  search.value=params.get('q')||'';
  if([...year.options].some(option=>option.value===params.get('year')))year.value=params.get('year');

  const syncUrl=()=>{
    const next=new URLSearchParams();
    if(search.value.trim())next.set('q',search.value.trim());
    if(type!=='all')next.set('type',type);
    if(year.value!=='all')next.set('year',year.value);
    const query=next.toString();
    history.replaceState(null,'',`${location.pathname}${query?`?${query}`:''}${location.hash}`);
  };
  const update=()=>{
    const q=normalize(search.value.trim());
    let visible=0;
    items.forEach(item=>{
      const show=(type==='all'||item.dataset.category===type) &&
        (year.value==='all'||item.dataset.year===year.value) &&
        (!q||normalize(item.dataset.search).includes(q));
      item.hidden=!show;
      if(show)visible+=1;
    });
    groups.forEach(group=>{
      const shown=[...group.querySelectorAll('.pub-item:not([hidden])')];
      group.hidden=!shown.length;
      const groupCount=group.querySelector('.pub-group-heading b');
      if(groupCount)groupCount.textContent=shown.length;
      group.querySelectorAll('[data-year-divider]').forEach(divider=>{
        divider.hidden=!shown.some(item=>item.dataset.year===divider.dataset.yearDivider);
      });
    });
    empty.hidden=visible!==0;
    tabs.forEach(button=>{const active=button.dataset.filter===type;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));});
    syncUrl();
  };
  search.addEventListener('input',update);
  year.addEventListener('change',update);
  tabs.forEach(tab=>tab.addEventListener('click',()=>{type=tab.dataset.filter;update();}));
  document.querySelectorAll('.citation-copy').forEach(button=>button.addEventListener('click',async()=>{
    const prior=button.textContent;
    try{await navigator.clipboard.writeText(button.dataset.citation);button.textContent='Citation copied ✓';announce('Citation copied to the clipboard.');}
    catch{button.textContent='Copy unavailable';announce('The citation could not be copied.');}
    setTimeout(()=>{button.textContent=prior;},2200);
  }));
  update();
})();
