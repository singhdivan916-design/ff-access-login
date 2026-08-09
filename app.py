# api/index.py (or app.py)
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

def convert(seconds):
    """Convert seconds to human readable format"""
    d, h = divmod(seconds, 86400)
    h, m = divmod(h, 3600)
    m, s = divmod(m, 60)
    parts = []
    if d > 0:
        parts.append(f"{d} Day{'s' if d != 1 else ''}")
    if h > 0:
        parts.append(f"{h} Hour{'s' if h != 1 else ''}")
    if m > 0:
        parts.append(f"{m} Min{'s' if m != 1 else ''}")
    if s > 0 or not parts:
        parts.append(f"{s} Sec{'s' if s != 1 else ''}")
    return " ".join(parts)

def get_bind_info(access_token):
    """Get bind information from Garena API"""
    url = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
    payload = {'app_id': "100067", 'access_token': access_token}
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }
    
    try:
        response = requests.get(url, params=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            email = data.get("email", "")
            email_to_be = data.get("email_to_be", "")
            countdown = data.get("request_exec_countdown", 0)
            
            result = {
                "status": "success",
                "current_email": email,
                "pending_email": email_to_be,
                "countdown_seconds": countdown,
                "countdown_human": convert(countdown) if countdown > 0 else "0",
                "raw_response": data
            }
            
            if email == "" and email_to_be != "":
                result["summary"] = f"Pending email confirmation: {email_to_be} - Confirms in: {convert(countdown)}"
            elif email != "" and email_to_be == "":
                result["summary"] = f"Email confirmed: {email}"
            elif email == "" and email_to_be == "":
                result["summary"] = "No recovery email set"
            else:
                result["summary"] = f"Current: {email} | Pending change: {email_to_be}"
                
            return result
        else:
            return {
                "status": "error",
                "error": f"API returned status code {response.status_code}",
                "details": response.text[:200] if response.text else "No response body"
            }
            
    except requests.exceptions.Timeout:
        return {"status": "error", "error": "Request timed out (30 seconds)"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "error": "Connection error - cannot reach Garena API"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "error": f"Unexpected error: {str(e)}"}

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Garena Bind Info</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
        h1 { font-size: 1.8rem; }
        label { font-weight: bold; display: block; margin-top: 20px; }
        input[type="text"] { width: 100%; padding: 8px; font-size: 1rem; box-sizing: border-box; }
        button { margin-top: 10px; padding: 8px 20px; font-size: 1rem; cursor: pointer; }
        .result { margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px; }
        .success { color: #0a0; }
        .error { color: #a00; }
        pre { background: #f4f4f4; padding: 10px; overflow: auto; }
    </style>
</head>
<body>
    <h1>🔐 Garena Bind Info</h1>
    <form method="POST">
        <label for="token">Access Token</label>
        <input type="text" id="token" name="token" placeholder="Enter your Garena access token" required>
        <button type="submit">Check</button>
    </form>
    {% if result %}
    <div class="result">
        <h2>Result</h2>
        {% if result.status == "success" %}
            <p class="success">✅ Success</p>
            <p><strong>Summary:</strong> {{ result.summary }}</p>
            <p><strong>Current email:</strong> {{ result.current_email or "None" }}</p>
            <p><strong>Pending email:</strong> {{ result.pending_email or "None" }}</p>
            <p><strong>Countdown:</strong> {{ result.countdown_human }}</p>
            <details>
                <summary>Raw API response</summary>
                <pre>{{ result.raw_response | tojson(indent=2) }}</pre>
            </details>
        {% else %}
            <p class="error">❌ Error: {{ result.error }}</p>
            {% if result.details %}
                <p><strong>Details:</strong> {{ result.details }}</p>
            {% endif %}
        {% endif %}
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        if token:
            result = get_bind_info(token)
        else:
            result = {"status": "error", "error": "No access token provided."}
    return render_template_string(HTML_FORM, result=result)

# For local development
if __name__ == '__main__':
    app.run(debug=True)