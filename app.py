from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
import requests
import base64
import os
import urllib.parse
import json
import re
import random
from functools import wraps
from datetime import datetime, timedelta
from io import BytesIO
import base64 as b64_encode
from dotenv import load_dotenv
import jwt

# تحميل المتغيرات من ملف .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# بيانات تسجيل الدخول من متغيرات البيئة
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
TEAM_NAME = "ZIKO-TEAM"

# قنوات المطور
YOUTUBE_URL = "https://youtube.com/@ziko_boss?si=dhuL5-voIabSYdI0"
TELEGRAM_URL = "https://t.me/Ziko_Tim"
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61586247175238"
DEVELOPER = "@ZikoBOSS"

# المفتاح السري للـ JWT (نفسه في الموقع المتقدم)
JWT_SECRET = os.getenv('JWT_SECRET', 'ziko_advanced_secret_key_2026')

# ==================== دوال تزخريف الأسماء ====================
SYMBOLS = [
    "★","✦","✧","♛","♞","✪","✫","✬","✯","✾","✿","❀","♚",
    "⚔","⚜","♫","♪","✤","✥","⍟","➤","➣","☽","☄","☇","☉",
    "☢","☣","☠","☤","☥","☨","☬","☭","☯","⚚","⚝","⚕","⚘","⚛","⚚","𓂀","𓂻","𓋹","𓆩","𓆪","𖤍"
]

FONTS = [
    str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"),
    str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"),
    str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"),
    str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"),
    str.maketrans("abcdefghijklmnopqrstuvwxyz", "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
]

def generate_styles(name):
    """توليد 32 تصميم مختلف للاسم"""
    output = []
    name = name.lower()
    
    for _ in range(32):
        font = random.choice(FONTS)
        left = random.choice(SYMBOLS)
        right = random.choice(SYMBOLS)
        styled = name.translate(font)
        output.append(f"{left} {styled} {right}")
    
    return output

# ==================== دوال المساعدة الأساسية ====================
def get_api_url(uid, server_name):
    try:
        encoded_url = "aHR0cHM6Ly9kdXJhbnRvLWxpa2UtcGVhcmwudmVyY2VsLmFwcC9saWtlP3VpZD17dWlkfSZzZXJ2ZXJfbmFtZT17c2VydmVyX25hbWV9"
        decoded_url = base64.b64decode(encoded_url).decode()
        return decoded_url.format(uid=uid, server_name=server_name)
    except:
        return None

regions = {
    'me': 'Middle East',
    'eu': 'Europe',
    'us': 'North America',
    'in': 'India',
    'br': 'Brazil',
    'id': 'Indonesia',
    'tr': 'Turkey',
    'th': 'Thailand'
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

def extract_guest_data(file_content):
    """استخراج معلومات حساب الضيف من الملف"""
    try:
        text = file_content.decode('utf-8')
        
        try:
            data = json.loads(text)
        except:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                return {"success": False, "error": "Invalid JSON format"}
        
        if "guest_account_info" in data:
            guest_info = data["guest_account_info"]
            uid = guest_info.get("com.garena.msdk.guest_uid")
            password = guest_info.get("com.garena.msdk.guest_password")
            
            if uid and password:
                return {
                    "success": True, 
                    "uid": str(uid).strip(), 
                    "password": str(password).strip()
                }
        
        uid = data.get("com.garena.msdk.guest_uid") or data.get("uid")
        password = data.get("com.garena.msdk.guest_password") or data.get("password")
        
        if uid and password:
            return {
                "success": True, 
                "uid": str(uid).strip(), 
                "password": str(password).strip()
            }
        
        return {"success": False, "error": "Could not find UID and password in file"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== قوالب HTML ====================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ziko TOOLS - Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-card {
            max-width: 420px;
            width: 100%;
            background: rgba(18, 18, 18, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 59, 59, 0.2);
            border-radius: 24px;
            padding: 40px 30px;
            box-shadow: 0 20px 40px rgba(255, 0, 0, 0.15);
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .welcome-text {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .welcome-text h1 {
            color: #ff3b3b;
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        
        .welcome-text p {
            color: #ff6b6b;
            font-size: 0.95rem;
            font-weight: 400;
            opacity: 0.9;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            color: #ff6b6b;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 6px;
            letter-spacing: 0.5px;
        }
        
        .input-group input {
            width: 100%;
            padding: 14px 16px;
            background: rgba(0, 0, 0, 0.3);
            border: 1.5px solid rgba(255, 59, 59, 0.3);
            border-radius: 12px;
            color: #fff;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        
        .input-group input:focus {
            outline: none;
            border-color: #ff3b3b;
            box-shadow: 0 0 0 3px rgba(255, 59, 59, 0.1);
        }
        
        .input-group input::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }
        
        .login-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #ff3b3b, #cc0000);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
            letter-spacing: 1px;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255, 59, 59, 0.3);
        }
        
        .error-message {
            background: rgba(255, 59, 59, 0.1);
            border: 1px solid rgba(255, 59, 59, 0.3);
            border-radius: 10px;
            padding: 12px;
            color: #ff6b6b;
            font-size: 0.9rem;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.8rem;
        }
        
        .footer a {
            color: #ff6b6b;
            text-decoration: none;
            font-weight: 500;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="welcome-text">
            <h1>WELCOME</h1>
            <p>{{ team_name }}</p>
        </div>
        
        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="input-group">
                <label>USERNAME</label>
                <input type="text" name="username" placeholder="Enter your username" required>
            </div>
            
            <div class="input-group">
                <label>PASSWORD</label>
                <input type="password" name="password" placeholder="Enter your password" required>
            </div>
            
            <button type="submit" class="login-btn">SIGN IN</button>
        </form>
        
        <div class="footer">
            {{ team_name }} · <a href="https://t.me/Ziko_Tim" target="_blank">@ZikoBOSS</a>
        </div>
    </div>
</body>
</html>
"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Ziko TOOLS - Free Fire</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 80px 20px 40px;
            position: relative;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: #ff3b3b;
            margin-bottom: 4px;
            letter-spacing: 1px;
            text-shadow: 0 0 20px rgba(255, 59, 59, 0.3);
        }
        
        .header .team {
            color: #ff9b9b;
            font-size: 1rem;
            font-weight: 400;
            opacity: 0.9;
        }
        
        .header .user-badge {
            margin-top: 12px;
            display: inline-block;
            padding: 6px 16px;
            background: rgba(255, 59, 59, 0.1);
            border: 1px solid rgba(255, 59, 59, 0.2);
            border-radius: 30px;
            color: #ff9b9b;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .logout-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: transparent;
            color: #ff4d4d;
            border: 2px solid #ff3333;
            padding: 8px 16px;
            border-radius: 30px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            transition: 0.3s;
        }
        
        .logout-btn:hover {
            background: #ff0000;
            color: black;
            box-shadow: 0 0 15px red;
        }
        
        .advanced-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            background: linear-gradient(135deg, #0099ff, #0066cc);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .advanced-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 153, 255, 0.4);
        }
        
        .advanced-btn i {
            font-size: 1rem;
        }
        
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .tab-btn {
            background: transparent;
            border: 1.5px solid rgba(255, 59, 59, 0.2);
            color: #ff9b9b;
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .tab-btn:hover {
            border-color: #ff3b3b;
            color: #ff3b3b;
            transform: translateY(-2px);
        }
        
        .tab-btn.active {
            background: #ff3b3b;
            border-color: #ff3b3b;
            color: #000;
            font-weight: 600;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.4s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            color: #ff9b9b;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .form-control {
            width: 100%;
            padding: 14px 16px;
            background: rgba(0, 0, 0, 0.3);
            border: 1.5px solid rgba(255, 59, 59, 0.2);
            border-radius: 12px;
            color: #fff;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #ff3b3b;
            box-shadow: 0 0 0 3px rgba(255, 59, 59, 0.1);
        }
        
        select.form-control {
            cursor: pointer;
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #ff3b3b, #cc0000);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 59, 59, 0.3);
        }
        
        .result-box {
            margin-top: 30px;
            padding: 20px;
            background: rgba(18, 18, 18, 0.8);
            border: 1px solid rgba(255, 59, 59, 0.2);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        
        .result-box pre {
            font-family: 'Inter', monospace;
            color: #ff9b9b;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        
        .info-item {
            background: rgba(0, 0, 0, 0.3);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 59, 59, 0.2);
        }
        
        .info-label {
            color: #ff9b9b;
            font-size: 0.8rem;
            margin-bottom: 4px;
        }
        
        .info-value {
            color: white;
            font-size: 1rem;
            font-weight: 600;
            word-break: break-word;
        }
        
        .image-container {
            margin-top: 15px;
            text-align: center;
        }
        
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            border: 2px solid #ff3b3b;
        }
        
        .credential-item {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 59, 59, 0.2);
            border-radius: 12px;
            padding: 12px;
            margin: 12px 0;
        }
        
        .credential-label {
            color: #ff9b9b;
            font-size: 0.8rem;
            margin-bottom: 5px;
            text-align: left;
        }
        
        .credential-value {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }
        
        .copy-btn {
            background: transparent;
            border: 1px solid #ff3b3b;
            color: #ff3b3b;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 3px;
            white-space: nowrap;
            transition: all 0.3s ease;
        }
        
        .copy-btn:hover {
            background: #ff3b3b;
            color: black;
        }
        
        .copy-btn i {
            font-size: 0.6rem;
        }
        
        .style-item {
            background: rgba(0,0,0,0.3);
            margin: 6px 0;
            padding: 8px 12px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .style-item:hover {
            background: rgba(255, 59, 59, 0.1);
        }
        
        .style-text {
            color: #ff9b9b;
            font-size: 1rem;
            flex: 1;
            font-family: monospace;
        }
        
        .style-copy-btn {
            background: transparent;
            border: none;
            color: #ff3b3b;
            padding: 4px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 2px;
            opacity: 0.5;
            transition: all 0.3s ease;
        }
        
        .style-item:hover .style-copy-btn {
            opacity: 1;
        }
        
        .style-copy-btn:hover {
            background: #ff3b3b;
            color: black;
            opacity: 1;
        }
        
        .style-copy-btn i {
            font-size: 0.6rem;
        }
        
        .error-message {
            background: rgba(255, 59, 59, 0.1);
            border: 1px solid rgba(255, 59, 59, 0.3);
            border-radius: 12px;
            padding: 15px;
            color: #ff6b6b;
            font-size: 0.9rem;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .social-links {
            margin-top: 40px;
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        
        .social-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(255, 59, 59, 0.1);
            border: 2px solid #ff3b3b;
            color: #ff3b3b;
            font-size: 1.5rem;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        
        .social-link:hover {
            background: #ff3b3b;
            color: black;
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(255, 59, 59, 0.5);
        }
        
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.85rem;
        }
        
        .footer a {
            color: #ff6b6b;
            text-decoration: none;
            font-weight: 500;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 90px 15px 30px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .tab-btn {
                padding: 8px 16px;
                font-size: 0.85rem;
            }
            
            .advanced-btn {
                top: 15px;
                left: 15px;
                padding: 6px 12px;
                font-size: 0.75rem;
            }
            
            .logout-btn {
                top: 15px;
                right: 15px;
                padding: 6px 12px;
                font-size: 0.75rem;
            }
            
            .credential-value {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .copy-btn {
                width: 100%;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout-btn">LOGOUT</a>
        <a href="/advanced-tools" class="advanced-btn">
            <i class="fas fa-crown"></i> ADVANCED TOOLS
        </a>
        
        <div class="header">
            <h1>⚡Ziko TOOLS⚡️</h1>
            <div class="team">{{ team_name }}</div>
            <div class="user-badge">
                <i class="fas fa-user"></i> {{ username }}
            </div>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('likes')"><i class="fas fa-heart"></i> SEND LIKES</button>
            <button class="tab-btn" onclick="showTab('check')"><i class="fas fa-shield-alt"></i> BAN CHECK</button>
            <button class="tab-btn" onclick="showTab('info')"><i class="fas fa-info-circle"></i> PLAYER INFO</button>
            <button class="tab-btn" onclick="showTab('outfit')"><i class="fas fa-tshirt"></i> OUTFIT</button>
            <button class="tab-btn" onclick="showTab('guest')"><i class="fas fa-file-import"></i> GUEST FILE</button>
            <button class="tab-btn" onclick="showTab('nick')"><i class="fas fa-pen-fancy"></i> NICK STYLER</button>
        </div>

        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        <!-- Tab: Send Likes -->
        <div id="likes-tab" class="tab-content active">
            <form onsubmit="handleFormSubmit(event, 'send_likes')">
                <div class="form-group">
                    <label><i class="fas fa-fingerprint"></i> UID</label>
                    <input type="text" name="uid" class="form-control" placeholder="Enter UID" required>
                </div>
                
                <div class="form-group">
                    <label><i class="fas fa-globe"></i> REGION</label>
                    <select name="server" class="form-control">
                        {% for code, name in regions.items() %}
                        <option value="{{ code }}">{{ name }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <button type="submit" class="btn">
                    <i class="fas fa-paper-plane"></i> SEND LIKES
                </button>
            </form>
        </div>

        <!-- Tab: Ban Check -->
        <div id="check-tab" class="tab-content">
            <form onsubmit="handleFormSubmit(event, 'check_ban')">
                <div class="form-group">
                    <label><i class="fas fa-fingerprint"></i> UID</label>
                    <input type="text" name="uid" class="form-control" placeholder="Enter UID" required>
                </div>
                
                <button type="submit" class="btn">
                    <i class="fas fa-shield-alt"></i> CHECK BAN
                </button>
            </form>
        </div>

        <!-- Tab: Player Info -->
        <div id="info-tab" class="tab-content">
            <form onsubmit="handleFormSubmit(event, 'player_info')">
                <div class="form-group">
                    <label><i class="fas fa-fingerprint"></i> UID</label>
                    <input type="text" name="uid" class="form-control" placeholder="Enter UID" required>
                </div>
                
                <button type="submit" class="btn">
                    <i class="fas fa-info-circle"></i> GET INFO
                </button>
            </form>
        </div>

        <!-- Tab: Outfit -->
        <div id="outfit-tab" class="tab-content">
            <form onsubmit="handleFormSubmit(event, 'get_outfit')">
                <div class="form-group">
                    <label><i class="fas fa-fingerprint"></i> UID</label>
                    <input type="text" name="uid" class="form-control" placeholder="Enter UID" required>
                </div>
                
                <div class="form-group">
                    <label><i class="fas fa-globe"></i> REGION</label>
                    <select name="region" class="form-control">
                        <option value="ind">India</option>
                        <option value="me">Middle East</option>
                        <option value="br">Brazil</option>
                        <option value="id">Indonesia</option>
                        <option value="tr">Turkey</option>
                        <option value="th">Thailand</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">
                    <i class="fas fa-tshirt"></i> GET OUTFIT
                </button>
            </form>
        </div>

        <!-- Tab: Guest File -->
        <div id="guest-tab" class="tab-content">
            <form onsubmit="handleFormSubmit(event, 'extract_guest')" enctype="multipart/form-data">
                <div class="form-group">
                    <label><i class="fas fa-file-import"></i> GUEST FILE</label>
                    <input type="file" name="guest_file" class="form-control" accept=".dat,.txt,.json" required>
                    <small style="color: #ff9b9b; display: block; margin-top: 5px;">Supported: .dat, .txt, .json</small>
                </div>
                
                <button type="submit" class="btn">
                    <i class="fas fa-file-import"></i> EXTRACT DATA
                </button>
            </form>
            
            <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                <p style="color: #ff9b9b; font-size: 0.9rem;">📁 Expected format:</p>
                <pre style="background: #111; padding: 10px; border-radius: 5px; color: #ff6666; overflow-x: auto;">{
  "guest_account_info": {
    "com.garena.msdk.guest_password": "...",
    "com.garena.msdk.guest_uid": "..."
  }
}</pre>
            </div>
        </div>

        <!-- Tab: Nick Styler -->
        <div id="nick-tab" class="tab-content">
            <form onsubmit="handleFormSubmit(event, 'style_nick')">
                <div class="form-group">
                    <label><i class="fas fa-font"></i> NAME</label>
                    <input type="text" name="name" class="form-control" placeholder="Enter your name" required>
                    <small style="color: #ff9b9b; display: block; margin-top: 5px;">Generate 32 unique stylish designs</small>
                </div>
                
                <button type="submit" class="btn">
                    <i class="fas fa-magic"></i> GENERATE STYLES
                </button>
            </form>
        </div>

        <div id="result-container"></div>

        <div class="social-links">
            <a href="{{ youtube_url }}" target="_blank" class="social-link" title="YouTube">
                <i class="fab fa-youtube"></i>
            </a>
            <a href="{{ telegram_url }}" target="_blank" class="social-link" title="Telegram">
                <i class="fab fa-telegram"></i>
            </a>
            <a href="{{ facebook_url }}" target="_blank" class="social-link" title="Facebook">
                <i class="fab fa-facebook-f"></i>
            </a>
        </div>

        <div class="footer">
            {{ team_name }} · <a href="https://t.me/Ziko_Tim" target="_blank">{{ developer }}</a>
        </div>
    </div>

    <script>
        let currentTab = 'likes';
        
        function showTab(tabName) {
            currentTab = tabName;
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');
            
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        async function handleFormSubmit(event, endpoint) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            
            const resultDiv = document.getElementById('result-container');
            resultDiv.innerHTML = `
                <div class="result-box" style="text-align: center; padding: 30px;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 2.5rem; color: #ff3b3b;"></i>
                    <p style="margin-top: 15px; color: #ff9b9b;">Processing your request...</p>
                </div>
            `;
            
            try {
                const response = await fetch(`/${endpoint}`, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `<div class="result-box">${data.result}</div>`;
                } else {
                    resultDiv.innerHTML = `
                        <div class="error-message">
                            <i class="fas fa-exclamation-triangle"></i> ${data.error}
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i> Connection Error: ${error.message}
                    </div>
                `;
            }
            
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return false;
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                const toast = document.createElement('div');
                toast.style.cssText = `
                    position: fixed;
                    top: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: #ff3b3b;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 30px;
                    font-size: 0.9rem;
                    z-index: 2000;
                    animation: fadeInOut 2s ease;
                `;
                toast.innerHTML = '<i class="fas fa-check-circle"></i> Copied!';
                document.body.appendChild(toast);
                
                setTimeout(() => toast.remove(), 2000);
            }).catch(() => alert('Copy failed'));
        }
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInOut {
                0% { opacity: 0; transform: translate(-50%, -20px); }
                15% { opacity: 1; transform: translate(-50%, 0); }
                85% { opacity: 1; transform: translate(-50%, 0); }
                100% { opacity: 0; transform: translate(-50%, -20px); }
            }
        `;
        document.head.appendChild(style);
        
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

# ==================== Routes ====================
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
            return redirect(url_for('index'))
        else:
            error = "❌ Invalid username or password"
            return render_template_string(LOGIN_TEMPLATE, team_name=TEAM_NAME, error=error)
    
    return render_template_string(LOGIN_TEMPLATE, team_name=TEAM_NAME, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def index():
    return render_template_string(MAIN_TEMPLATE, 
                                 team_name=TEAM_NAME, 
                                 regions=regions,
                                 username=session.get('username', ''),
                                 developer=DEVELOPER,
                                 youtube_url=YOUTUBE_URL,
                                 telegram_url=TELEGRAM_URL,
                                 facebook_url=FACEBOOK_URL)

@app.route('/advanced-tools')
@login_required
def go_to_advanced():
    """توجيه المستخدم إلى الموقع المتقدم مع توكن JWT"""
    try:
        # إنشاء توكن صالح لمدة 10 دقائق
        token = jwt.encode({
            'user_id': session.get('username'),
            'exp': datetime.utcnow() + timedelta(minutes=10),
            'source': 'ziko-main'
        }, JWT_SECRET, algorithm='HS256')
        
        # توجيه المستخدم للموقع المتقدم (غير الرابط حسب موقعك)
        advanced_url = f"https://ziko-tools-rs7b.vercel.app?token={token}"
        return redirect(advanced_url)
        
    except Exception as e:
        return render_template_string(MAIN_TEMPLATE, 
                                     team_name=TEAM_NAME, 
                                     regions=regions,
                                     username=session.get('username', ''),
                                     developer=DEVELOPER,
                                     youtube_url=YOUTUBE_URL,
                                     telegram_url=TELEGRAM_URL,
                                     facebook_url=FACEBOOK_URL,
                                     error=f"Error accessing advanced tools: {str(e)}")

@app.route('/send_likes', methods=['POST'])
@login_required
def send_likes():
    uid = request.form.get('uid', '').strip()
    server = request.form.get('server', 'me')

    if not uid:
        return jsonify({"success": False, "error": "Please enter UID"})

    api_url = get_api_url(uid, server)
    if not api_url:
        return jsonify({"success": False, "error": "System error"})

    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()

        likes_given = data.get('LikesGivenByAPI', 0)
        likes_after = data.get('LikesafterCommand', 0)
        likes_before = data.get('LikesbeforeCommand', 0)
        player_nickname = data.get('PlayerNickname', 'Unknown')
        status = data.get('status', 0)

        status_text = {0: "Failed", 1: "Limited", 2: "Success", 3: "Locked"}.get(status, 'Unknown')
        region_name = regions.get(server, server.upper())

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
            result_lines.append("✅ Successfully added")
        elif status == 2:
            result_lines.append("")
            result_lines.append("ℹ️ Maximum limit reached")
        else:
            result_lines.append("")
            result_lines.append("❌ Not added")

        result_text = "\n".join(result_lines)

        return jsonify({"success": True, "result": f"<pre>{result_text}</pre>"})

    except Exception as e:
        return jsonify({"success": False, "error": f"Connection failed: {str(e)}"})

@app.route('/check_ban', methods=['POST'])
@login_required
def check_ban():
    uid = request.form.get('uid', '').strip()

    if not uid:
        return jsonify({"success": False, "error": "Please enter UID"})

    try:
        url = f"https://foubia-ban-check.vercel.app/bancheck?key=xTzPrO&uid={uid}"
        response = requests.get(url, timeout=10)
        data = response.json()

        username = data.get('username', 'Unknown')
        uid_from_api = data.get('uid', uid)
        status = data.get('status', 'UNKNOWN')
        ban_period = data.get('ban_period', 0)
        is_banned = data.get('is_banned', False)
        
        result_lines = []
        result_lines.append(f"✨ Result for UID: {uid}")
        result_lines.append("━━━━━━━━━━━━━━━")
        result_lines.append(f"username: {username}")
        result_lines.append(f"uid: {uid_from_api}")
        result_lines.append(f"status: {status}")
        result_lines.append(f"ban_period: {ban_period}")
        result_lines.append(f"is_banned: {'✅ No' if not is_banned else '❌ Yes'}")
        result_lines.append("━━━━━━━━━━━━━━━")
        result_lines.append(f"💎 Powered by: @ZikoBOSS")

        result_text = "\n".join(result_lines)

        return jsonify({"success": True, "result": f"<pre>{result_text}</pre>"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/player_info', methods=['POST'])
@login_required
def player_info():
    uid = request.form.get('uid', '').strip()

    if not uid:
        return jsonify({"success": False, "error": "Please enter UID"})

    try:
        url = f"https://foubia-info-ff.vercel.app/{uid}"
        response = requests.get(url, timeout=10)
        data = response.json()

        basic = data.get("basicinfo", [{}])[0]
        clan = data.get("claninfo", [{}])[0]
        clan_admin = data.get("clanadmin", [{}])[0]

        player_name = basic.get('username', 'Unknown')
        player_level = basic.get('level', '1')
        guild_name = clan.get('clanname', '')

        AVATAR_ID = "902028017"
        BANNER_ID = "901043008"
        PIN_ID = "0"
        PRIME_LEVEL = "1"

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

        last_login = format_timestamp(basic.get('lastlogin', 0))
        create_at = format_timestamp(basic.get('createat', 0))

        result_html = f"""
<div style="font-family: 'Inter', monospace;">
    <h4 style="color: #ff3b3b; text-align: center;">Player Information</h4>
    
    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: #ff3b3b; margin: 0 0 10px 0;">Basic Info</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Name</div>
                <div class="info-value" style="word-break: break-all;">{basic.get('username', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Level</div>
                <div class="info-value">{basic.get('level', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Exp</div>
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
                <div class="info-label">Likes</div>
                <div class="info-value">{basic.get('likes', 0):,}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Region</div>
                <div class="info-value">{basic.get('region', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Bio</div>
                <div class="info-value" style="word-break: break-all;">{basic.get('bio', 'N/A')}</div>
            </div>
        </div>
    </div>

    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: #ff3b3b; margin: 0 0 10px 0;">Dates</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Created</div>
                <div class="info-value">{create_at}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Last Login</div>
                <div class="info-value">{last_login}</div>
            </div>
        </div>
    </div>

    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: #ff3b3b; margin: 0 0 10px 0;">Guild Info</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Guild Name</div>
                <div class="info-value" style="word-break: break-all;">{clan.get('clanname', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Guild Level</div>
                <div class="info-value">{clan.get('guildlevel', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Members</div>
                <div class="info-value">{clan.get('livemember', 'N/A')}</div>
            </div>
        </div>
    </div>

    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h5 style="color: #ff3b3b; margin: 0 0 10px 0;">Guild Admin</h5>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Name</div>
                <div class="info-value" style="word-break: break-all;">{clan_admin.get('adminname', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Level</div>
                <div class="info-value">{clan_admin.get('level', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Exp</div>
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
        <h5 style="color: #ff3b3b;">Player Banner</h5>
        <div class="image-container">
            <img src="{banner_url}" alt="Player Banner" style="max-width: 100%; height: auto;" onerror="this.onerror=null; this.src=''; this.parentNode.innerHTML+='<p style=\'color:#ff6666;\'>⚠️ Banner load failed</p>'">
        </div>
    </div>

    <div style="margin-top: 15px; color: #888; font-size: 0.9em; text-align: center;">
        💎 ZIKO-TEAM · @ZikoBOSS
    </div>
</div>
"""

        return jsonify({"success": True, "result": result_html})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/get_outfit', methods=['POST'])
@login_required
def get_outfit():
    uid = request.form.get('uid', '').strip()
    region = request.form.get('region', 'ind').strip().lower()

    if not uid:
        return jsonify({"success": False, "error": "Please enter UID"})

    try:
        region_info = get_region_info(uid)
        
        outfit_url = f"https://ffoutfitapis.vercel.app/outfit-image?uid={uid}&region={region}&key=99day"
        response = requests.get(outfit_url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": "Failed to fetch outfit"})
        
        image_base64 = b64_encode.b64encode(response.content).decode('utf-8')
        image_data = f"data:image/png;base64,{image_base64}"
        
        result_html = f"""
<div style="text-align: center;">
    <h4 style="color: #ff3b3b;">👕 Player Outfit</h4>
    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <div style="margin: 8px 0; color: #ff6666; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
            <span>👤 Name: <span style="color: white; font-weight: bold;">{region_info.get('nickname', 'Unknown')}</span></span>
            <span>🆔 UID: <span style="color: white; font-weight: bold;">{uid}</span></span>
            <span>🌍 Region: <span style="color: white; font-weight: bold;">{region.upper()}</span></span>
        </div>
        <div class="image-container">
            <img src="{image_data}" alt="Player Outfit" style="max-width: 100%; height: auto;">
        </div>
    </div>
    <div style="margin-top: 10px; color: #888; font-size: 0.85rem;">
        💎 ZIKO-TEAM · @ZikoBOSS
    </div>
</div>
"""
        
        return jsonify({"success": True, "result": result_html})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/extract_guest', methods=['POST'])
@login_required
def extract_guest():
    if 'guest_file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})
    
    file = request.files['guest_file']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"})
    
    try:
        file_content = file.read()
        result = extract_guest_data(file_content)
        
        if result['success']:
            result_html = f"""
<div style="text-align: center;">
    <div style="background: linear-gradient(135deg, #00c853, #009624); color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <i class="fas fa-check-circle" style="font-size: 2rem;"></i>
        <h3 style="margin: 10px 0 0;">✅ Extraction Successful!</h3>
    </div>
    
    <div class="credential-item">
        <div class="credential-label">📌 UID</div>
        <div class="credential-value">
            <code style="color: white; font-size: 1rem; word-break: break-all; flex: 1;">{result['uid']}</code>
            <button onclick="copyToClipboard('{result['uid']}')" class="copy-btn">
                <i class="fas fa-copy"></i> Copy
            </button>
        </div>
    </div>
    
    <div class="credential-item">
        <div class="credential-label">🔑 Password</div>
        <div class="credential-value">
            <code style="color: white; font-size: 1rem; word-break: break-all; flex: 1;">{result['password']}</code>
            <button onclick="copyToClipboard('{result['password']}')" class="copy-btn">
                <i class="fas fa-copy"></i> Copy
            </button>
        </div>
    </div>
    
    <div style="margin-top: 15px; color: #888; font-size: 0.85rem;">
        💎 ZIKO-TEAM · @ZikoBOSS
    </div>
</div>
"""
            return jsonify({"success": True, "result": result_html})
        else:
            return jsonify({"success": False, "error": result.get('error', 'Extraction failed')})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/style_nick', methods=['POST'])
@login_required
def style_nick():
    name = request.form.get('name', '').strip()
    
    if not name:
        return jsonify({"success": False, "error": "Please enter a name"})
    
    try:
        styles = generate_styles(name)
        
        result_html = '<div style="font-family: monospace;">'
        result_html += '<h4 style="color: #ff3b3b; text-align: center; margin-bottom: 20px;">✨ Your Stylish Name Designs ✨</h4>'
        
        for i, style in enumerate(styles, 1):
            result_html += f'''
            <div class="style-item">
                <span class="style-text">{style}</span>
                <button onclick="copyToClipboard(\'{style}\')" class="style-copy-btn">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            '''
        
        result_html += '<div style="margin-top: 15px; color: #888; font-size: 0.85rem; text-align: center;">💎 ZIKO-TEAM · @ZikoBOSS</div>'
        result_html += '</div>'
        
        return jsonify({"success": True, "result": result_html})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# للتشغيل على Vercel
app = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)