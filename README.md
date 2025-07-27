# SNI Tool

サーバーとエージェントで構成されるコマンド実行システムです。

## 構造

```
├── server/
│   ├── docker-compose.yml
│   ├── app/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
├── agent/
│   ├── docker-compose.yml
│   ├── app/
│   │   ├── agent.py
│   │   ├── requirements.txt
│   │   ├── agent.conf
│   │   └── Dockerfile
```

## 使用方法

### サーバーの起動

```bash
cd server
docker-compose up -d
```

サーバーは自動的にSSL証明書を生成し、ポート8443でHTTPS通信を開始します。

### エージェントの起動

```bash
cd agent
# agent.confファイルで設定を確認
# SERVER_URL=https://localhost:8443
# CLIENT_ID=agent001
# POLL_INTERVAL=1

docker-compose up -d
```

## 設定

### エージェント側 (agent.conf)

```ini
[DEFAULT]
SERVER_URL = https://localhost:8443
CLIENT_ID = agent001
POLL_INTERVAL = 1
```

## 機能

- **サーバー**: Flaskベースのコマンドサーバー（HTTPS、ポート8443）
- **エージェント**: コマンド実行エージェント
- **SSL通信**: 自己署名証明書によるHTTPS通信
- **対話的コマンド**: サーバー側での対話的なコマンド入力
- **自動証明書生成**: 初回起動時にSSL証明書を自動生成

## API エンドポイント

- `GET /fetch_command?id=<client_id>` - コマンド取得
- `POST /post_result` - 実行結果送信

## 使用例

1. サーバーを起動
2. エージェントを起動
3. サーバー側でコマンドを入力（例: `ls -la`）
4. エージェントがコマンドを実行し、結果を返送
5. サーバー側で結果を確認 