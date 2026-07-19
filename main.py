from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
import io
from PIL import Image
import pi_heif

# HEIC format ko support karne ke liye register kiya
pi_heif.register_heif_opener()

app = Flask(__name__)
CORS(app)

# Aapke credentials pehle se filled hain
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
    
    try:
        # Photo ko memory me read karna
        file_bytes = file.read()
        image_stream = io.BytesIO(file_bytes)
        
        # Kisi bhi format ki photo ho (HEIC, PNG, etc.), use PIL se open karo
        img = Image.open(image_stream)
        
        # Use standard RGB JPEG format me convert karo
        output_stream = io.BytesIO()
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.save(output_stream, format="JPEG", quality=85)
        output_stream.seek(0)
        
        # Telegram API URL
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        
        # Converted photo ko bhej rahe hain
        files = {'photo': ('photo.jpg', output_stream, 'image/jpeg')}
        data = {'chat_id': CHAT_ID}
        
        response = requests.post(url, files=files, data=data, timeout=60)
        res_data = response.json()
        
        if response.status_code == 200 and res_data.get("ok"):
            return jsonify({"success": True, "message": "Photo sent successfully!"})
        else:
            return jsonify({"success": False, "message": res_data.get("description", "Telegram error")}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Photo process nahi ho payi: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


