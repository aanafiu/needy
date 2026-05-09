setTimeout(function () {
  const flash = document.getElementById("flash-message");
  if (flash) {
    flash.style.transition = " opacity 0.5s ease";
    flash.style.opacity = "0";

    setTimeout(() => {
      flash.remove();
    }, 500);
  }
}, 3000);


function escapeHTML(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function nl2br(str) {
  return escapeHTML(str).replace(/\n/g, '<br>');
}

function openModal(index) {
  const note = allPublicNotes[index];
  if (!note) return;
  
  document.getElementById("modal-title").innerText = note.title;

  document.getElementById("modal-meta").innerHTML = `
    By <strong>${note.author}</strong> • ${note.created_at || ''}
  `;

  let html = "";

  (note.blocks || []).forEach(block => {
    html += `
      <div class="modal-block">
        <h4>${block.headline}</h4>
        <p>${nl2br(block.description)}</p>
      </div>
    `;
  });

  document.getElementById("modal-body").innerHTML = html;
  document.getElementById("note-modal").style.display = "block";
}

function closeModal() {
  document.getElementById("note-modal").style.display = "none";
}

/* click outside */
window.onclick = function (e) {
  const modal = document.getElementById("note-modal");
  if (e.target === modal) closeModal();
};