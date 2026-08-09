#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Termux Web - Vercel Edition (HTTP-only)
Deployable on Vercel as a serverless function.
"""

import os
import sys
import json
import base64
import subprocess
import shlex
import tempfile
from flask import Flask, request, jsonify, render_template_string, send_file

app = Flask(__name__)

# ---------- HTML Frontend (xterm.js + HTTP polling) ----------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Termux Web</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm/css/xterm.css" />
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #1e1e1e;
            display: flex;
            flex-direction: column;
            height: 100vh;
            font-family: 'Courier New', monospace;
        }
        #toolbar {
            background: #2d2d2d;
            padding: 8px 15px;
            display: flex;
            gap: 12px;
            align-items: center;
            border-bottom: 1px solid #444;
        }
        #toolbar button {
            background: #3a3a3a;
            border: none;
            color: #eee;
            padding: 6px 14px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        #toolbar button:hover { background: #555; }
        #toolbar input[type="file"] { display: none; }
        #terminal-container {
            flex: 1;
            padding: 8px;
            background: #1e1e1e;
        }
        .xterm { height: 100%; }
        #cwdDisplay { color: #0f0; margin-left: auto; font-weight: bold; }
    </style>
</head>
<body>
    <div id="toolbar">
        <span style="color: #0f0; font-weight: bold;">Termux Web (Vercel)</span>
        <button id="uploadBtn">📤 Upload</button>
        <button id="downloadBtn">📥 Download</button>
        <button id="clearBtn">🗑 Clear</button>
        <span id="cwdDisplay">/tmp</span>
    </div>
    <div id="terminal-container"></div>
    <input type="file" id="fileInput" multiple />

    <script src="https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"></script>
    <script>
        // ----- Setup terminal -----
        const term = new Terminal({
            cursorBlink: true,
            theme: { background: '#1e1e1e', foreground: '#f0f0f0', cursor: '#fff', green: '#00ff00' },
            fontFamily: '"Courier New", monospace',
            fontSize: 14,
            lineHeight: 1.2
        });

        const container = document.getElementById('terminal-container');
        term.open(container);
        term.focus();

        // ----- State (persisted in localStorage) -----
        let cwd = localStorage.getItem('termux_cwd') || '/tmp';
        let history = JSON.parse(localStorage.getItem('termux_history') || '[]');
        let histIndex = history.length;
        let currentLine = '';

        function updateCwdDisplay() {
            document.getElementById('cwdDisplay').textContent = cwd;
            localStorage.setItem('termux_cwd', cwd);
        }
        updateCwdDisplay();

        // ----- Execute command via HTTP -----
        async function executeCommand(cmd) {
            try {
                const resp = await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd, cwd: cwd })
                });
                const data = await resp.json();
                if (data.error) {
                    term.writeln('\\x1b[1;31mError: ' + data.error + '\\x1b[0m');
                } else {
                    if (data.stdout) term.write(data.stdout);
                    if (data.stderr) term.write('\\x1b[1;31m' + data.stderr + '\\x1b[0m');
                    if (data.new_cwd) {
                        cwd = data.new_cwd;
                        updateCwdDisplay();
                    }
                }
            } catch (e) {
                term.writeln('\\x1b[1;31mNetwork error: ' + e.message + '\\x1b[0m');
            }
        }

        // ----- Input handling -----
        function prompt() {
            term.write('\\x1b[32m$ \\x1b[0m');
        }

        term.onData((data) => {
            if (data === '\r') { // Enter
                term.write('\\r\\n');
                const cmd = currentLine.trim();
                currentLine = '';
                if (cmd) {
                    history.push(cmd);
                    localStorage.setItem('termux_history', JSON.stringify(history));
                    histIndex = history.length;
                    executeCommand(cmd).then(() => prompt());
                } else {
                    prompt();
                }
            } else if (data === '\x7f') { // Backspace
                if (currentLine.length > 0) {
                    currentLine = currentLine.slice(0, -1);
                    term.write('\\b \\b');
                }
            } else if (data === '\x03') { // Ctrl+C
                term.writeln('^C');
                currentLine = '';
                prompt();
            } else if (data === '\x1b[A') { // Up arrow
                if (histIndex > 0) {
                    histIndex--;
                    const cmd = history[histIndex] || '';
                    // clear current line
                    for (let i = 0; i < currentLine.length; i++) term.write('\\b \\b');
                    currentLine = cmd;
                    term.write(cmd);
                }
            } else if (data === '\x1b[B') { // Down arrow
                if (histIndex < history.length - 1) {
                    histIndex++;
                    const cmd = history[histIndex] || '';
                    for (let i = 0; i < currentLine.length; i++) term.write('\\b \\b');
                    currentLine = cmd;
                    term.write(cmd);
                } else {
                    histIndex = history.length;
                    for (let i = 0; i < currentLine.length; i++) term.write('\\b \\b');
                    currentLine = '';
                }
            } else if (data.length === 1 && data >= ' ' && data <= '~') {
                currentLine += data;
                term.write(data);
            }
        });

        // ----- File upload -----
        document.getElementById('uploadBtn').onclick = () => document.getElementById('fileInput').click();
        document.getElementById('fileInput').onchange = async (e) => {
            for (let file of e.target.files) {
                const reader = new FileReader();
                reader.onload = async (ev) => {
                    const content = ev.target.result.split(',')[1];
                    const resp = await fetch('/api/upload', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: file.name, content, cwd })
                    });
                    const result = await resp.json();
                    if (result.error) alert('Upload error: ' + result.error);
                    else term.writeln('\\x1b[32mUploaded: ' + file.name + '\\x1b[0m');
                };
                reader.readAsDataURL(file);
            }
            e.target.value = '';
        };

        // ----- File download -----
        document.getElementById('downloadBtn').onclick = async () => {
            const filename = prompt('Enter filename to download:');
            if (!filename) return;
            const resp = await fetch(`/api/download?path=${encodeURIComponent(filename)}&cwd=${encodeURIComponent(cwd)}`);
            if (resp.ok) {
                const blob = await resp.blob();
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = filename.split('/').pop();
                a.click();
            } else {
                const err = await resp.json();
                alert('Download error: ' + (err.error || 'Unknown'));
            }
        };

        document.getElementById('clearBtn').onclick = () => term.clear();

        // ----- Resize -----
        function resize() {
            const cols = Math.floor(container.clientWidth / 9.5);
            const rows = Math.floor(container.clientHeight / 19.5);
            if (cols > 0 && rows > 0) term.resize(cols, rows);
        }
        window.addEventListener('resize', resize);
        setTimeout(resize, 100);

        // ----- Initial prompt -----
        term.writeln('\\x1b[1;32mWelcome to Termux Web (Vercel)!\\x1b[0m');
        term.writeln('Note: Interactive commands (vim, top, etc.) are not supported.\\n');
        prompt();
    </script>
</body>
</html>
"""

# ---------- Backend API ----------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get('command', '').strip()
    cwd = data.get('cwd', '/tmp')
    if not command:
        return jsonify({'error': 'No command'})

    # Handle 'cd' built-in manually
    if command.startswith('cd '):
        parts = shlex.split(command)
        target = parts[1] if len(parts) >= 2 else os.path.expanduser('~')
        if target.startswith('~'):
            target = os.path.expanduser(target)
        new_cwd = os.path.realpath(os.path.join(cwd, target))
        if os.path.isdir(new_cwd):
            return jsonify({'new_cwd': new_cwd, 'stdout': '', 'stderr': ''})
        else:
            return jsonify({'error': f'cd: {target}: No such file or directory'})
    elif command == 'cd':
        return jsonify({'new_cwd': os.path.expanduser('~'), 'stdout': '', 'stderr': ''})

    # For other commands, run in a shell and capture new cwd
    # Use a unique marker to separate stdout from cwd
    marker = '---CWD---'
    full_cmd = f"{command}; echo '{marker}'; pwd"
    try:
        proc = subprocess.Popen(
            ['/bin/bash', '-c', full_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        stdout, stderr = proc.communicate(timeout=30)
        # Split stdout at the marker
        if marker in stdout:
            parts = stdout.split(marker)
            output = parts[0].rstrip('\n')
            new_cwd_line = parts[1].strip() if len(parts) > 1 else cwd
            # The new_cwd_line might contain extra output if the command also printed something after marker? Unlikely.
            # We'll assume pwd is the last line.
            new_cwd = new_cwd_line.split('\n')[-1].strip()
            # Remove the new_cwd from stdout?
            # We already separated; we'll keep output as the part before marker.
            # But we also need to strip trailing newline.
            stdout = output
        else:
            new_cwd = cwd
        return jsonify({
            'stdout': stdout,
            'stderr': stderr,
            'new_cwd': new_cwd
        })
    except subprocess.TimeoutExpired:
        proc.kill()
        return jsonify({'error': 'Command timed out'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    data = request.get_json()
    if not data or 'name' not in data or 'content' not in data or 'cwd' not in data:
        return jsonify({'error': 'Missing fields'}), 400
    name = os.path.basename(data['name'])
    cwd = data['cwd']
    # Ensure cwd exists, if not fallback to /tmp
    if not os.path.isdir(cwd):
        cwd = '/tmp'
    filepath = os.path.join(cwd, name)
    try:
        content = base64.b64decode(data['content'])
        # Write to file; if directory doesn't exist, try to create it? Not needed.
        with open(filepath, 'wb') as f:
            f.write(content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download_file():
    path = request.args.get('path', '')
    cwd = request.args.get('cwd', '/tmp')
    if not path:
        return jsonify({'error': 'Missing path'}), 400
    # Prevent directory traversal
    abs_path = os.path.realpath(os.path.join(cwd, path))
    if not abs_path.startswith(os.path.realpath(cwd)):
        return jsonify({'error': 'Access denied'}), 403
    if not os.path.isfile(abs_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(abs_path, as_attachment=True)

# ---------- For Vercel, we need to export 'app' as the WSGI handler ----------
# Vercel expects a variable named 'app'
# In this file, we have 'app' defined, so it's fine.

if __name__ == '__main__':
    # For local testing (not used on Vercel)
    app.run(host='0.0.0.0', port=5000)
