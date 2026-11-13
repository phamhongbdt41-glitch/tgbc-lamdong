import os
from functools import wraps
from flask import Flask, request, session, redirect, url_for, send_from_directory, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'thay-bang-chuoi-ngau-nhien')

# Hỗ trợ nhiều tài khoản: USERS=user1:pass1,user2:pass2
# Hoặc dùng APP_PASSWORD cho tài khoản đơn (tương thích cũ)
def load_users():
    users = {}
    users_env = os.environ.get('USERS', '')
    if users_env:
        for entry in users_env.split(','):
            entry = entry.strip()
            if ':' in entry:
                u, p = entry.split(':', 1)
                users[u.strip()] = p.strip()
    if not users:
        # Chế độ tương thích cũ: chỉ mật khẩu, tên đăng nhập mặc định "admin"
        users['admin'] = os.environ.get('APP_PASSWORD', 'admin123')
    return users

LOGIN_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Đăng nhập – Thẩm định TGBC</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#1a3a5c 0%,#245080 100%);display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#fff;border-radius:14px;padding:36px 32px;width:100%;max-width:380px;box-shadow:0 8px 32px rgba(0,0,0,.25)}
.logo{text-align:center;margin-bottom:24px}
.logo-img{width:72px;height:72px;margin:0 auto 10px;display:block}
.logo h1{font-size:17px;color:#1a3a5c;font-weight:700;margin-top:4px;line-height:1.3}
.logo p{font-size:11px;color:#6b7280;margin-top:5px}
.divider{height:1px;background:#e5e7eb;margin:16px 0}
label{display:block;font-size:12px;font-weight:600;color:#374151;margin-bottom:4px}
input{width:100%;padding:9px 12px;border:1.5px solid #d1d5db;border-radius:6px;font-size:14px;margin-bottom:12px}
input:focus{outline:none;border-color:#1a3a5c}
button{width:100%;padding:11px;background:#1a3a5c;color:#fff;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;margin-top:4px}
button:hover{background:#245080}
.err{color:#dc2626;font-size:12px;margin-bottom:12px;padding:8px 10px;background:#fef2f2;border-radius:5px;border-left:3px solid #dc2626}
.foot{text-align:center;font-size:10px;color:#9ca3af;margin-top:14px}
</style>
</head>
<body>
<div class="box">
  <div class="logo">
    <svg class="logo-img" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
      <circle cx="36" cy="36" r="34" fill="#1a3a5c" stroke="#c8a84b" stroke-width="3"/>
      <text x="36" y="44" text-anchor="middle" font-size="28" fill="#c8a84b">🏛</text>
    </svg>
    <h1>Phần mềm Thẩm định<br>Tinh giản Biên chế</h1>
    <p>Sở Dân tộc và Tôn giáo tỉnh Lâm Đồng</p>
  </div>
  <div class="divider"></div>
  {% if error %}<div class="err">⚠ {{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <label>Tên đăng nhập</label>
    <input type="text" name="username" placeholder="Nhập tên đăng nhập" autocomplete="username" autofocus>
    <label>Mật khẩu</label>
    <input type="password" name="password" placeholder="Nhập mật khẩu" autocomplete="current-password">
    <button type="submit">🔐 Đăng nhập</button>
  </form>
  <div class="foot">Nghị định 154/2025/NĐ-CP · Hiệu lực 16/6/2025 – 31/12/2030</div>
</div>
</body>
</html>"""

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = load_users()
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        error = 'Tên đăng nhập hoặc mật khẩu không đúng.'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/whoami')
@login_required
def whoami():
    return jsonify({'username': session.get('username', 'admin')})

@app.route('/')
@login_required
def index():
    return send_from_directory('.', 'tgbc_app.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
