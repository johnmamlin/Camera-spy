from flask import Flask, Response
import cv2
import socket
import requests

app = Flask(__name__)
camera = cv2.VideoCapture(0)

# Telegram bot config — fill these!
TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHAT_ID = ''


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text
    }
    try:
        r = requests.post(url, data=payload)
        r.raise_for_status()
        print("Telegram message sent!")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    local_ip = get_local_ip()
    url_local = f"http://127.0.0.1:5000"
    url_network = f"http://{local_ip}:5000"

    # Write to me.txt
    with open('me.txt', 'w') as f:
        f.write(f"Localhost URL: {url_local}\n")
        f.write(f"Network URL: {url_network}\n")

    # Send Telegram message
    message = f"Webcam app running!\nLocal: {url_local}\nNetwork: {url_network}"
    send_telegram_message(message)

    # Run Flask app
    app.run(host='0.0.0.0', port=5000)
