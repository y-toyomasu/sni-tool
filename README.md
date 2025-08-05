# SNI Tool

サーバーとエージェントで構成されるコマンド実行システムです。HTTPS通信を使用して安全にリモートコマンドを実行できます。

## 概要

SNI Toolは、中央サーバーと複数のエージェント間でコマンドを安全に実行するためのシステムです。

### 主な機能

- **HTTPS通信**: SSL証明書による安全な通信
- **自動証明書生成**: 初回起動時にSSL証明書を自動生成
- **対話的コマンド実行**: サーバー側での対話的なコマンド入力
- **Docker対応**: コンテナ化されたデプロイメント
- **複数エージェント対応**: 複数のエージェントを同時管理

## システム構造

```
sni-tool/
├── server/                 # サーバーコンポーネント
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── app/
│       ├── server.py      # Flaskサーバー
│       └── requirements.txt
├── agent/                  # エージェントコンポーネント
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── app/
│       ├── agent.py       # コマンド実行エージェント
│       ├── requirements.txt
│       └── agent.conf     # エージェント設定（Git管理外）
└── README.md
```

## セットアップ

### 前提条件

- Docker と Docker Compose がインストールされていること
- ポート8443が利用可能であること

### 1. サーバーの起動

```bash
cd server
docker-compose up -d
```

サーバーは自動的にSSL証明書を生成し、ポート8443でHTTPS通信を開始します。

### 2. エージェントの設定

```bash
cd agent
# agent.confファイルを編集して設定を確認
```

`agent/app/agent.conf`の設定例：
```ini
[DEFAULT]
SERVER_IP = 192.168.1.100
SNI_HOST      = example.com
FETCH_PATH    = /fetch_command
POST_PATH     = /post_result
CLIENT_ID     = agent001
POLL_INTERVAL = 3
USERNAME      = Jack
HOST_HEADER   = example.com
```

### 3. エージェントの起動

```bash
cd agent
docker-compose up -d
```

## 使用方法

### 基本的な使用手順

1. **サーバーを起動**
   ```bash
   cd server
   docker-compose up -d
   ```

2. **エージェントを起動**
   ```bash
   cd agent
   docker-compose up -d
   ```

3. **コマンドを実行**
   - サーバー側で対話的にコマンドを入力
   - エージェントがコマンドを実行し、結果を返送
   - サーバー側で結果を確認

### 使用例

```bash
# サーバー側でコマンドを入力
> ls -la
> pwd
> whoami
```

## API エンドポイント

### サーバーAPI

- `GET /fetch_command?id=<client_id>` - コマンド取得
- `POST /post_result` - 実行結果送信

## 設定

### エージェント設定 (agent.conf)

| 設定項目 | 説明 | デフォルト値 |
|---------|------|-------------|
| SERVER_IP | サーバーのIPアドレス | 192.168.1.100 |
| SNI_HOST | SNIホスト名 | example.com |
| FETCH_PATH | コマンド取得パス | /fetch_command |
| POST_PATH | 結果送信パス | /post_result |
| CLIENT_ID | エージェントのID | agent001 |
| POLL_INTERVAL | ポーリング間隔（秒） | 3 |
| USERNAME | ユーザー名 | Jack |
| HOST_HEADER | ホストヘッダー | example.com |

## トラブルシューティング

### よくある問題

1. **ポート8443が使用中**
   ```bash
   # 別のポートを使用する場合
   # server/docker-compose.yml でポート番号を変更
   ```

2. **SSL証明書エラー**
   ```bash
   # 証明書を再生成
   rm -rf server/app/certs/
   docker-compose restart
   ```

3. **エージェントがサーバーに接続できない**
   - `agent.conf`の`SERVER_IP`を確認
   - `SNI_HOST`と`HOST_HEADER`の設定を確認
   - ファイアウォール設定を確認
   - サーバーが起動していることを確認

### ログの確認

```bash
# サーバーログ
docker-compose logs server

# エージェントログ
docker-compose logs agent
```

## 開発

### ローカル開発環境

```bash
# サーバー側
cd server/app
pip install -r requirements.txt
python server.py

# エージェント側
cd agent/app
pip install -r requirements.txt
python agent.py
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能要望は、GitHubのIssuesでお知らせください。

## 更新履歴

- v1.0.0: 初期リリース
  - 基本的なコマンド実行機能
  - HTTPS通信対応
  - Docker対応 