from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

RESULTS_DIR = "/app/data/results"
ANALYSIS_DIR = "/app/data/analysis"

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@app.route('/api/correlations')
def get_correlations():
    """API endpoint para obtener correlaciones"""
    try:
        path = os.path.join(RESULTS_DIR, "correlations_latest.json")
        
        if not os.path.exists(path):
            return jsonify({"error": "No data available"}), 404
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/news_counts')
def get_news_counts():
    """API endpoint para obtener conteos de noticias"""
    try:
        path = os.path.join(ANALYSIS_DIR, "daily_counts.json")
        
        if not os.path.exists(path):
            return jsonify({"error": "No data available"}), 404
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def get_status():
    """API endpoint para verificar estado del sistema"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "correlations_available": os.path.exists(os.path.join(RESULTS_DIR, "correlations_latest.json")),
        "news_data_available": os.path.exists(os.path.join(ANALYSIS_DIR, "daily_counts.json"))
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)