(() => {
  const screen = document.querySelector("#screen");
  const form = document.querySelector("#command-form");
  const command = document.querySelector("#command");
  const state = document.querySelector("#connection-state");
  const reconnect = document.querySelector("#reconnect");
  const theme = document.querySelector("#theme");
  const rememberHistory = document.querySelector("#remember-history");
  const screenFrame = document.querySelector(".screen-frame");
  const saveTextButton = document.querySelector("#save-text");
  const downloadsPanel = document.querySelector("#downloads-panel");
  const downloadList = document.querySelector("#download-list");
  const MAX_SCREEN_CHARS = 120000;
  const MAX_TRANSCRIPT_CHARS = 5000000;
  const MAX_HISTORY = 100;
  const HISTORY_KEY = "cis-command-history";
  let socket;
  let passwordMode = false;
  let processingTimer;
  const history = [];
  let historyIndex = 0;
  let historyDraft = "";
  let transcript = "";
  let transcriptTruncated = false;

  function downloadLink(url, name) {
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    link.textContent = name;
    return link;
  }

  function saveText() {
    const selection = window.getSelection();
    const selected = selection && !selection.isCollapsed &&
      screen.contains(selection.anchorNode) && screen.contains(selection.focusNode)
      ? selection.toString() : "";
    const text = selected || (transcriptTruncated ? "[Earlier session text omitted: capture limit reached.]\n" : "") + transcript;
    if (!text) {
      setState("NO TEXT TO SAVE");
      return;
    }
    const name = `CIS-${selected ? "selection" : "session"}-${new Date().toISOString().replace(/[:.]/g, "-")}.txt`;
    const url = URL.createObjectURL(new Blob([text], {type: "text/plain;charset=utf-8"}));
    const link = downloadLink(url, name);
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    setState("TEXT DOWNLOAD REQUESTED", "connected");
  }

  function offerDownload(message) {
    if (!/^\/downloads\/[a-f0-9]{32}\/[a-f0-9]{32}$/.test(message.url)) return;
    const link = downloadLink(message.url, message.name);
    const item = document.createElement("li");
    item.append(link);
    downloadList.prepend(item);
    downloadsPanel.hidden = false;
    link.click();
    setState("FILE READY TO SAVE", "connected");
  }

  function loadHistory() {
    if (localStorage.getItem("cis-remember-history") !== "1") return;
    rememberHistory.checked = true;
    try {
      const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      history.push(...saved.filter((item) => typeof item === "string").slice(-MAX_HISTORY));
    } catch {
      localStorage.removeItem(HISTORY_KEY);
    }
    historyIndex = history.length;
  }

  function saveHistory() {
    if (rememberHistory.checked) {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    }
  }

  function rememberCommand(value) {
    if (!value || history.at(-1) === value) return;
    history.push(value);
    if (history.length > MAX_HISTORY) history.splice(0, history.length - MAX_HISTORY);
    saveHistory();
  }

  function setInputValue(value, cursor = value.length) {
    command.value = value;
    requestAnimationFrame(() => command.setSelectionRange(cursor, cursor));
  }

  function setState(label, kind = "") {
    state.textContent = label;
    state.className = kind;
  }

  function restoreInputFocus() {
    if (!document.hidden && !command.disabled) {
      requestAnimationFrame(() => command.focus({preventScroll: true}));
    }
  }

  function appendOutput(text) {
    clearTimeout(processingTimer);
    if (socket?.readyState === WebSocket.OPEN) setState("CONNECTED", "connected");
    transcript += text.replaceAll("\r", "").replaceAll("\f", "\n");
    if (transcript.length > MAX_TRANSCRIPT_CHARS) {
      transcript = transcript.slice(-MAX_TRANSCRIPT_CHARS);
      transcriptTruncated = true;
    }
    const sections = text.split("\f");
    if (sections.length > 1) screen.textContent = "";
    const visible = sections[sections.length - 1].replaceAll("\r", "");
    screen.textContent += visible;
    if (screen.textContent.length > MAX_SCREEN_CHARS) {
      screen.textContent = screen.textContent.slice(-MAX_SCREEN_CHARS);
    }
    passwordMode = /(?:password|retype)[^\n:]*:\s*$/i.test(screen.textContent);
    command.type = passwordMode ? "password" : "text";
    screen.scrollTop = screen.scrollHeight;
  }

  function connect() {
    if (socket && socket.readyState < WebSocket.CLOSING) socket.close();
    screen.textContent = "Connecting to CompuServe...\n";
    transcript = "";
    transcriptTruncated = false;
    setState("CONNECTING");
    command.disabled = true;
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${protocol}://${location.host}/terminal`);
    const connection = socket;

    socket.addEventListener("open", () => {
      if (connection !== socket) return;
      setState("CONNECTED", "connected");
      command.disabled = false;
      restoreInputFocus();
    });

    socket.addEventListener("message", (event) => {
      if (connection !== socket) return;
      const message = JSON.parse(event.data);
      if (message.type === "output") appendOutput(message.data);
      if (message.type === "download") offerDownload(message);
      if (message.type === "status" && message.data !== "CONNECTED") {
        appendOutput(`\n[${message.data}]\n`);
      }
    });

    socket.addEventListener("close", () => {
      if (connection !== socket) return;
      setState("DISCONNECTED", "error");
      command.disabled = true;
    });

    socket.addEventListener("error", () => {
      if (connection === socket) setState("CONNECTION ERROR", "error");
    });
  }

  function sendCommand(value) {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    const wasPassword = passwordMode;
    appendOutput(wasPassword ? "••••••\n" : `${value}\n`);
    socket.send(JSON.stringify({type: "input", data: value}));
    setState("INPUT SENT", "connected");
    processingTimer = setTimeout(() => {
      if (socket?.readyState === WebSocket.OPEN) setState("PROCESSING…", "connected");
    }, 2500);
    command.value = "";
    command.type = "text";
    passwordMode = false;
    if (!wasPassword) rememberCommand(value);
    historyIndex = history.length;
    historyDraft = "";
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendCommand(command.value);
  });

  command.addEventListener("keydown", (event) => {
    if (passwordMode) return;
    if (["ArrowUp", "ArrowDown"].includes(event.key)) {
      event.preventDefault();
      if (event.key === "ArrowUp" && historyIndex === history.length) historyDraft = command.value;
      historyIndex = event.key === "ArrowUp" ? Math.max(0, historyIndex - 1) : Math.min(history.length, historyIndex + 1);
      setInputValue(historyIndex < history.length ? history[historyIndex] : historyDraft);
      return;
    }
    if (event.ctrlKey && !event.altKey && !event.metaKey && ["a", "e"].includes(event.key.toLowerCase())) {
      event.preventDefault();
      const cursor = event.key.toLowerCase() === "a" ? 0 : command.value.length;
      command.setSelectionRange(cursor, cursor);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      setInputValue("");
      historyIndex = history.length;
      historyDraft = "";
    }
  });

  command.addEventListener("input", () => {
    if (historyIndex !== history.length) {
      historyIndex = history.length;
      historyDraft = command.value;
    }
  });

  document.querySelectorAll(".quick-command").forEach((button) => {
    button.addEventListener("click", () => sendCommand(button.dataset.command));
  });

  reconnect.addEventListener("click", connect);
  saveTextButton.addEventListener("click", saveText);
  screenFrame.addEventListener("click", (event) => {
    if (!window.getSelection()?.isCollapsed) return;
    if (!event.target.closest("button, select")) restoreInputFocus();
  });
  window.addEventListener("focus", restoreInputFocus);
  document.addEventListener("visibilitychange", restoreInputFocus);
  document.addEventListener("keydown", (event) => {
    if (
      !command.disabled &&
      document.activeElement !== command &&
      !event.ctrlKey && !event.altKey && !event.metaKey &&
      (event.key.length === 1 || event.key === "Backspace" || event.key === "Enter")
    ) {
      command.focus({preventScroll: true});
    }
  });
  theme.addEventListener("change", () => {
    document.documentElement.dataset.theme = theme.value;
    localStorage.setItem("cis-theme", theme.value);
  });
  rememberHistory.addEventListener("change", () => {
    localStorage.setItem("cis-remember-history", rememberHistory.checked ? "1" : "0");
    if (rememberHistory.checked) saveHistory();
    else localStorage.removeItem(HISTORY_KEY);
  });

  const savedTheme = localStorage.getItem("cis-theme") || "amber";
  theme.value = savedTheme;
  document.documentElement.dataset.theme = savedTheme;
  loadHistory();
  connect();
})();
