from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

LIBRETRANSLATE_URL = "https://libretranslate.com/translate"

@app.route("/translate", methods=["POST"])
def translate():
    text = request.json.get("text")
    source_lang = request.json.get("source_lang", "auto")
    target_lang = request.json.get("target_lang", "en")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        response = requests.post(
            LIBRETRANSLATE_URL,
            json={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            },
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        result = response.json()
        return jsonify({
            "translated_text": result.get("translatedText", ""),
            "original_text": text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "PolyGlot API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
