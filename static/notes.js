let noteTitle = "";
const blocks = [];

function toggleComposer(e) {
  const composer = document.getElementById('composer');
  if (composer.classList.contains('open')) {
    closeComposer();
  } else {
    composer.classList.add('open');
    document.getElementById('note-title').focus();
  }
}

function closeComposer() {
  document.getElementById('composer').classList.remove('open');
  resetComposer();
}

function resetComposer() {
  noteTitle = ""; blocks.length = 0;
  document.getElementById('note-title').value = "";
  document.getElementById('block-headline').value = "";
  document.getElementById('block-description').value = "";
  document.getElementById('staged-blocks').innerHTML = "";
  document.getElementById('block-counter').textContent = "";
  document.getElementById('title-preview').classList.remove('show');
  showStep('step-title');
}

function showStep(id) {
  document.querySelectorAll('.composer-step').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function goToBlocks() {
  const val = document.getElementById('note-title').value.trim();
  if (!val) {
    document.getElementById('note-title').focus();
    document.getElementById('note-title').style.borderColor = '#c9965a';
    setTimeout(() => document.getElementById('note-title').style.borderColor = '', 1000);
    return;
  }
  noteTitle = val;
  document.getElementById('title-preview-text').textContent = noteTitle;
  document.getElementById('title-preview').classList.add('show');
  showStep('step-blocks');
  document.getElementById('block-headline').focus();
}

function appendBlock() {
  const headline = document.getElementById('block-headline').value.trim();
  const description = document.getElementById('block-description').value.trim();
  if (!headline || !description) {
    alert("Fill in both headline and description.");
    return;
  }
  blocks.push({ headline, description });
  const el = document.createElement('div');
  el.className = 'staged-block';
  el.innerHTML = `
      <div class="staged-block-headline">✦ ${headline}</div>
      <div class="staged-block-desc">${description}</div>`;
  document.getElementById('staged-blocks').appendChild(el);
  document.getElementById('block-counter').textContent =
    `${blocks.length} block${blocks.length > 1 ? 's' : ''} added`;
  document.getElementById('block-headline').value = "";
  document.getElementById('block-description').value = "";
  document.getElementById('block-headline').focus();
}

async function saveNote() {
  if (!noteTitle) { alert("Title missing."); return; }
  if (!blocks.length) { alert("Add at least one block."); return; }
  try {
    const res = await fetch("/store-note", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: noteTitle, blocks })
    });
    const result = await res.json();
    if (result.success) {
      closeComposer();
      location.reload();
    } else {
      alert("Error: " + result.message);
    }
  } catch (err) {
    console.error(err);
    alert("Connection error.");
  }
}

document.getElementById('note-title')
  .addEventListener('keydown', e => { if (e.key === 'Enter') goToBlocks(); });
document.getElementById('block-headline')
  .addEventListener('keydown', e => { if (e.key === 'Enter') document.getElementById('block-description').focus(); });