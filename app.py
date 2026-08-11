# api/index.py
import hashlib
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ---------- Helper ----------
def hash_secondary(plain: str) -> str:
    """Return SHA‑256 uppercase hex of the plain password."""
    return hashlib.sha256(plain.encode()).hexdigest().upper()

# ---------- Garena API endpoints ----------
HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

def garena_post(url: str, data: dict):
    """Make a POST request to Garena and return JSON."""
    resp = requests.post(url, headers=HEADERS, data=data)
    resp.raise_for_status()
    return resp.json()

# ---------- API routes ----------
@app.route('/api/verify_identity', methods=['POST'])
def verify_identity():
    data = request.get_json()
    access_token = data.get('access_token')
    old_email = data.get('old_email')
    secondary_password = data.get('secondary_password')
    if not all([access_token, old_email, secondary_password]):
        return jsonify({'error': 'Missing required fields'}), 400

    hashed = hash_secondary(secondary_password)
    payload = {
        'email': old_email,
        'secondary_password': hashed,
        'app_id': '100067',
        'access_token': access_token
    }
    try:
        resp = garena_post(
            'https://100067.connect.garena.com/game/account_security/bind:verify_identity',
            payload
        )
        identity_token = resp.get('identity_token')
        if not identity_token:
            return jsonify({'error': 'Identity verification failed', 'details': resp}), 400
        return jsonify({'identity_token': identity_token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    new_email = data.get('new_email')
    access_token = data.get('access_token')
    if not all([new_email, access_token]):
        return jsonify({'error': 'Missing required fields'}), 400

    payload = {
        'email': new_email,
        'locale': 'en_MA',
        'region': 'IND',
        'app_id': '100067',
        'access_token': access_token
    }
    try:
        resp = garena_post(
            'https://100067.connect.garena.com/game/account_security/bind:send_otp',
            payload
        )
        # Garena returns {"result":0} on success
        if resp.get('result') != 0:
            return jsonify({'error': 'Failed to send OTP', 'details': resp}), 400
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    new_email = data.get('new_email')
    otp = data.get('otp')
    access_token = data.get('access_token')
    if not all([new_email, otp, access_token]):
        return jsonify({'error': 'Missing required fields'}), 400

    payload = {
        'email': new_email,
        'otp': otp,
        'app_id': '100067',
        'access_token': access_token
    }
    try:
        resp = garena_post(
            'https://100067.connect.garena.com/game/account_security/bind:verify_otp',
            payload
        )
        verifier_token = resp.get('verifier_token')
        if not verifier_token:
            return jsonify({'error': 'OTP verification failed', 'details': resp}), 400
        return jsonify({'verifier_token': verifier_token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rebind', methods=['POST'])
def rebind():
    data = request.get_json()
    identity_token = data.get('identity_token')
    verifier_token = data.get('verifier_token')
    new_email = data.get('new_email')
    access_token = data.get('access_token')
    if not all([identity_token, verifier_token, new_email, access_token]):
        return jsonify({'error': 'Missing required fields'}), 400

    payload = {
        'identity_token': identity_token,
        'email': new_email,
        'app_id': '100067',
        'verifier_token': verifier_token,
        'access_token': access_token
    }
    try:
        resp = garena_post(
            'https://100067.connect.garena.com/game/account_security/bind:create_rebind_request',
            payload
        )
        if resp.get('result') != 0:
            return jsonify({'error': 'Rebind failed', 'details': resp}), 400
        return jsonify({'success': True, 'response': resp})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- Frontend ----------
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Change Bind Email</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0b0e14;
            color: #e0e6f0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: #1a1f2b;
            border-radius: 24px;
            padding: 32px 36px;
            max-width: 520px;
            width: 100%;
            box-shadow: 0 12px 40px rgba(0,0,0,0.6);
            border: 1px solid #2a3240;
        }
        h1 {
            font-size: 24px;
            font-weight: 600;
            text-align: center;
            margin-bottom: 24px;
            color: #d0d9e8;
            letter-spacing: 0.5px;
        }
        .form-group {
            margin-bottom: 18px;
        }
        label {
            display: block;
            font-size: 13px;
            font-weight: 500;
            color: #8e9bb5;
            margin-bottom: 6px;
        }
        input {
            width: 100%;
            padding: 12px 14px;
            background: #0f141e;
            border: 1px solid #2e384b;
            border-radius: 12px;
            color: #f0f4fe;
            font-size: 15px;
            transition: border 0.2s;
            outline: none;
        }
        input:focus {
            border-color: #5b7cfa;
        }
        input::placeholder {
            color: #55647a;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: #4b6af5;
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.05s;
            margin-top: 6px;
        }
        .btn:hover { background: #5f7cf7; }
        .btn:active { transform: scale(0.98); }
        .btn:disabled {
            opacity: 0.5;
            pointer-events: none;
        }
        .btn-secondary {
            background: #2e384b;
        }
        .btn-secondary:hover { background: #3d4a62; }
        #otp-section {
            margin-top: 20px;
            border-top: 1px solid #2a3240;
            padding-top: 20px;
            display: none;
        }
        #status {
            margin-top: 18px;
            padding: 12px 16px;
            border-radius: 12px;
            background: #11161f;
            font-size: 14px;
            line-height: 1.5;
            min-height: 40px;
            white-space: pre-wrap;
            word-break: break-word;
            display: none;
        }
        #status.error { color: #f88b8b; background: #2b1a1a; border-left: 4px solid #f55; }
        #status.success { color: #8bdd8b; background: #1a2b1a; border-left: 4px solid #5f5; }
        #status.info { color: #8bb3f0; background: #1a223b; border-left: 4px solid #55aaff; }
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid #4b6af5;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            vertical-align: middle;
            margin-right: 10px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .flex-row {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        .flex-row .btn { flex: 1; margin-top: 0; }
        .hidden { display: none; }
    </style>
</head>
<body>
<div class="container">
    <h1>🔐 Change Bind Email</h1>
    <form id="main-form">
        <div class="form-group">
            <label>Access Token</label>
            <input type="text" id="access_token" placeholder="Enter your access token" required>
        </div>
        <div class="form-group">
            <label>Current Email</label>
            <input type="email" id="old_email" placeholder="old@email.com" required>
        </div>
        <div class="form-group">
            <label>New Email</label>
            <input type="email" id="new_email" placeholder="new@email.com" required>
        </div>
        <div class="form-group">
            <label>Secondary Password</label>
            <input type="password" id="secondary_password" placeholder="Your secondary password" required>
        </div>
        <button type="submit" class="btn" id="submit-btn">Start</button>
    </form>

    <div id="otp-section">
        <div class="form-group">
            <label>OTP sent to <span id="otp-email-label"></span></label>
            <input type="text" id="otp" placeholder="Enter 6‑digit code" maxlength="10">
        </div>
        <div class="flex-row">
            <button class="btn" id="verify-otp-btn">Verify OTP & Rebind</button>
            <button class="btn btn-secondary" id="resend-otp-btn">Resend</button>
        </div>
    </div>

    <div id="status"></div>
</div>

<script>
// ---------- DOM refs ----------
const form = document.getElementById('main-form');
const statusDiv = document.getElementById('status');
const submitBtn = document.getElementById('submit-btn');
const otpSection = document.getElementById('otp-section');
const otpInput = document.getElementById('otp');
const verifyOtpBtn = document.getElementById('verify-otp-btn');
const resendOtpBtn = document.getElementById('resend-otp-btn');
const otpEmailLabel = document.getElementById('otp-email-label');

let state = {
    access_token: '',
    old_email: '',
    new_email: '',
    identity_token: '',
    verifier_token: ''
};

// ---------- Helpers ----------
function setStatus(msg, type = 'info') {
    statusDiv.textContent = msg;
    statusDiv.className = type;
    statusDiv.style.display = 'block';
}

function clearStatus() {
    statusDiv.style.display = 'none';
    statusDiv.className = '';
}

function showLoading(btn, loading = true) {
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Processing...';
    } else {
        btn.disabled = false;
        btn.textContent = btn.dataset.originalText || 'Submit';
    }
}

// ---------- API calls ----------
async function callApi(url, body) {
    const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.error || 'Request failed');
    }
    return data;
}

// ---------- Main flow ----------
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearStatus();

    const access_token = document.getElementById('access_token').value.trim();
    const old_email = document.getElementById('old_email').value.trim();
    const new_email = document.getElementById('new_email').value.trim();
    const secondary_password = document.getElementById('secondary_password').value;

    if (!access_token || !old_email || !new_email || !secondary_password) {
        setStatus('Please fill in all fields.', 'error');
        return;
    }

    state.access_token = access_token;
    state.old_email = old_email;
    state.new_email = new_email;

    submitBtn.dataset.originalText = submitBtn.textContent;
    showLoading(submitBtn, true);

    try {
        // Step 1: Verify identity
        setStatus('Verifying identity...', 'info');
        const identityResp = await callApi('/api/verify_identity', {
            access_token,
            old_email,
            secondary_password
        });
        state.identity_token = identityResp.identity_token;

        // Step 2: Send OTP
        setStatus('Sending OTP to ' + new_email + '...', 'info');
        await callApi('/api/send_otp', {
            new_email,
            access_token
        });

        // Show OTP section
        otpEmailLabel.textContent = new_email;
        otpSection.style.display = 'block';
        setStatus('✅ OTP sent! Enter the code below.', 'success');
        submitBtn.disabled = true;  // prevent re‑submission
        submitBtn.textContent = '✔ Started';

        // Store resend handler
        resendOtpBtn.onclick = async () => {
            clearStatus();
            setStatus('Resending OTP...', 'info');
            try {
                await callApi('/api/send_otp', { new_email, access_token });
                setStatus('✅ OTP resent to ' + new_email, 'success');
            } catch (err) {
                setStatus('❌ ' + err.message, 'error');
            }
        };

        // Verify OTP button
        verifyOtpBtn.onclick = async () => {
            const otp = otpInput.value.trim();
            if (!otp) {
                setStatus('Please enter the OTP.', 'error');
                return;
            }
            clearStatus();
            setStatus('Verifying OTP...', 'info');
            showLoading(verifyOtpBtn, true);

            try {
                const otpResp = await callApi('/api/verify_otp', {
                    new_email,
                    otp,
                    access_token
                });
                state.verifier_token = otpResp.verifier_token;

                // Step 4: Rebind
                setStatus('Creating rebind request...', 'info');
                const rebindResp = await callApi('/api/rebind', {
                    identity_token: state.identity_token,
                    verifier_token: state.verifier_token,
                    new_email,
                    access_token
                });
                setStatus('✅ Email rebind successful! ' + JSON.stringify(rebindResp.response), 'success');
                otpSection.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Start Over';
                // reset form? user can reload.
            } catch (err) {
                setStatus('❌ ' + err.message, 'error');
            } finally {
                showLoading(verifyOtpBtn, false);
            }
        };

    } catch (err) {
        setStatus('❌ ' + err.message, 'error');
        showLoading(submitBtn, false);
    } finally {
        // Not disabling submitBtn here because we disable it on success, but on error we re-enable.
        if (submitBtn.disabled === false) {
            showLoading(submitBtn, false);
        }
    }
});

// Reset OTP button text after load
verifyOtpBtn.dataset.originalText = verifyOtpBtn.textContent;
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

# ---------- For local development ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
