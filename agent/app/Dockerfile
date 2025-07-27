FROM python:3.11-slim

# 必要なパッケージのインストール
RUN apt-get update && \
    apt-get install -y sudo && \
    rm -rf /var/lib/apt/lists/*

# Jackユーザーの作成とsudo権限付与
RUN useradd -m -s /bin/bash -u 1000 Jack && \
    usermod -aG sudo Jack && \
    echo 'Jack ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# 作業ディレクトリ作成
WORKDIR /app

# アプリケーションファイルをコピー
COPY . /app

# 依存パッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# /etc/passwdの権限変更
RUN chmod o-r /etc/passwd

# Jackユーザーで実行
USER Jack

CMD ["python3", "agent.py"] 