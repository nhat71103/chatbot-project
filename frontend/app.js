const API_URL = "http://127.0.0.1:8000/chat";
const AUTH_API = "http://127.0.0.1:8000/auth";
const CONVERSATIONS_API = "http://127.0.0.1:8000/chat/conversations";

let currentConversationId = null;

/* ===== delete confirm (session only) ===== */
let skipDeleteConfirm = false;

/* ===== loading flag để tránh gọi loadConversations nhiều lần ===== */
let isLoadingConversations = false;

/* ================= UTIL ================= */

function getAuthHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: "Bearer " + token } : {};
}

function updateAuthUI() {
  const isLoggedIn = !!localStorage.getItem("token");
  const username = localStorage.getItem("username");

  document.getElementById("login-hint")
    ?.classList.toggle("hidden", isLoggedIn);

  document.getElementById("logout-btn")
    ?.classList.toggle("hidden", !isLoggedIn);

  // Cập nhật hiển thị username
  const statusEl = document.getElementById("user-status");
  if (statusEl) {
    if (isLoggedIn && username) {
      statusEl.innerHTML = `● Online · <span style="font-weight: 500;">${username}</span>`;
    } else {
      statusEl.innerHTML = "● Online";
    }
  }
}

/* ===== format time ===== */
function timeAgo(isoTime) {
  if (!isoTime) return "";

  let date;
  if (typeof isoTime === "string" && !isoTime.endsWith("Z")) {
    date = new Date(isoTime + "Z");
  } else {
    date = new Date(isoTime);
  }

  if (isNaN(date.getTime())) return "";

  const diff = Math.floor((Date.now() - date.getTime()) / 1000);

  if (diff < 60) return "vừa xong";
  if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
  return `${Math.floor(diff / 86400)} ngày trước`;
}

/* ================= CHAT ================= */

function appendMessage(text, sender = "bot") {
  const messages = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = sender;
  div.innerHTML = String(text).replace(/\n/g, "<br>");
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

async function send() {
  const input = document.getElementById("input");
  const msg = input.value.trim();
  if (!msg) return;

  appendMessage(msg, "user");
  input.value = "";

  document.getElementById("typing").classList.remove("hidden");

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        message: msg,
        conversation_id: currentConversationId
      })
    });

    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        currentConversationId = null;
        updateAuthUI();
        loadConversations();
        document.getElementById("login-hint").classList.remove("hidden");
        alert("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
        return;
      }
      const errorData = await res.json().catch(() => ({}));
      alert(errorData.detail || "Lỗi khi gửi tin nhắn");
      document.getElementById("typing").classList.add("hidden");
      return;
    }

    const data = await res.json();
    document.getElementById("typing").classList.add("hidden");

    appendMessage(data.answer, "bot");

    if (!data.guest) {
      currentConversationId = data.conversation_id;
      await loadConversations();
    } else {
      document.getElementById("login-hint").classList.remove("hidden");
    }
  } catch (error) {
    document.getElementById("typing").classList.add("hidden");
    alert("Lỗi kết nối đến server");
  }
}

function newConversation() {
  currentConversationId = null;
  document.getElementById("messages").innerHTML =
    `<div class="bot">Xin chào 👋 Tôi có thể giúp bạn về CNTT.</div>`;
}

/* ================= CONVERSATIONS ================= */

function searchConversations(q) {
  loadConversations(q);
}

/* ===== PIN / UNPIN ===== */
async function togglePin(convo) {
  const token = localStorage.getItem("token");
  if (!token) return alert("Bạn cần đăng nhập");

  const url = convo.is_pinned
    ? `${CONVERSATIONS_API}/${convo.id}/unpin`
    : `${CONVERSATIONS_API}/${convo.id}/pin`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: getAuthHeaders()
    });

    if (!res.ok) {
      alert("Lỗi khi ghim/bỏ ghim. Vui lòng thử lại.");
      return;
    }

    await loadConversations();
  } catch (error) {
    alert("Lỗi kết nối đến server");
  }
}

async function loadConversations(search = "", retryCount = 0) {
  // Tránh gọi nhiều lần cùng lúc
  if (isLoadingConversations && retryCount === 0) {
    return;
  }
  
  isLoadingConversations = true;
  
  const token = localStorage.getItem("token");
  const list = document.getElementById("conversations-list");

  if (!list) {
    isLoadingConversations = false;
    return;
  }

  if (!token) {
    list.innerHTML = `
      <div style="opacity:.6; padding:10px; text-align:center;">
        Đăng nhập để xem lịch sử chat
      </div>`;
    isLoadingConversations = false;
    return;
  }

  try {
    const url = search
      ? `${CONVERSATIONS_API}?search=${encodeURIComponent(search)}`
      : CONVERSATIONS_API;

    // Tạo AbortController cho timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const res = await fetch(url, { 
      headers: getAuthHeaders(),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        currentConversationId = null;
        updateAuthUI();
        list.innerHTML = `
          <div style="opacity:.6; padding:10px; text-align:center;">
            Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.
          </div>`;
        isLoadingConversations = false;
        return;
      }
      // Retry nếu lỗi 500 hoặc 503 (server error)
      if ((res.status === 500 || res.status === 503) && retryCount < 3) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
        isLoadingConversations = false;
        return loadConversations(search, retryCount + 1);
      }
      list.innerHTML = `
        <div style="opacity:.6; padding:10px; text-align:center; color: #ef4444;">
          Lỗi khi tải lịch sử chat (${res.status})
        </div>`;
      isLoadingConversations = false;
      return;
    }

    const data = await res.json();

    if (!Array.isArray(data)) {
      list.innerHTML = `
        <div style="opacity:.6; padding:10px; text-align:center; color: #ef4444;">
          Dữ liệu không hợp lệ
        </div>`;
      isLoadingConversations = false;
      return;
    }

    list.innerHTML = "";

    if (data.length === 0) {
      list.innerHTML = `
        <div style="opacity:.6; padding:10px; text-align:center;">
          Chưa có cuộc hội thoại nào
        </div>`;
      isLoadingConversations = false;
      return;
    }

    data.forEach(c => {
      const item = document.createElement("div");
      item.className =
        "conversation-item " + (currentConversationId === c.id ? "active" : "");
      item.dataset.convId = c.id;
      
      item.onclick = function(e) {
        const target = e.target;
        if (target.closest(".pin-star") || target.closest(".delete-conv-btn")) {
          return;
        }
        loadConversation(c.id);
      };

      const row = document.createElement("div");
      row.className = "conv-row";

      /* LEFT: STAR + TITLE */
      const left = document.createElement("div");
      left.className = "conv-left";

      const star = document.createElement("span");
      star.className = "pin-star" + (c.is_pinned ? " pinned" : "");
      star.innerText = "⭐";
      star.title = c.is_pinned ? "Bỏ ghim" : "Ghim";
      star.onclick = function(e) {
        e.stopPropagation();
        e.preventDefault();
        togglePin(c);
      };

      const title = document.createElement("b");
      title.innerText = c.title || "Cuộc hội thoại";

      left.appendChild(star);
      left.appendChild(title);

      /* DELETE */
      const delBtn = document.createElement("button");
      delBtn.className = "delete-conv-btn";
      delBtn.innerText = "🗑️";
      delBtn.title = "Xóa hội thoại";
      delBtn.onclick = function(e) {
        e.stopPropagation();
        e.preventDefault();
        confirmDeleteConversation(c.id);
      };

      row.appendChild(left);
      row.appendChild(delBtn);

      const meta = document.createElement("small");
      meta.innerText =
        `${c.message_count} tin nhắn · ${timeAgo(c.last_message_at)}`;

      item.appendChild(row);
      item.appendChild(meta);

      list.appendChild(item);
    });
    
    isLoadingConversations = false;
  } catch (error) {
    const list = document.getElementById("conversations-list");
    if (!list) {
      isLoadingConversations = false;
      return;
    }
    
    // Retry nếu là lỗi network và chưa retry quá 3 lần
    if ((error.name === 'TypeError' || error.name === 'NetworkError' || error.name === 'AbortError') && retryCount < 3) {
      list.innerHTML = `
        <div style="opacity:.6; padding:10px; text-align:center;">
          Đang kết nối đến server... (thử lại lần ${retryCount + 1})
        </div>`;
      await new Promise(resolve => setTimeout(resolve, 2000 * (retryCount + 1)));
      isLoadingConversations = false;
      return loadConversations(search, retryCount + 1);
    }
    
    list.innerHTML = `
      <div style="opacity:.6; padding:10px; text-align:center; color: #ef4444;">
        Lỗi kết nối đến server. Vui lòng kiểm tra backend đã chạy chưa.
      </div>`;
    isLoadingConversations = false;
  }
}

async function loadConversation(id) {
  if (!id || isNaN(id)) {
    return;
  }
  
  try {
    const res = await fetch(
      `${CONVERSATIONS_API}/${id}/messages`,
      { headers: getAuthHeaders() }
    );
    
    if (!res.ok) {
      if (res.status === 401) {
        alert("Bạn cần đăng nhập để xem lịch sử chat");
        return;
      }
      if (res.status === 404) {
        alert("Không tìm thấy cuộc hội thoại này");
        return;
      }
      alert("Lỗi khi tải cuộc hội thoại");
      return;
    }

    const messages = await res.json();
    
    if (!Array.isArray(messages)) {
      alert("Dữ liệu không hợp lệ");
      return;
    }

    currentConversationId = id;
    const box = document.getElementById("messages");
    if (!box) return;
    
    box.innerHTML = "";

    if (messages.length === 0) {
      box.innerHTML = "<div class='bot'>Chưa có tin nhắn nào trong cuộc hội thoại này.</div>";
    } else {
      messages.forEach(m => {
        appendMessage(m.question, "user");
        appendMessage(m.answer, "bot");
      });
    }

    // Chỉ reload conversations nếu cần cập nhật active state, không reload nếu đang load
    if (!isLoadingConversations) {
      loadConversations();
    }
  } catch (error) {
    alert("Lỗi khi tải cuộc hội thoại");
  }
}

/* ===== delete conversation ===== */

function confirmDeleteConversation(id) {
  if (!skipDeleteConfirm) {
    if (!confirm("Bạn có chắc muốn xóa cuộc hội thoại này?")) return;

    const remember = confirm(
      "Ghi nhớ lựa chọn và không hỏi lại trong phiên này?"
    );
    if (remember) skipDeleteConfirm = true;
  }

  deleteConversation(id);
}

async function deleteConversation(id) {
  try {
    const res = await fetch(`${CONVERSATIONS_API}/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });

    if (!res.ok) {
      if (res.status === 401) {
        alert("❌ Bạn cần đăng nhập để xóa cuộc hội thoại");
        return;
      }
      if (res.status === 404) {
        alert("❌ Không tìm thấy cuộc hội thoại này");
        return;
      }
      alert("❌ Xóa thất bại. Vui lòng thử lại.");
      return;
    }

    if (currentConversationId === id) {
      newConversation();
    }
    
    await loadConversations();
  } catch (error) {
    alert("❌ Lỗi kết nối đến server");
  }
}

/* ================= AUTH ================= */

let authMode = "login";

function resetAuthInputs() {
  document.getElementById("auth-username").value = "";
  document.getElementById("auth-password").value = "";
  document.getElementById("auth-email").value = "";
}

function openLogin() {
  authMode = "login";
  resetAuthInputs();
  document.getElementById("auth-modal").classList.remove("hidden");
  document.getElementById("auth-title").innerText = "Đăng nhập";
  document.getElementById("auth-email").classList.add("hidden");
  document.getElementById("auth-switch-text").innerText =
    "Chưa có tài khoản? Đăng ký";
}

function openRegister() {
  authMode = "register";
  resetAuthInputs();
  document.getElementById("auth-modal").classList.remove("hidden");
  document.getElementById("auth-title").innerText = "Đăng ký";
  document.getElementById("auth-email").classList.remove("hidden");
  document.getElementById("auth-switch-text").innerText =
    "Đã có tài khoản? Đăng nhập";
}

function switchAuth() {
  authMode === "login" ? openRegister() : openLogin();
}

function closeAuth() {
  document.getElementById("auth-modal").classList.add("hidden");
}

async function submitAuth() {
  const username = document.getElementById("auth-username").value.trim();
  const password = document.getElementById("auth-password").value.trim();
  const email = document.getElementById("auth-email").value.trim();

  if (!username || !password || (authMode === "register" && !email)) {
    alert("Vui lòng nhập đủ thông tin");
    return;
  }

  if (authMode === "login") {
    const res = await fetch(AUTH_API + "/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password })
    });

    const data = await res.json();
    if (!res.ok) return alert(data.detail);

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("username", username);
    closeAuth();
    updateAuthUI();
    loadConversations();

    appendMessage(`👋 Xin chào <b>${username}</b>!`, "bot");
  } else {
    const res = await fetch(AUTH_API + "/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });

    if (res.ok) {
      alert("🎉 Đăng ký thành công! Hãy đăng nhập");
      openLogin();
    } else {
      const data = await res.json();
      alert(data.detail);
    }
  }
}

function logout() {
  if (!confirm("Bạn muốn đăng xuất?")) return;

  localStorage.removeItem("token");
  localStorage.removeItem("username");
  currentConversationId = null;

  document.getElementById("messages").innerHTML =
    `<div class="bot">👋 Bạn đã đăng xuất</div>`;

  updateAuthUI();
  loadConversations();
}

/* ================= INIT ================= */

document.getElementById("auth-modal").addEventListener("click", e => {
  if (e.target.id === "auth-modal") closeAuth();
});

// Lắng nghe storage event để đồng bộ khi token thay đổi ở tab khác
window.addEventListener("storage", (e) => {
  if (e.key === "token") {
    updateAuthUI();
    loadConversations();
  }
});


window.addEventListener("DOMContentLoaded", async () => {
  updateAuthUI();
  
  // Load conversations khi trang load - đảm bảo luôn được gọi
  await loadConversations();
  
  // Enter key cho input chat
  const chatInput = document.getElementById("input");
  if (chatInput) {
    chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        send();
      }
    });
  }

  // Enter key cho form đăng nhập/đăng ký
  const authUsername = document.getElementById("auth-username");
  const authEmail = document.getElementById("auth-email");
  const authPassword = document.getElementById("auth-password");
  
  if (authUsername) {
    authUsername.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        submitAuth();
      }
    });
  }
  
  if (authEmail) {
    authEmail.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        submitAuth();
      }
    });
  }
  
  if (authPassword) {
    authPassword.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        submitAuth();
      }
    });
  }
});

/* expose */
window.openLogin = openLogin;
window.openRegister = openRegister;
window.switchAuth = switchAuth;
window.submitAuth = submitAuth;
window.send = send;
window.newConversation = newConversation;
window.loadConversation = loadConversation;
window.searchConversations = searchConversations;
window.logout = logout;
