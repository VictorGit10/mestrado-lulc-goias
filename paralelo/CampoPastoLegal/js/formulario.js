/* formulario.js — modal, preview de imagem e submissão */
(function () {
  'use strict';

  const modal = document.getElementById('modal-form');
  const fab = document.getElementById('fab-form');
  const btnClose = document.getElementById('btn-close-modal');
  const form = document.getElementById('campo-form');
  const statusEl = document.getElementById('form-status');
  const selectFazenda = document.getElementById('f-fazenda');
  const fileInput = document.getElementById('f-imagem');
  const preview = document.getElementById('file-preview');
  const btnLocal = document.getElementById('btn-salvar-local');

  // Popula select de fazendas
  FAZENDAS.forEach(fz => {
    const opt = document.createElement('option');
    opt.value = fz.id;
    opt.textContent = fz.nome;
    selectFazenda.appendChild(opt);
  });

  // Abrir/fechar modal
  function openModal() {
    if (typeof modal.showModal === 'function') {
      modal.showModal();
    } else {
      modal.setAttribute('open', '');
    }
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (typeof modal.close === 'function') {
      modal.close();
    } else {
      modal.removeAttribute('open');
      modal.dispatchEvent(new Event('close'));
    }
  }

  if (fab) fab.addEventListener('click', openModal);
  if (btnClose) btnClose.addEventListener('click', closeModal);

  // Fecha ao clicar no backdrop (fora da modal-card)
  modal.addEventListener('click', (e) => {
    const rect = modal.getBoundingClientRect();
    const isInDialog = (rect.top <= e.clientY && e.clientY <= rect.top + rect.height &&
                        rect.left <= e.clientX && e.clientX <= rect.left + rect.width);
    if (!isInDialog) {
      closeModal();
    }
  });

  // Limpa o formulário e restaura o scroll ao fechar (cobre fechamento nativo via Esc)
  modal.addEventListener('close', () => {
    document.body.style.overflow = '';
    form.reset();
    clearFile();
    statusEl.textContent = '';
    statusEl.className = 'form-hint';
  });

  const uploadZone = document.getElementById('upload-zone');

  if (uploadZone && fileInput) {
    uploadZone.addEventListener('click', () => fileInput.click());

    // Drag and Drop styling and events
    ['dragenter', 'dragover'].forEach(eventName => {
      uploadZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      uploadZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
      }, false);
    });

    uploadZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length) {
        fileInput.files = files;
        processFile(files[0]);
      }
    });
  }

  let currentBase64 = '';
  let currentFileName = '';
  let currentFileSize = '';

  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
      processFile(file);
    } else {
      clearFile();
    }
  });

  function clearFile() {
    preview.innerHTML = '';
    currentBase64 = '';
    currentFileName = '';
    currentFileSize = '';
  }

  function processFile(file) {
    clearFile();
    if (!file) return;

    currentFileName = file.name;
    currentFileSize = formatBytes(file.size);

    const reader = new FileReader();
    reader.onload = ev => {
      currentBase64 = ev.target.result;

      if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = currentBase64;
        img.alt = file.name;
        preview.appendChild(img);
      } else {
        const card = document.createElement('div');
        card.className = 'file-card';
        card.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          <div class="file-card-details">
            <div class="file-card-name" title="${file.name}">${file.name}</div>
            <div class="file-card-size">${currentFileSize}</div>
          </div>
        `;
        preview.appendChild(card);
      }
    };
    reader.readAsDataURL(file);
  }

  function formatBytes(bytes, decimals = 1) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  function getPayload() {
    return {
      timestamp: new Date().toISOString(),
      fazenda: selectFazenda.value,
      fazenda_nome: selectFazenda.options[selectFazenda.selectedIndex]?.text || '',
      tipo: document.getElementById('f-tipo').value,
      descricao: document.getElementById('f-descricao').value.trim(),
      url: document.getElementById('f-url').value.trim(),
      arquivo_nome: currentFileName,
      arquivo_tamanho: currentFileSize,
      imagem_base64: currentBase64
    };
  }

  function showStatus(msg, type) {
    statusEl.textContent = msg;
    statusEl.className = 'form-hint ' + (type === 'success' ? 'is-success' : type === 'error' ? 'is-error' : '');
  }

  // Submissão para Google Sheets (placeholder endpoint)
  // Configure a URL real após criar o Apps Script conforme README.md
  const SHEETS_ENDPOINT = localStorage.getItem('pl_sheets_url') || '';

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }

    const payload = getPayload();
    if (!SHEETS_ENDPOINT) {
      showStatus('Endpoint do Google Sheets não configurado. Salvando localmente…', 'error');
      salvarLocal(payload);
      return;
    }

    showStatus('Enviando…', '');
    try {
      const res = await fetch(SHEETS_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      showStatus('Enviado com sucesso para a planilha.', 'success');
      setTimeout(closeModal, 900);
    } catch (err) {
      showStatus('Falha no envio: ' + err.message + '. Clique em "Salvar localmente".', 'error');
    }
  });

  function salvarLocal(payload) {
    const chave = 'pl_campo_dados';
    const existente = JSON.parse(localStorage.getItem(chave) || '[]');
    existente.push(payload);
    localStorage.setItem(chave, JSON.stringify(existente));
    showStatus('Salvo localmente (' + existente.length + ' registros).', 'success');
    setTimeout(closeModal, 700);
  }

  if (btnLocal) {
    btnLocal.addEventListener('click', () => {
      if (!form.checkValidity()) { form.reportValidity(); return; }
      salvarLocal(getPayload());
    });
  }
}());
