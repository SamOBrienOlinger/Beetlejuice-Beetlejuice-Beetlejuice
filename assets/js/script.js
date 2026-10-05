/* Progressive enhancements. No framework, no stored names or contact messages. */
(() => {
  'use strict';
  const byId = (id) => document.getElementById(id);
  // Older Safari implements MediaQueryList.addListener, not addEventListener.
  const onMediaChange = (query, listener) => {
    if (typeof query.addEventListener === 'function') query.addEventListener('change', listener);
    else if (typeof query.addListener === 'function') query.addListener(listener);
  };
  const readPreference = (key) => {
    try { return localStorage.getItem(key); } catch { return null; }
  };
  const savePreference = (key, value) => {
    try { localStorage.setItem(key, value); } catch { /* Private browsing may deny storage. */ }
  };
  if (byId('copyrightYear')) byId('copyrightYear').textContent = new Date().getFullYear();

  // One lightweight navigation controller, including Escape and resize recovery.
  const menuButton = document.querySelector('.navbar-toggler');
  const menu = byId('navbarNav');
  if (menu && menuButton) {
    const desktop = window.matchMedia('(min-width: 62em)');
    document.documentElement.classList.add('nav-enhanced');
    menuButton.hidden = false;
    const setMenu = (open, restoreFocus = false) => {
      menu.classList.toggle('is-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      if (restoreFocus) menuButton.focus();
    };
    menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false, true);
    });
    document.addEventListener('click', (event) => {
      if (!event.target.closest('.navbar') && menu.classList.contains('is-open')) setMenu(false);
    });
    menu.addEventListener('click', (event) => {
      if (event.target.closest('a')) setMenu(false);
    });
    onMediaChange(desktop, () => {
      const wasInMenu = menu.contains(document.activeElement);
      const wasOnToggle = document.activeElement === menuButton;
      setMenu(false);
      if (!desktop.matches && wasInMenu) menuButton.focus();
      if (desktop.matches && wasOnToggle) menu.querySelector('a')?.focus();
    });
  }

  // Keep the original GIF; capture a still frame only when motion is paused.
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let motionChoice = readPreference('beetlejuice-motion');
  const motionButton = byId('motion-toggle');
  const welcomeImage = byId('welcome-image');
  const animatedSource = welcomeImage?.getAttribute('src');
  let stillSource = null;
  const motionPaused = () => motionChoice === 'paused' || (motionChoice !== 'running' && reducedMotion.matches);
  const freezeWelcome = () => {
    if (!welcomeImage || !motionPaused()) return;
    if (!stillSource && welcomeImage.complete && welcomeImage.naturalWidth > 0) {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = welcomeImage.naturalWidth;
        canvas.height = welcomeImage.naturalHeight;
        canvas.getContext('2d').drawImage(welcomeImage, 0, 0);
        stillSource = canvas.toDataURL('image/png');
      } catch {
        // This image is already part of the site and is a safe static fallback.
        stillSource = 'assets/images/beetlejuice-standing.png';
      }
    }
    if (stillSource && welcomeImage.getAttribute('src') !== stillSource) welcomeImage.src = stillSource;
  };
  const applyMotion = () => {
    const paused = motionPaused();
    document.body.classList.toggle('motion-paused', paused);
    document.body.classList.toggle('motion-running', !paused);
    if (motionButton) {
      motionButton.hidden = false;
      motionButton.setAttribute('aria-pressed', String(paused));
      motionButton.textContent = paused ? 'Play animations' : 'Pause animations';
    }
    if (paused) freezeWelcome();
    else if (welcomeImage && welcomeImage.getAttribute('src') !== animatedSource) welcomeImage.src = animatedSource;
  };
  welcomeImage?.addEventListener('load', freezeWelcome);
  motionButton?.addEventListener('click', () => {
    motionChoice = motionPaused() ? 'running' : 'paused';
    savePreference('beetlejuice-motion', motionChoice);
    applyMotion();
  });
  onMediaChange(reducedMotion, applyMotion);
  applyMotion();

  // Only initialise the generator on its own page.
  const nameInput = byId('name');
  if (nameInput) {
    const phraseLists = [
      ['shall forever', 'is cursed to', 'will endlessly', 'is fated to', 'shall eternally', 'is doomed to', 'will repeatedly', 'has been chosen to', 'is condemned to', 'will henceforth'],
      ['endure', 'suffer through', 'face', 'confront', 'be haunted by', 'be tormented by', 'be plagued by', 'be surrounded by', 'be trapped with'],
      ["a mountain of Beetlejuice's poop", "buckets of Beetlejuice's spittle", 'a lake of boiling Beetlejuice — whatever that means; use your imagination', 'rotting corpses with far too many teeth', 'a mountain of stale candy corn', 'buckets of sinister sweets', "a lake of witches' brew", 'rotten pumpkins carved in their own likenesses', 'eerie whispers beneath the moonlight', 'spectral footsteps in the dark', 'a relentless barrage of spooktacular puns', 'cauldrons bubbling with enchanted brews', 'ghosts and goblins at the doorstep', 'skeletons dancing to "The Monster Mash"', 'sweets that somebody else has sucked and spat out', 'shrieking Halloween masks', 'swarms of creepy-crawlies', 'tap-dancing spiders', 'invisible sandworms', 'friends and family dancing to "Day-O (The Banana Boat Song)" with unnerving enthusiasm', 'a choir of shrunken heads singing off-key', 'a conga line of zombies in squeaky shoes', 'possessed garden gnomes stealing every left sock', 'a sandworm with a taste for freshly washed laundry', 'ghostly dinner guests who never stop slurping']
    ];
    const commonWords = new Set(['a', 'an', 'and', 'at', 'be', 'been', 'by', 'for', 'has', 'in', 'is', 'of', 'on', 'shall', 'that', 'the', 'their', 'through', 'to', 'will', 'with']);
    const words = (text) => text.split(/\s+/).map((word) => {
      let normalized = word.toLowerCase().replace(/['’]s$/, '').replace(/[^a-z0-9]/g, '');
      if (normalized.endsWith('ly') && normalized.length > 5) normalized = normalized.slice(0, -2);
      return normalized;
    }).filter((word) => word && !commonWords.has(word));
    const buttons = [...document.querySelectorAll('.curse-button')];
    const outputs = ['firstResult', 'secondResult', 'thirdResult'].map(byId);
    const builder = byId('phussy');
    const result = byId('curse-and-beetlejuice');
    const finalButton = byId('finalButton');
    const status = byId('game-status');
    const progress = byId('curse-progress');
    const dialog = byId('loading-panel');
    const soundButton = byId('sound-toggle');
    const sound = new Audio('assets/audio/evil-laugh-1.mp3');
    sound.preload = 'none';
    let soundEnabled = readPreference('beetlejuice-sound') !== 'off';
    let nextPart = 0;
    let phase = 'building';
    let revealTimer = null;
    let copyTimer = null;
    let copyVersion = 0;
    let fullCurse = '';
    const validName = () => nameInput.value.trim().length > 0;
    const stopSound = () => { sound.pause(); sound.currentTime = 0; };
    const playSound = () => {
      if (!soundEnabled) return;
      sound.currentTime = 0;
      const play = sound.play();
      if (play && typeof play.catch === 'function') play.catch(() => {
        // Missing audio or browser restrictions must never stop the game.
        soundEnabled = false;
        updateSound();
      });
    };
    const updateSound = () => {
      soundButton.hidden = false;
      soundButton.textContent = soundEnabled ? 'Sound: on' : 'Sound: off';
      soundButton.setAttribute('aria-pressed', String(soundEnabled));
    };
    soundButton.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      savePreference('beetlejuice-sound', soundEnabled ? 'on' : 'off');
      if (!soundEnabled) stopSound();
      updateSound();
    });
    updateSound();

    const updateControls = () => {
      buttons.forEach((button, index) => {
        button.disabled = phase !== 'building' || !validName() || index !== nextPart;
        button.closest('.curse-step').classList.toggle('is-complete', index < nextPart);
        button.textContent = index < nextPart ? 'Curse set ✓' : 'Curse!';
        button.setAttribute('aria-label', index < nextPart ? `Curse set: ${['first', 'second', 'third'][index]} part` : `Curse! Generate the ${['first', 'second', 'third'][index]} part of your curse`);
      });
      finalButton.disabled = phase !== 'building' || !validName() || nextPart !== 3;
      progress.value = nextPart;
      progress.textContent = `${nextPart} of 3`;
      const statusText = !validName() ? 'Enter a name to begin.' : nextPart === 3 ? '3 of 3 parts ready. Reveal your curse!' : `${nextPart} of 3 parts ready. Press ${['the first', 'the second', 'the third'][nextPart]} Curse! button.`;
      if (status.textContent !== statusText) status.textContent = statusText;
    };
    const showNameError = () => {
      const invalid = !validName();
      byId('name-error').hidden = !invalid;
      if (invalid) nameInput.setAttribute('aria-invalid', 'true');
      else nameInput.removeAttribute('aria-invalid');
    };
    nameInput.addEventListener('input', () => {
      if (nameInput.hasAttribute('aria-invalid')) showNameError();
      updateControls();
    });
    nameInput.addEventListener('blur', () => {
      if (nameInput.value.length > 0) showNameError();
    });
    nameInput.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' || event.isComposing) return;
      event.preventDefault();
      if (!validName()) { showNameError(); return; }
      (buttons[nextPart] || finalButton).focus();
    });
    buttons.forEach((button, index) => button.addEventListener('click', () => {
      if (button.disabled || phase !== 'building' || !validName() || index !== nextPart) return;
      const earlier = new Set(outputs.slice(0, index).flatMap((output) => words(output.textContent)));
      const compatible = phraseLists[index].filter((phrase) => !words(phrase).some((word) => earlier.has(word)));
      // Keep the no-repeated-meaningful-words rule; never fall back to a conflicting phrase.
      if (!compatible.length) {
        status.textContent = 'No matching phrase was found. Please try again.';
        return;
      }
      outputs[index].textContent = compatible[Math.floor(Math.random() * compatible.length)];
      nextPart += 1;
      playSound();
      updateControls();
      (buttons[nextPart] || finalButton).focus();
    }));

    const closeDialog = () => {
      if (dialog.open && typeof dialog.close === 'function') dialog.close();
    };
    const cancelReveal = () => {
      if (phase !== 'loading') return;
      clearTimeout(revealTimer);
      revealTimer = null;
      closeDialog();
      stopSound();
      phase = 'building';
      updateControls();
      finalButton.focus();
    };
    byId('cancel-curse').addEventListener('click', cancelReveal);
    dialog.addEventListener('cancel', (event) => { event.preventDefault(); cancelReveal(); });
    finalButton.addEventListener('click', () => {
      if (finalButton.disabled || phase !== 'building' || !validName() || nextPart !== 3) return;
      phase = 'loading';
      updateControls();
      // textContent prevents names such as <img ...> being interpreted as HTML.
      fullCurse = `${nameInput.value.trim()} ${outputs.map((output) => output.textContent).join(' ')}!`;
      byId('finalResult').textContent = fullCurse;
      const reveal = () => {
        if (phase !== 'loading') return;
        revealTimer = null;
        closeDialog();
        builder.hidden = true;
        result.hidden = false;
        phase = 'result';
        byId('result-title').focus({ preventScroll: true });
        result.scrollIntoView({ block: 'start', behavior: 'auto' });
      };
      // Do not strand the player when a browser lacks native dialog support.
      if (typeof dialog.showModal !== 'function') { reveal(); return; }
      try { dialog.showModal(); } catch { reveal(); return; }
      playSound();
      revealTimer = setTimeout(reveal, motionPaused() ? 150 : 1500);
    });
    byId('refresh').addEventListener('click', () => {
      clearTimeout(revealTimer);
      clearTimeout(copyTimer);
      copyVersion += 1;
      closeDialog();
      stopSound();
      nextPart = 0;
      phase = 'building';
      fullCurse = '';
      outputs.forEach((output) => { output.textContent = ''; });
      byId('finalResult').textContent = '';
      byId('copy-status').textContent = '';
      byId('copy-curse').textContent = 'Copy curse';
      nameInput.value = '';
      nameInput.removeAttribute('aria-invalid');
      byId('name-error').hidden = true;
      result.hidden = true;
      builder.hidden = false;
      updateControls();
      nameInput.focus({ preventScroll: true });
      builder.scrollIntoView({ block: 'start', behavior: 'auto' });
    });
    byId('copy-curse').addEventListener('click', async () => {
      if (phase !== 'result') return;
      const version = ++copyVersion;
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard is unavailable');
        await navigator.clipboard.writeText(fullCurse);
        if (version !== copyVersion || phase !== 'result') return;
        byId('copy-curse').textContent = 'Copied!';
        byId('copy-status').textContent = 'Your curse has been copied.';
        clearTimeout(copyTimer);
        copyTimer = setTimeout(() => { byId('copy-curse').textContent = 'Copy curse'; }, 2000);
      } catch {
        if (version !== copyVersion || phase !== 'result') return;
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(byId('finalResult'));
        selection?.removeAllRanges();
        selection?.addRange(range);
        byId('copy-status').textContent = 'Automatic copying is unavailable. Your curse is selected; use your device’s Copy command.';
      }
    });
    window.addEventListener('pagehide', () => {
      clearTimeout(revealTimer);
      clearTimeout(copyTimer);
      stopSound();
      if (phase === 'loading') { closeDialog(); phase = 'building'; updateControls(); }
    });
    updateControls();
  }

  // Keep the existing Formspree endpoint and native POST fallback.
  const form = byId('contact-form');
  if (form && typeof window.fetch === 'function' && typeof window.AbortController === 'function' && typeof window.FormData === 'function') {
    const fields = ['fullname', 'email', 'message'].map(byId);
    const formStatus = byId('form-status');
    const sendButton = byId('send-message');
    let sending = false;
    const validateField = (field, showError) => {
      field.setCustomValidity(field.value.trim() ? '' : 'Please complete this field.');
      const valid = field.validity.valid;
      const error = byId(`${field.id}-error`);
      if (showError) {
        error.textContent = valid ? '' : field.type === 'email' && field.validity.typeMismatch ? 'Enter a valid email address, such as name@example.com.' : field.validationMessage;
        error.hidden = valid;
        if (valid) field.removeAttribute('aria-invalid');
        else field.setAttribute('aria-invalid', 'true');
      }
      return valid;
    };
    fields.forEach((field) => {
      field.addEventListener('input', () => validateField(field, field.hasAttribute('aria-invalid')));
      field.addEventListener('blur', () => { if (field.value.length) validateField(field, true); });
      field.addEventListener('invalid', () => validateField(field, true));
    });
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (sending) return;
      fields.forEach((field) => { field.value = field.value.trim(); });
      const validity = fields.map((field) => validateField(field, true));
      if (validity.some((valid) => !valid)) {
        fields[validity.indexOf(false)].focus();
        form.reportValidity();
        return;
      }
      sending = true;
      sendButton.disabled = true;
      sendButton.textContent = 'Sending...';
      form.setAttribute('aria-busy', 'true');
      formStatus.textContent = 'Sending your message...';
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' }, signal: controller.signal });
        const data = await response.json();
        if (!response.ok || data.ok !== true) throw new Error('Delivery was not confirmed');
        // Only a confirmed successful service response reaches the thank-you page.
        try { sessionStorage.setItem('beetlejuice-message-sent', 'yes'); } catch { /* Storage is optional. */ }
        form.reset();
        window.location.assign('thank-you.html');
      } catch {
        formStatus.textContent = 'We could not confirm delivery. Your message is still here. Check your connection and any confirmation before trying again, to avoid sending it twice.';
        formStatus.focus({ preventScroll: true });
      } finally {
        clearTimeout(timeout);
        sending = false;
        sendButton.disabled = false;
        sendButton.textContent = 'Send message';
        form.removeAttribute('aria-busy');
      }
    });
  }
  if (byId('thanks-message')) {
    try {
      if (sessionStorage.getItem('beetlejuice-message-sent') === 'yes') {
        byId('thanks-message').textContent = 'Your message was sent successfully. Thanks for contacting The Magic Numb3rs.';
        sessionStorage.removeItem('beetlejuice-message-sent');
      }
    } catch { /* A directly opened page never claims an unconfirmed delivery. */ }
  }
})();
