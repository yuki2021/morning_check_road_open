# morning_check_road

朝の通勤ルートをGoogle Maps Routes APIで比較し、最速ルートをSlackに通知するツール。
iOSショートカットからワンタップで起動できる。

## 構成

```
.
├── check_route.py              # メインスクリプト
├── requirements.txt
├── .env.example                # 環境変数テンプレート
└── .github/
    └── workflows/
        └── check_route.yml     # GitHub Actions ワークフロー
```

## 機能

- 複数の通勤ルートを同時に取得・比較
- リアルタイムの渋滞情報を考慮（`TRAFFIC_AWARE`）
- 最速ルートをSlackに通知
- GitHub Actions の `workflow_dispatch` でiOSショートカットから起動可能

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、各値を設定する。

```bash
cp .env.example .env
```

| 変数名 | 説明 |
|--------|------|
| `GOOGLE_MAPS_API_KEY` | Google Cloud Console で発行したAPIキー |
| `HOME_ADDRESS` | 出発地の住所 |
| `WORK_ADDRESS` | 目的地の住所 |
| `ROUTE1` | ルート1の名前と経由地（JSON形式） |
| `ROUTE2` | ルート2の名前と経由地（JSON形式） |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL |

ルートはJSON形式で定義する：

```
ROUTE1={"name": "ルートA", "waypoints": ["経由地1", "経由地2"]}
```

`ROUTE1` から連番で定義し、ルートを増やす場合は `ROUTE3`、`ROUTE4`... と追加するだけでよい。

### 3. ローカルで実行

```bash
python check_route.py
```

## GitHub Actions での実行

### Secrets の登録

リポジトリの `Settings` → `Secrets and variables` → `Actions` に以下を登録する。

| Secret名 | 説明 |
|----------|------|
| `GOOGLE_MAPS_API_KEY` | Google Maps APIキー |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL |
| `HOME_ADDRESS` | 出発地 |
| `WORK_ADDRESS` | 目的地 |
| `ROUTE1` 〜 `ROUTE4` | 各ルート定義（JSON） |

### iOSショートカットからの起動

GitHub Mobile アプリをインストールすると、ショートカットアプリに「ワークフローをディスパッチ」アクションが追加される。

| フィールド | 値 |
|---------|-----|
| Owner | GitHubユーザー名 |
| Workflow ID | `check_route.yml` |
| Repository | `morning_check_road_open` |
| Branch / ref | `main` |

## 注意事項

住所や通勤経路などの個人情報は `.env`（ローカルのみ）および GitHub Secrets で管理する。
ソースコードには一切含めないこと。

## 関連記事

- Zenn: （記事URL）
