// Footer year, mobile menu toggle, and the HWMR message tiles.
(function () {
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  initMessageTiles();

  var toggle = document.querySelector('.nav-toggle');
  if (!toggle) return;

  toggle.addEventListener('click', function () {
    toggle.setAttribute('aria-expanded', String(toggle.getAttribute('aria-expanded') !== 'true'));
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }
  });

  // Message tiles: one message panel open at a time. The URL hash (#msg-3)
  // lets a message be linked to directly.
  function initMessageTiles() {
    var tiles = document.querySelectorAll('.msg-tile[aria-controls]');
    if (!tiles.length) return;

    function show(id) {
      tiles.forEach(function (tile) {
        var on = tile.getAttribute('aria-controls') === id;
        tile.setAttribute('aria-expanded', String(on));
        document.getElementById(tile.getAttribute('aria-controls')).classList.toggle('is-open', on);
      });
    }

    function setHash(hash) {
      try { history.replaceState(null, '', location.pathname + location.search + hash); } catch (e) {}
    }

    tiles.forEach(function (tile) {
      tile.addEventListener('click', function () {
        var id = tile.getAttribute('aria-controls');
        if (tile.getAttribute('aria-expanded') === 'true') {
          show(null);
          setHash('');
          return;
        }
        show(id);
        setHash('#' + id);
        var calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
        document.getElementById(id).scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'start' });
      });
    });

    function fromHash() {
      var id = location.hash.slice(1);
      var panel = id && document.getElementById(id);
      if (!panel || !panel.classList.contains('msg-panel')) return;
      var group = panel.closest('details');
      if (group) group.open = true;
      show(id);
      panel.scrollIntoView();
    }

    fromHash();
    window.addEventListener('hashchange', fromHash);
  }
})();
