const API = "http://127.0.0.1:8000";

/* ================= TOKEN RIÊNG CHO ADMIN ================= */
const ADMIN_TOKEN_KEY = "admin_token";

function getToken() {
  return localStorage.getItem(ADMIN_TOKEN_KEY);
}
function setToken(token) {
  localStorage.setItem(ADMIN_TOKEN_KEY, token);
}
function clearToken() {
  localStorage.removeItem(ADMIN_TOKEN_KEY);
}

/* ================= UI HELPERS ================= */

function showLogin() {
  document.getElementById("loginBox").style.display = "flex";
  document.getElementById("adminBox").style.display = "none";
}

function showAdminUI() {
  document.getElementById("loginBox").style.display = "none";
  document.getElementById("adminBox").style.display = "block";
}

/* ================= INIT CHECK ================= */

async function showAdmin() {
  const token = getToken();
  if (!token) {
    showLogin();
    return;
  }

  try {
    const res = await fetch(`${API}/admin/users`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!res.ok) {
      clearToken();
      showLogin();
      return;
    }

    showAdminUI();
    switchTab("knowledge");
  } catch (err) {
    console.error(err);
    clearToken();
    showLogin();
  }
}

/* ================= TABS ================= */

function switchTab(tab) {
  document.querySelectorAll(".tab-btn").forEach(b =>
    b.classList.remove("active")
  );
  document.querySelectorAll(".tab-content").forEach(c =>
    c.classList.remove("active")
  );

  document.getElementById(`tab-${tab}`).classList.add("active");
  document.getElementById(`content-${tab}`).classList.add("active");

  if (tab === "knowledge") AdminUI.loadList();
  if (tab === "users") UserUI.loadList();
}

/* ================= LOGIN ================= */

async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorEl = document.getElementById("loginError");

  if (!username || !password) {
    errorEl.innerText = "Vui lòng nhập đầy đủ thông tin";
    return;
  }

  errorEl.innerText = "";

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password })
    });

    const data = await res.json();
    if (!res.ok) {
      errorEl.innerText = data.detail || "Đăng nhập thất bại";
      return;
    }

    // 🔒 LƯU TOKEN ADMIN
    setToken(data.access_token);

    // ⚠️ ẨN LOGIN NGAY
    showAdminUI();

    // ✅ CHECK QUYỀN ADMIN
    const check = await fetch(`${API}/admin/users`, {
      headers: { Authorization: `Bearer ${data.access_token}` }
    });

    if (!check.ok) {
      clearToken();
      errorEl.innerText = "Tài khoản không có quyền admin";
      showLogin();
      return;
    }

    switchTab("knowledge");
  } catch (err) {
    console.error(err);
    errorEl.innerText = "Không thể kết nối server";
  }
}

function logout() {
  if (!confirm("Bạn muốn đăng xuất admin?")) return;
  clearToken();
  showLogin();
}

/* ================= KNOWLEDGE ================= */

const AdminUI = {
  selectedId: null,

  async loadList() {
    const res = await fetch(`${API}/admin/knowledge`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });

    if (!res.ok) return logout();

    const data = await res.json();
    const list = document.getElementById("knowledge-list");
    list.innerHTML = "";

    if (!data.length) {
      list.innerHTML = "<p style='opacity:.6'>Chưa có dữ liệu</p>";
      return;
    }

    data.forEach(k => {
      const div = document.createElement("div");
      div.className = "knowledge-item";
      div.innerText = `#${k.id} • ${k.title}`;
      div.onclick = () => this.select(k);
      list.appendChild(div);
    });
  },

  select(k) {
    this.selectedId = k.id;
    document.getElementById("k-id").value = k.id;
    document.getElementById("k-title").value = k.title;
    document.getElementById("k-content").value = k.content;
  },

  newItem() {
    this.selectedId = null;
    document.getElementById("k-id").value = "";
    document.getElementById("k-title").value = "";
    document.getElementById("k-content").value = "";
  },

  async save() {
    const id = document.getElementById("k-id").value;
    const title = document.getElementById("k-title").value.trim();
    const content = document.getElementById("k-content").value.trim();

    if (!title || !content) {
      alert("Nhập đầy đủ nội dung");
      return;
    }

    const res = await fetch(
      id ? `${API}/admin/knowledge/${id}` : `${API}/admin/knowledge`,
      {
        method: id ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`
        },
        body: JSON.stringify({ title, content })
      }
    );

    if (!res.ok) return alert("Lỗi khi lưu");

    this.newItem();
    this.loadList();
  }
};

/* ================= USERS ================= */

const UserUI = {
  async loadList() {
    const res = await fetch(`${API}/admin/users`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });

    if (!res.ok) return logout();

    const users = await res.json();
    const list = document.getElementById("users-list");
    list.innerHTML = "";

    users.forEach(u => {
      const div = document.createElement("div");
      div.className = "user-item";

      const info = document.createElement("div");
      info.className = "user-info";
      info.innerHTML = `
        <div class="user-name">${u.username}</div>
        <div class="user-email">${u.email}</div>
        <div class="user-meta">
          ${u.is_admin ? "<span class='user-badge badge-admin'>ADMIN</span>" : ""}
          ${u.is_active ? "<span class='user-badge badge-active'>ACTIVE</span>" : "<span class='user-badge badge-inactive'>LOCKED</span>"}
        </div>
      `;

      const actions = document.createElement("div");
      actions.className = "user-actions";

      if (!u.is_admin) {
        actions.innerHTML = `
          <button class="btn-edit" onclick='UserUI.edit(${JSON.stringify(u)})'>Sửa</button>
          <button class="btn-password" onclick='UserUI.changePassword(${u.id})'>MK</button>
          <button class="btn-delete" onclick='UserUI.remove(${u.id})'>Xóa</button>
        `;
      } else {
        actions.innerHTML = `<i>Admin hệ thống</i>`;
      }

      div.appendChild(info);
      div.appendChild(actions);
      list.appendChild(div);
    });
  },

  async edit(user) {
    const email = prompt("Email mới:", user.email);
    if (!email) return;

    const is_active = confirm("Tài khoản hoạt động?");
    const is_admin = confirm("Cấp quyền admin?");

    const res = await fetch(`${API}/admin/users/${user.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`
      },
      body: JSON.stringify({ email, is_active, is_admin })
    });

    if (!res.ok) return alert("Cập nhật thất bại");
    this.loadList();
  },

  async changePassword(id) {
    const pwd = prompt("Nhập mật khẩu mới (>=6 ký tự)");
    if (!pwd || pwd.length < 6) return alert("Mật khẩu không hợp lệ");

    const res = await fetch(`${API}/admin/users/${id}/password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`
      },
      body: JSON.stringify({ new_password: pwd })
    });

    if (!res.ok) return alert("Đổi mật khẩu thất bại");
    alert("Đã đổi mật khẩu");
  },

  async remove(id) {
    if (!confirm("Xóa tài khoản này?")) return;

    const res = await fetch(`${API}/admin/users/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${getToken()}` }
    });

    if (!res.ok) return alert("Xóa thất bại");
    this.loadList();
  }
};

/* ================= INIT ================= */

window.addEventListener("DOMContentLoaded", () => {
  showAdmin();
});
