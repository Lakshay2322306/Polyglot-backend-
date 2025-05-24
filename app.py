from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)  # Allow requests from any domain
# For production, use: CORS(app, origins=["https://polyglot-phi.vercel.app"])

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# External Translation APIs
LIBRETRANSLATE_URL = "https://libretranslate.com/translate"
LINGVA_URL = "https://lingva.ml/api/v1"

def translate_text(text, source="auto", target="es"):
    try:
        response = requests.post(
            LIBRETRANSLATE_URL,
            json={"q": text, "source": source, "target": target, "format": "text"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("translatedText", "Translation failed"), None
        logger.warning(f"LibreTranslate failed: HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"LibreTranslate error: {str(e)}")

    try:
        lingva_url = f"{LINGVA_URL}/{source}/{target}/{text}"
        response = requests.get(lingva_url, timeout=5)
        if response.status_code == 200:
            return response.json().get("translation", "Translation failed"), None
        return None, f"Lingva failed: HTTP {response.status_code}"
    except Exception as e:
        return None, f"Lingva error: {str(e)}"

@app.route('/')
def home():
    return jsonify({"message": "PolyGlot API is running."})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang', 'es')

    if not text:
        return jsonify({"error": "Please enter text to translate"}), 400

    translated_text, error = translate_text(text, source_lang, target_lang)
    if error or not translated_text:
        return jsonify({"error": error or "Translation failed"}), 500

    return jsonify({
        "original_text": text,
        "translated_text": translated_text,
        "source_lang": source_lang,
        "target_lang": target_lang
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
