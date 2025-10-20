#!/usr/bin/env python3
"""LIFE_DB Web Clipper - Standalone met web interface"""
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import webbrowser
import threading

API_BASE = "http://localhost:8081"
PORT = 8888

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LIFE_DB Clipper</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 60px;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }
        button {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-secondary {
            background: #f5f5f5;
            color: #666;
        }
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        .status {
            margin-top: 20px;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .quick-btn {
            padding: 8px 16px;
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        .quick-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔖 LIFE_DB Clipper</h1>
        <p class="subtitle">Sla interessante content op in je database</p>
        
        <div class="quick-actions">
            <button class="quick-btn" onclick="pasteURL()">📋 Plak URL</button>
            <button class="quick-btn" onclick="getCurrentTab()">🌐 Huidige Tab</button>
            <button class="quick-btn" onclick="loadCategories()">🔄 Refresh</button>
        </div>
        
        <form id="clipForm" onsubmit="return submitClip(event)">
            <div class="form-group">
                <label for="url">URL *</label>
                <input type="url" id="url" name="url" required placeholder="https://example.com">
            </div>
            
            <div class="form-group">
                <label for="title">Titel (optioneel)</label>
                <input type="text" id="title" name="title" placeholder="Laat leeg voor automatisch">
            </div>
            
            <div class="form-group">
                <label for="category">Categorie</label>
                <select id="category" name="category">
                    <option value="">Geen categorie</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="tags">Tags (komma gescheiden)</label>
                <input type="text" id="tags" name="tags" placeholder="tech, artikel, belangrijk">
            </div>
            
            <div class="form-group">
                <label for="description">Beschrijving (optioneel)</label>
                <textarea id="description" name="description" placeholder="Korte beschrijving..."></textarea>
            </div>
            
            <div class="btn-group">
                <button type="button" class="btn-secondary" onclick="clearForm()">Wissen</button>
                <button type="submit" class="btn-primary">📌 Clip naar Database</button>
            </div>
        </form>
        
        <div id="status" class="status"></div>
    </div>
    
    <script>
        const API_BASE = 'http://localhost:8081';
        
        async function loadCategories() {
            try {
                const response = await fetch(`${API_BASE}/categories`);
                const data = await response.json();
                const select = document.getElementById('category');
                select.innerHTML = '<option value="">Geen categorie</option>';
                data.categories.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.name;
                    option.textContent = cat.name;
                    select.appendChild(option);
                });
                showStatus('Categorieën geladen', 'success');
            } catch (error) {
                showStatus('Fout bij laden categorieën: ' + error.message, 'error');
            }
        }
        
        async function submitClip(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            
            const tags = formData.get('tags').split(',').map(t => t.trim()).filter(t => t);
            
            const payload = {
                url: formData.get('url'),
                title: formData.get('title') || undefined,
                description: formData.get('description') || undefined,
                category: formData.get('category') || undefined,
                tags: tags
            };
            
            try {
                const response = await fetch(`${API_BASE}/capture`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) throw new Error(await response.text());
                
                const result = await response.json();
                showStatus(`✅ Succesvol geclipped! ID: ${result.id}`, 'success');
                clearForm();
            } catch (error) {
                showStatus('❌ Fout: ' + error.message, 'error');
            }
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            setTimeout(() => {
                status.style.display = 'none';
            }, 5000);
        }
        
        function clearForm() {
            document.getElementById('clipForm').reset();
        }
        
        async function pasteURL() {
            try {
                const text = await navigator.clipboard.readText();
                if (text.startsWith('http')) {
                    document.getElementById('url').value = text;
                    showStatus('URL geplakt', 'success');
                } else {
                    showStatus('Geen geldige URL in clipboard', 'error');
                }
            } catch (error) {
                showStatus('Kon niet plakken: ' + error.message, 'error');
            }
        }
        
        function getCurrentTab() {
            showStatus('Deze functie werkt alleen in een browser extensie', 'error');
        }
        
        // Load categories on page load
        loadCategories();
    </script>
</body>
</html>
"""

class ClipperHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode('utf-8'))
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_server():
    server = HTTPServer(('localhost', PORT), ClipperHandler)
    print(f"✅ LIFE_DB Clipper gestart op http://localhost:{PORT}")
    print(f"🌐 Opening browser...")
    threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    print(f"\n📌 Druk Ctrl+C om te stoppen\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Clipper gestopt")
        server.shutdown()

if __name__ == "__main__":
    start_server()
