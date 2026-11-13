import os
from functools import wraps
from flask import Flask, request, session, redirect, url_for, send_from_directory, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'thay-bang-chuoi-ngau-nhien')

PASSWORD = os.environ.get('APP_PASSWORD', 'admin123')

LOGIN_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Đăng nhập – Thẩm định TGBC</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f4f6f9;display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#fff;border-radius:12px;padding:36px 32px;width:100%;max-width:360px;box-shadow:0 4px 24px rgba(0,0,0,.12)}
.logo{text-align:center;margin-bottom:24px}
.logo h1{font-size:18px;color:#1a3a5c;font-weight:700;margin-top:8px}
.logo p{font-size:11px;color:#6b7280;margin-top:4px}
label{display:block;font-size:12px;font-weight:600;color:#374151;margin-bottom:4px}
input[type=password]{width:100%;padding:9px 12px;border:1.5px solid #d1d5db;border-radius:6px;font-size:14px;margin-bottom:16px}
input:focus{outline:none;border-color:#1a3a5c}
button{width:100%;padding:10px;background:#1a3a5c;color:#fff;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer}
button:hover{background:#245080}
.err{color:#dc2626;font-size:12px;margin-bottom:12px;padding:8px;background:#fef2f2;border-radius:5px}
</style>
</head>
<body>
<div class="box">
  <div class="logo">
    <div style="font-size:40px">🏛</div>
    <h1>Phần mềm Thẩm định TGBC</h1>
    <p>Nghị định 154/2025/NĐ-CP · Sở Nội vụ Lâm Đồng</p>
  </div>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <label>Mật khẩu đăng nhập</label>
    <input type="password" name="password" placeholder="Nhập mật khẩu" autofocus>
    <button type="submit">Đăng nhập</button>
  </form>
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
        if request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        error = 'Mật khẩu không đúng. Vui lòng thử lại.'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return send_from_directory('.', 'tgbc_app.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
