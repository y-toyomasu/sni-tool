FROM python:3.11-slim

# 必要なパッケージのインストール
RUN apt-get update && \
    apt-get install -y openssl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# appディレクトリの内容をコピー
COPY app/ /app

RUN pip install --no-cache-dir -r requirements.txt

# 証明書がなければ自動生成してサーバー起動
CMD ["bash", "-c", "if [ ! -f cert.pem ] || [ ! -f key.pem ]; then \
  echo '[init] Generating self-signed certificate...'; \
  openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj '/C=JP/ST=Tokyo/L=Minato/O=PoC Inc./CN=localhost'; \
fi && python3 server.py"]

EXPOSE 443 