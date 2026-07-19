from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Aapke screenshots se exact credentials daal diye hain
BOT_TOKEN = "8903839809:AAGFAtDI4HVNwxd4IzCH4WAhY12FY73BvA0"  
CHAT_ID = "8036623116"      

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-photo', methods=['POST'])
def send_photo():
    if 'photo' not in request.files:
        return jsonify({"success": False, "message": "Photo nahi mili"}), 400
        
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"success": False, "message": "File select nahi ki"}), 400

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    # HEIC aur dynamic content type handle karne ke liye headers mapping
    mime_type = file.mimetype if file.mimetype else 'application/octet-stream'
    files = {'photo': (file.filename, file.stream, mime_type)}
    data = {'chat_id': CHAT_ID}
    
    try:
        # Timeout ko max 120 seconds kar diya hai taaki dusre phone ki heavy files na rukein
        response = requests.post(url, files=files, data=data, timeout=120)
        res_data = response.json()
        
        if response.status_code == 200 and res_data.get("ok"):
            return jsonify({"success": True, "message": "Photo sent successfully!"})
        else:
            return jsonify({"success": False, "message": res_data.get("description", "Telegram error")}), 500
    except requests.exceptions.Timeout:
        return jsonify({"success": False, "message": "File processing me time lag raha hai. Fir se try karein!"}), 504
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

