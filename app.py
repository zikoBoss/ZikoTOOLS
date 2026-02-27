from flask import Flask, request, render_template_string, session, redirect, url_for
import requests
import base64
import os
import urllib.parse
from functools import wraps
from datetime import datetime, timedelta
from io import BytesIO
import base64 as b64_encode
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# بيانات تسجيل الدخول من متغيرات البيئة
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
TEAM_NAME = "ZIKO-TEAM"

def get_api_url(uid, server_name):
    try:
        encoded_url = "aHR0cHM6Ly9kdXJhbnRvLWxpa2UtcGVhcmwudmVyY2VsLmFwcC9saWtlP3VpZD17dWlkfSZzZXJ2ZXJfbmFtZT17c2VydmVyX25hbWV9"
        decoded_url = base64.b64decode(encoded_url).decode()
        return decoded_url.format(uid=uid, server_name=server_name)
    except:
        return None

regions = {
    'me': {'ar': 'الشرق الأوسط', 'en': 'Middle East'},
    'eu': {'ar': 'أوروبا', 'en': 'Europe'},
    'us': {'ar': 'أمريكا الشمالية', 'en': 'North America'},
    'in': {'ar': 'الهند', 'en': 'India'},
    'br': {'ar': 'البرازيل', 'en': 'Brazil'},
    'id': {'ar': 'إندونيسيا', 'en': 'Indonesia'},
    'tr': {'ar': 'تركيا', 'en': 'Turkey'},
    'th': {'ar': 'تايلاند', 'en': 'Thailand'}
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def format_timestamp(timestamp):
    try:
        if timestamp and timestamp > 0:
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return "N/A"
    except:
        return "N/A"

def get_region_info(uid):
    """جلب معلومات المنطقة والاسم من API"""
    try:
        url = f"https://region-check-six.vercel.app/?uid={uid}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "nickname": data.get("nickname", "Unknown"),
                "region": data.get("region", "Unknown"),
                "error": None
            }
        return {"nickname": "Unknown", "region": "Unknown", "error": "API Error"}
    except Exception as e:
        return {"nickname": "Unknown", "region": "Unknown", "error": str(e)}

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ziko TOOLS Login</title>
    <style>
        body {
            background-color: black;
            color: red;
            font-family: 'Poppins', 'Arial', sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(45deg, #000000, #1a0000);
        }
        .login-container {
            max-width: 400px;
            width: 100%;
            background: rgba(26, 26, 26, 0.95);
            padding: 40px;
            border-radius: 20px;
            border: 2px solid red;
            box-shadow: 0 0 30px rgba(255,0,0,0.5);
            backdrop-filter: blur(10px);
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(255,0,0,0.5); }
            to { box-shadow: 0 0 40px rgba(255,0,0,0.8); }
        }
        h1 {
            color: red;
            font-size: 2.8em;
            margin-bottom: 5px;
            text-shadow: 0 0 15px red;
            letter-spacing: 2px;
        }
        .team-name {
            color: #ff6666;
            font-size: 1.2em;
            margin-bottom: 25px;
            font-weight: 300;
        }
        .input-group {
            margin-bottom: 20px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #ff4d4d;
            font-weight: bold;
            font-size: 0.95em;
            letter-spacing: 1px;
        }
        input {
            width: 100%;
            padding: 14px;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #ff3333;
            color: white;
            border-radius: 12px;
            font-size: 1em;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }
        input:focus {
            outline: none;
            border-color: white;
            box-shadow: 0 0 15px red;
            transform: scale(1.02);
        }
        button {
            background: linear-gradient(45deg, #ff0000, #cc0000);
            color: black;
            border: none;
            padding: 16px 30px;
            font-size: 1.3em;
            font-weight: bold;
            border-radius: 12px;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 20px;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        button:hover {
            background: linear-gradient(45deg, #cc0000, #990000);
            box-shadow: 0 0 25px red;
            transform: scale(1.05);
        }
        .error-message {
            color: #ff9999;
            background: rgba(51, 0, 0, 0.9);
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid red;
        }
        .social-icons {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333;
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        .social-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #1a1a1a;
            border: 2px solid red;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        .social-icon:hover {
            transform: scale(1.15);
            box-shadow: 0 0 25px red;
            background: red;
        }
        .social-icon:hover svg {
            fill: black;
        }
        .social-icon svg {
            width: 25px;
            height: 25px;
            fill: red;
            transition: all 0.3s ease;
        }
        .footer {
            margin-top: 20px;
            color: #666;
            font-size: 0.85em;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="login-container">
        <h1>WELCOME</h1>
        <div class="team-name">{{ team_name }}</div>
        
        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="input-group">
                <label>👤 USERNAME</label>
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            
            <div class="input-group">
                <label>🔑 PASSWORD</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            
            <button type="submit">▶ LOGIN</button>
        </form>
        
        <div class="social-icons">
            <a href="https://youtube.com/@ziko_boss?si=Te3gus_-91NNFkfP" target="_blank" class="social-icon" title="YouTube">
                <svg viewBox="0 0 24 24">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
            </a>
            <a href="https://t.me/Ziko_Tim" target="_blank" class="social-icon" title="Telegram">
                <svg viewBox="0 0 24 24">
                    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                </svg>
            </a>
        </div>
        
        <div class="footer">
            {{ team_name }}
        </div>
    </div>
</body>
</html>
"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{% if lang == 'ar' %}rtl{% else %}ltr{% endif %}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Ziko TOOLS - Free Fire</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            background: linear-gradient(135deg, #000000, #1a0000, #330000);
            color: #ff3333;
            font-family: 'Poppins', 'Arial', sans-serif;
            text-align: center;
            margin: 0;
            padding: 10px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            animation: gradientBG 15s ease infinite;
            background-size: 400% 400%;
        }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container {
            max-width: 100%;
            width: 100%;
            margin: auto;
            background: rgba(26, 26, 26, 0.95);
            padding: 60px 20px 20px 20px;
            border-radius: 20px;
            border: 2px solid #ff0000;
            box-shadow: 0 0 30px rgba(255,0,0,0.4);
            backdrop-filter: blur(10px);
            flex: 1;
            position: relative;
        }
        .logout-btn {
            position: absolute;
            top: 15px;
            {% if lang == 'ar' %}
            left: 15px;
            {% else %}
            right: 15px;
            {% endif %}
            background: transparent;
            color: #ff4d4d;
            border: 2px solid #ff3333;
            padding: 5px 12px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.75em;
            font-weight: 600;
            transition: 0.3s;
            z-index: 10;
        }
        .logout-btn:hover {
            background: #ff0000;
            color: black;
            box-shadow: 0 0 15px red;
        }
        .user-badge {
            position: absolute;
            top: 15px;
            {% if lang == 'ar' %}
            right: 15px;
            {% else %}
            left: 15px;
            {% endif %}
            color: #ff6666;
            font-size: 0.8em;
            border: 1px solid #ff3333;
            padding: 4px 10px;
            border-radius: 20px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
            font-weight: 500;
            max-width: 130px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            z-index: 10;
        }
        h1 {
            color: #ff1a1a;
            font-size: 2.2em;
            margin-top: 15px;
            margin-bottom: 2px;
            text-shadow: 0 0 15px #ff0000;
            letter-spacing: 2px;
            font-weight: 700;
            word-break: break-word;
        }
        .team-name {
            color: #ff6666;
            font-size: 1.1em;
            margin-bottom: 25px;
            font-weight: 300;
            letter-spacing: 1px;
        }
        .tabs {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        .tab-btn {
            background: transparent;
            color: #ff4d4d;
            border: 2px solid #ff3333;
            padding: 10px 12px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            transition: 0.3s;
            flex: 1 1 auto;
            min-width: 100px;
            max-width: 150px;
            backdrop-filter: blur(5px);
        }
        .tab-btn:hover, .tab-btn.active {
            background: linear-gradient(45deg, #ff0000, #cc0000);
            color: black;
            box-shadow: 0 0 15px red;
            transform: translateY(-2px);
        }
        .tab-content {
            display: none;
            animation: fadeIn 0.4s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .tab-content.active {
            display: block;
        }
        label {
            display: block;
            margin: 15px 0 5px;
            color: #ff4d4d;
            font-weight: 600;
            font-size: 0.9em;
            text-align: {% if lang == 'ar' %}right{% else %}left{% endif %};
        }
        input, select {
            width: 100%;
            padding: 14px;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #ff3333;
            color: white;
            border-radius: 15px;
            font-size: 1em;
            margin-bottom: 12px;
            transition: all 0.3s ease;
            -webkit-appearance: none;
            appearance: none;
        }
        input:focus, select:focus {
            outline: none;
            border-color: white;
            box-shadow: 0 0 15px red;
        }
        button {
            background: linear-gradient(45deg, #ff0000, #cc0000);
            color: black;
            border: none;
            padding: 15px 20px;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 40px;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 10px;
            width: 100%;
            letter-spacing: 1px;
            text-transform: uppercase;
            -webkit-tap-highlight-color: transparent;
        }
        button:hover, button:active {
            background: linear-gradient(45deg, #cc0000, #990000);
            box-shadow: 0 0 20px red;
            transform: scale(1.01);
        }
        .result-box {
            margin-top: 25px;
            padding: 18px;
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid #ff0000;
            border-radius: 18px;
            color: #ff4d4d;
            text-align: {% if lang == 'ar' %}right{% else %}left{% endif %};
            word-wrap: break-word;
            overflow-x: hidden;
        }
        .result-box pre {
            font-family: 'Courier New', monospace;
            color: white;
            background: #111;
            padding: 15px;
            border-radius: 12px;
            overflow-x: auto;
            border-left: 4px solid red;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-width: 100%;
            font-size: 0.9em;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .info-item {
            background: rgba(17, 17, 17, 0.95);
            padding: 12px;
            border-radius: 12px;
            border: 1px solid #ff3333;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        .info-label {
            color: #ff6666;
            font-size: 0.85em;
            margin-bottom: 5px;
        }
        .info-value {
            color: white;
            font-size: 1.1em;
            font-weight: 600;
            word-break: break-word;
        }
        .image-container {
            margin-top: 15px;
            text-align: center;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 18px;
            border: 2px solid #ff3333;
            width: 100%;
            overflow: hidden;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            border: 2px solid #ff0000;
            box-shadow: 0 0 20px rgba(255,0,0,0.4);
            transition: 0.3s;
            display: block;
            margin: 0 auto;
        }
        .image-container img:hover {
            transform: scale(1.01);
            box-shadow: 0 0 25px red;
        }
        .ban-safe {
            color: #00ff00;
            text-shadow: 0 0 8px #00ff00;
        }
        .ban-banned {
            color: #ff0000;
            text-shadow: 0 0 8px #ff0000;
        }
        .language-switch {
            margin: 15px 0;
        }
        .language-switch a {
            color: #ff6666;
            text-decoration: none;
            margin: 0 8px;
            font-weight: 600;
            font-size: 0.95em;
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid transparent;
            display: inline-block;
        }
        .language-switch a:hover {
            border-color: red;
            background: rgba(255,0,0,0.1);
        }
        .social-icons {
            margin-top: 25px;
            padding: 15px 0 5px;
            border-top: 2px solid #333;
            display: flex;
            justify-content: center;
            gap: 25px;
            flex-wrap: wrap;
        }
        .social-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            background: #1a1a1a;
            border: 2px solid #ff3333;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        .social-icon:hover, .social-icon:active {
            transform: scale(1.1);
            box-shadow: 0 0 20px red;
            background: #ff0000;
        }
        .social-icon:hover svg, .social-icon:active svg {
            fill: black;
        }
        .social-icon svg {
            width: 28px;
            height: 28px;
            fill: #ff3333;
            transition: all 0.2s ease;
        }
        .footer {
            margin-top: 20px;
            color: #666;
            font-size: 0.85em;
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 65px 15px 15px 15px;
            }
            
            h1 {
                font-size: 1.8em;
                margin-top: 15px;
            }
            
            .logout-btn {
                padding: 4px 10px;
                font-size: 0.7em;
                top: 12px;
            }
            
            .user-badge {
                max-width: 100px;
                font-size: 0.7em;
                padding: 3px 8px;
                top: 12px;
            }
            
            .team-name {
                margin-bottom: 20px;
                font-size: 1em;
            }
            
            .tab-btn {
                min-width: 80px;
                font-size: 0.8em;
                padding: 8px 6px;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (min-width: 481px) and (max-width: 768px) {
            .container {
                padding: 60px 20px 20px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout-btn">{% if lang == 'ar' %}⭕ خروج{% else %}⭕ LOGOUT{% endif %}</a>
        <div class="user-badge">{{ username }}</div>
        
        <h1>⚡Ziko TOOLS⚡️</h1>
        <div class="team-name">{{ team_name }}</div>

        <div class="language-switch">
            <a href="?lang=ar">🇸🇦 العربية</a> | <a href="?lang=en">🇬🇧 English</a>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('likes')">❤️ {% if lang == 'ar' %}إرسال لايكات{% else %}SEND LIKES{% endif %}</button>
            <button class="tab-btn" onclick="showTab('check')">🔍 {% if lang == 'ar' %}فحص الحظر{% else %}BAN CHECK{% endif %}</button>
            <button class="tab-btn" onclick="showTab('info')">📋 {% if lang == 'ar' %}معلومات الحساب{% else %}PLAYER INFO{% endif %}</button>
            <button class="tab-btn" onclick="showTab('outfit')">👕 {% if lang == 'ar' %}الأوتفيت{% else %}OUTFIT{% endif %}</button>
        </div>

        {% if error %}
        <div style="color: #ff9999; background: rgba(51, 0, 0, 0.9); padding: 12px; border-radius: 12px; margin-bottom: 20px; border: 1px solid red; font-size: 0.9em;">
            {{ error }}
        </div>
        {% endif %}

        <!-- Tab: Send Likes -->
        <div id="likes-tab" class="tab-content active">
            <form method="POST" action="/send_likes">
                <input type="hidden" name="lang" value="{{ lang }}">
                
                <label>{% if lang == 'ar' %}🆔 UID{% else %}🆔 UID{% endif %}</label>
                <input type="text" name="uid" placeholder="Your UID here" required>

                <label>{% if lang == 'ar' %}🌍 المنطقة{% else %}🌍 REGION{% endif %}</label>
                <select name="server">
                    {% for code, names in regions.items() %}
                    <option value="{{ code }}">{{ names[lang] }}</option>
                    {% endfor %}
                </select>

                <button type="submit">▶ {% if lang == 'ar' %}إرسال{% else %}SEND{% endif %}</button>
            </form>
        </div>

        <!-- Tab: Ban Check -->
        <div id="check-tab" class="tab-content">
            <form method="POST" action="/check_ban">
                <input type="hidden" name="lang" value="{{ lang }}">
                
                <label>{% if lang == 'ar' %}🆔 UID{% else %}🆔 UID{% endif %}</label>
                <input type="text" name="uid" placeholder="Your UID here" required>

                <button type="submit">▶ {% if lang == 'ar' %}فحص{% else %}CHECK{% endif %}</button>
            </form>
        </div>

        <!-- Tab: Player Info (مع البانر) -->
        <div id="info-tab" class="tab-content">
            <form method="POST" action="/player_info">
                <input type="hidden" name="lang" value="{{ lang }}">
                
                <label>{% if lang == 'ar' %}🆔 UID{% else %}🆔 UID{% endif %}</label>
                <input type="text" name="uid" placeholder="Your UID here" required>

                <button type="submit">▶ {% if lang == 'ar' %}جلب المعلومات{% else %}GET INFO{% endif %}</button>
            </form>
        </div>

        <!-- Tab: Get Outfit -->
        <div id="outfit-tab" class="tab-content">
            <form method="POST" action="/get_outfit">
                <input type="hidden" name="lang" value="{{ lang }}">
                
                <label>{% if lang == 'ar' %}🆔 UID{% else %}🆔 UID{% endif %}</label>
                <input type="text" name="uid" placeholder="Your UID here" required>

                <label>{% if lang == 'ar' %}🌍 المنطقة{% else %}🌍 REGION{% endif %}</label>
                <select name="region">
                    {% for code, names in regions.items() %}
                    <option value="{{ code }}">{{ names[lang] }}</option>
                    {% endfor %}
                </select>

                <button type="submit">▶ {% if lang == 'ar' %}جلب الأوتفيت{% else %}GET OUTFIT{% endif %}</button>
            </form>
        </div>

        {% if result %}
        <div class="result-box">
            {{ result|safe }}
        </div>
        {% endif %}

        <div class="social-icons">
            <a href="https://youtube.com/@ziko_boss?si=Te3gus_-91NNFkfP" target="_blank" class="social-icon" title="YouTube">
                <svg viewBox="0 0 24 24">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
            </a>
            <a href="https://t.me/Ziko_Tim" target="_blank" class="social-icon" title="Telegram">
                <svg viewBox="0 0 24 24">
                    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                </svg>
            </a>
        </div>
        
        <div class="footer">
            {{ team_name }}
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');
            
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        const urlParams = new URLSearchParams(window.location.search);
        const activeTab = urlParams.get('tab');
        if (activeTab) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.getElementById(activeTab + '-tab').classList.add('active');
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[onclick="showTab('${activeTab}')"]`).classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index', lang='en'))
        else:
            error = "❌ Invalid username or password"
            return render_template_string(LOGIN_TEMPLATE, team_name=TEAM_NAME, error=error)
    
    return render_template_string(LOGIN_TEMPLATE, team_name=TEAM_NAME, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET'])
@login_required
def index():
    lang = request.args.get('lang', 'ar')
    if lang not in ['ar', 'en']:
        lang = 'ar'
    return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, 
                                   lang=lang, error=None, result=None, username=session.get('username', ''))

@app.route('/send_likes', methods=['POST'])
@login_required
def send_likes():
    uid = request.form.get('uid', '').strip()
    server = request.form.get('server', 'me')
    lang = request.form.get('lang', 'ar')

    if not uid:
        error = "⚠️ الرجاء إدخال UID" if lang == 'ar' else "⚠️ Please enter UID"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

    api_url = get_api_url(uid, server)
    if not api_url:
        error = "❌ خطأ في النظام" if lang == 'ar' else "❌ System error"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()

        likes_given = data.get('LikesGivenByAPI', 0)
        likes_after = data.get('LikesafterCommand', 0)
        likes_before = data.get('LikesbeforeCommand', 0)
        player_nickname = data.get('PlayerNickname', 'Unknown')
        status = data.get('status', 0)

        if lang == 'ar':
            status_text = {0: "فشل", 1: "محدود", 2: "ناجح", 3: "مغلق"}.get(status, 'غير معروف')
            region_name = regions.get(server, {}).get('ar', server.upper())
        else:
            status_text = {0: "Failed", 1: "Limited", 2: "Success", 3: "Locked"}.get(status, 'Unknown')
            region_name = regions.get(server, {}).get('en', server.upper())

        result_lines = []
        result_lines.append(f"Player: {player_nickname}")
        result_lines.append(f"UID: {uid}")
        result_lines.append(f"Region: {region_name}")
        result_lines.append("")
        result_lines.append("Likes:")
        result_lines.append(f"  Before: {likes_before}")
        result_lines.append(f"  After: {likes_after}")
        result_lines.append(f"  Added: {likes_given}")
        result_lines.append("")
        result_lines.append(f"Status: {status_text}")

        if likes_given > 0:
            result_lines.append("")
            result_lines.append("Successfully added")
        elif status == 2:
            result_lines.append("")
            result_lines.append("Maximum limit reached")
        else:
            result_lines.append("")
            result_lines.append("Not added")

        result_text = "\n".join(result_lines)

        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=None, result=f"<pre>{result_text}</pre>", username=session.get('username', ''))

    except Exception as e:
        error = "❌ فشل الاتصال بالخادم" if lang == 'ar' else "❌ Connection failed"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

@app.route('/check_ban', methods=['POST'])
@login_required
def check_ban():
    uid = request.form.get('uid', '').strip()
    lang = request.form.get('lang', 'ar')

    if not uid:
        error = "⚠️ الرجاء إدخال UID" if lang == 'ar' else "⚠️ Please enter UID"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

    try:
        # استخدام API فحص الحظر المطلوب
        url = f"https://foubia-ban-check.vercel.app/bancheck?key=xTzPrO&uid={uid}"
        response = requests.get(url, timeout=10)
        data = response.json()

        # استخراج البيانات من الرد (بما يتوافق مع الرد الذي أعطيته)
        username = data.get('username', 'Unknown')
        uid_from_api = data.get('uid', uid)
        status = data.get('status', 'UNKNOWN')
        ban_period = data.get('ban_period', 0)
        is_banned = data.get('is_banned', False)
        
        # تنسيق النتيجة بالشكل المطلوب
        result_lines = []
        result_lines.append(f"✨ Result for UID: {uid}")
        result_lines.append("━━━━━━━━━━━━━━━")
        result_lines.append(f"username: {username}")
        result_lines.append(f"uid: {uid_from_api}")
        result_lines.append(f"status: {status}")
        result_lines.append(f"ban_period: {ban_period}")
        
        # عرض is_banned في النهاية
        if lang == 'ar':
            result_lines.append(f"is_banned: {'✅ لا' if not is_banned else '❌ نعم'}")
        else:
            result_lines.append(f"is_banned: {'✅ No' if not is_banned else '❌ Yes'}")
            
        result_lines.append("━━━━━━━━━━━━━━━")
        result_lines.append("💎 Powered by: @ZikoB0SS")

        result_text = "\n".join(result_lines)

        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=None, result=f"<pre>{result_text}</pre>", username=session.get('username', ''))

    except Exception as e:
        error = f"❌ خطأ: {str(e)}" if lang == 'ar' else f"❌ Error: {str(e)}"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

@app.route('/player_info', methods=['POST'])
@login_required
def player_info():
    uid = request.form.get('uid', '').strip()
    lang = request.form.get('lang', 'ar')

    if not uid:
        error = "⚠️ الرجاء إدخال UID" if lang == 'ar' else "⚠️ Please enter UID"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

    try:
        # 1. جلب معلومات اللاعب
        url = f"https://foubia-info-ff.vercel.app/{uid}"
        response = requests.get(url, timeout=10)
        data = response.json()

        basic = data.get("basicinfo", [{}])[0]
        clan = data.get("claninfo", [{}])[0]
        clan_admin = data.get("clanadmin", [{}])[0]

        player_name = basic.get('username', 'Unknown')
        player_level = basic.get('level', '1')
        guild_name = clan.get('clanname', '')

        # 2. القيم الثابتة للبانر
        AVATAR_ID = "902028017"
        BANNER_ID = "901043008"
        PIN_ID = "0"
        PRIME_LEVEL = "1"

        # 3. بناء رابط البانر مع ترميز الاسم
        encoded_name = urllib.parse.quote(player_name)
        encoded_guild = urllib.parse.quote(guild_name) if guild_name else ""
        
        banner_url = (f"https://banner-apibykala-api.vercel.app/profile"
                      f"?avatar_id={AVATAR_ID}"
                      f"&banner_id={BANNER_ID}"
                      f"&pin_id={PIN_ID}"
                      f"&prime_level={PRIME_LEVEL}"
                      f"&level={player_level}"
                      f"&name={encoded_name}"
                      f"&guild={encoded_guild}")

        # 4. تنسيق التواريخ
        last_login = format_timestamp(basic.get('lastlogin', 0))
        create_at = format_timestamp(basic.get('createat', 0))

        # 5. بناء HTML النتيجة مع البانر
        result_html = f"""
<div style="font-family: 'Courier New', monospace;">
    <h4 style="color: red; text-align: center;">{'معلومات اللاعب' if lang == 'ar' else 'Player Information'}</h4>
    
    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: red; margin: 0 0 10px 0;">{'المعلومات الأساسية' if lang == 'ar' else 'Basic Info'}</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">{'الاسم' if lang == 'ar' else 'Name'}</div>
                <div class="info-value" style="word-break: break-all;">{basic.get('username', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'المستوى' if lang == 'ar' else 'Level'}</div>
                <div class="info-value">{basic.get('level', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'الخبرة' if lang == 'ar' else 'Exp'}</div>
                <div class="info-value">{basic.get('Exp', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">BR</div>
                <div class="info-value">{basic.get('brrankscore', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">CS</div>
                <div class="info-value">{basic.get('csrankscore', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'الإعجابات' if lang == 'ar' else 'Likes'}</div>
                <div class="info-value">{basic.get('likes', 0):,}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'المنطقة' if lang == 'ar' else 'Region'}</div>
                <div class="info-value">{basic.get('region', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'السيرة' if lang == 'ar' else 'Bio'}</div>
                <div class="info-value" style="word-break: break-all;">{basic.get('bio', 'N/A')}</div>
            </div>
        </div>
    </div>

    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: red; margin: 0 0 10px 0;">{'التواريخ' if lang == 'ar' else 'Dates'}</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">{'تاريخ الإنشاء' if lang == 'ar' else 'Created'}</div>
                <div class="info-value">{create_at}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'آخر دخول' if lang == 'ar' else 'Last Login'}</div>
                <div class="info-value">{last_login}</div>
            </div>
        </div>
    </div>

    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: red; margin: 0 0 10px 0;">{'معلومات العشيرة' if lang == 'ar' else 'Guild Info'}</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">{'اسم العشيرة' if lang == 'ar' else 'Guild Name'}</div>
                <div class="info-value" style="word-break: break-all;">{clan.get('clanname', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'مستوى العشيرة' if lang == 'ar' else 'Guild Level'}</div>
                <div class="info-value">{clan.get('guildlevel', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'الأعضاء' if lang == 'ar' else 'Members'}</div>
                <div class="info-value">{clan.get('livemember', 'N/A')}</div>
            </div>
        </div>
    </div>

    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: red; margin: 0 0 10px 0;">{'أدمن العشيرة' if lang == 'ar' else 'Guild Admin'}</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">{'الاسم' if lang == 'ar' else 'Name'}</div>
                <div class="info-value" style="word-break: break-all;">{clan_admin.get('adminname', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'المستوى' if lang == 'ar' else 'Level'}</div>
                <div class="info-value">{clan_admin.get('level', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">{'الخبرة' if lang == 'ar' else 'Exp'}</div>
                <div class="info-value">{clan_admin.get('exp', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">BR</div>
                <div class="info-value">{clan_admin.get('brpoint', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">CS</div>
                <div class="info-value">{clan_admin.get('cspoint', 'N/A')}</div>
            </div>
        </div>
    </div>

    <div style="margin-top: 30px; text-align: center;">
        <h5 style="color: red;">{'بانر اللاعب' if lang == 'ar' else 'Player Banner'}</h5>
        <div class="image-container">
            <img src="{banner_url}" alt="Player Banner" style="max-width: 100%; height: auto;" onerror="this.onerror=null; this.src=''; this.parentNode.innerHTML+='<p style=\'color:#ff6666;\'>⚠️ {'فشل تحميل البانر' if lang == 'ar' else 'Banner load failed'}</p>'">
            <p style="color: #888; font-size: 0.8em; margin-top: 8px;">
                {'تم التوليد تلقائياً' if lang == 'ar' else 'Auto-generated'}
            </p>
        </div>
    </div>

    <div style="margin-top: 15px; color: #888; font-size: 0.9em; text-align: center;">
        💎 ZIKO-TEAM
    </div>
</div>
"""

        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=None, result=result_html, username=session.get('username', ''))

    except Exception as e:
        error = f"❌ خطأ: {str(e)}" if lang == 'ar' else f"❌ Error: {str(e)}"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

@app.route('/get_outfit', methods=['POST'])
@login_required
def get_outfit():
    uid = request.form.get('uid', '').strip()
    region = request.form.get('region', 'ind').strip().lower()
    lang = request.form.get('lang', 'ar')

    if not uid:
        error = "⚠️ الرجاء إدخال UID" if lang == 'ar' else "⚠️ Please enter UID"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

    try:
        # جلب معلومات اللاعب أولاً (للاسم)
        region_info = get_region_info(uid)
        
        # بناء رابط الأوتفيت بالمفتاح 99day
        outfit_url = f"https://ffoutfitapis.vercel.app/outfit-image?uid={uid}&region={region}&key=99day"
        
        # جلب الصورة
        response = requests.get(outfit_url, timeout=15)
        
        if response.status_code != 200:
            error_msg = "❌ فشل جلب الأوتفيت. تأكد من UID والمنطقة." if lang == 'ar' else "❌ Failed to fetch outfit. Check UID and region."
            return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                           error=error_msg, result=None, username=session.get('username', ''))
        
        # تحويل الصورة إلى base64 لعرضها في HTML
        image_base64 = b64_encode.b64encode(response.content).decode('utf-8')
        image_data = f"data:image/png;base64,{image_base64}"
        
        # إنشاء HTML لعرض الصورة بشكل متجاوب مع الهاتف
        result_html = f"""
<div style="text-align: center;">
    <h4 style="color: red;">{'👕 أوتفيت اللاعب' if lang == 'ar' else '👕 Player Outfit'}</h4>
    <div style="background: #111; padding: 15px; border-radius: 15px; margin: 10px 0;">
        <div style="margin: 8px 0; color: #ff6666; font-size: 0.95rem; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
            <span>👤 {'الاسم' if lang == 'ar' else 'Name'}: <span style="color: white; font-weight: bold;">{region_info.get('nickname', 'Unknown')}</span></span>
            <span>🆔 UID: <span style="color: white; font-weight: bold;">{uid}</span></span>
            <span>🌍 {'المنطقة' if lang == 'ar' else 'Region'}: <span style="color: white; font-weight: bold;">{region.upper()}</span></span>
        </div>
        <div class="image-container">
            <img src="{image_data}" alt="Player Outfit" style="max-width: 100%; height: auto; border-radius: 15px;">
        </div>
    </div>
    <div style="margin-top: 10px; color: #888; font-size: 0.85rem;">
        💎 ZIKO-TEAM
    </div>
</div>
"""
        
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=None, result=result_html, username=session.get('username', ''))
        
    except Exception as e:
        error = f"❌ خطأ: {str(e)}" if lang == 'ar' else f"❌ Error: {str(e)}"
        return render_template_string(MAIN_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=error, result=None, username=session.get('username', ''))

# للتشغيل على Vercel
app = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)