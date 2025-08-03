# LLM-Proxy-CLI

Google Gemini LLMを活用したコマンドラインインターフェース（CLI）アプリケーションです。
テキストファイルや標準入力からテキストを受け取り、Gemini LLMに送信して処理結果を取得できます。
**LLM-Guardによるセキュリティ機能を統合し、入力・出力の安全性を確保します。**

## 機能

- 📝 テキストファイルの処理
- ⌨️ 標準入力からのテキスト読み込み
- 🤖 Google Gemini LLMとの連携
- ⚙️ カスタマイズ可能なプロンプト
- 🎯 複数のGeminiモデル対応
- 🔧 環境変数による設定管理
- 🛡️ **LLM-Guardによるセキュリティ保護**
  - 入力検証（プロンプトインジェクション、機密情報検出）
  - 出力検証（不適切なコンテンツ、機密情報漏洩）
  - レート制限機能
  - セキュリティログ記録

## 必要条件

- Python 3.12以上
- Google Cloud Platform アカウント
- Gemini API アクセス権限

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd LLM-Proxy-CLI
```

### 2. 依存関係のインストール

```bash
# uvを使用した場合
uv sync

# または pip を使用
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env`ファイルを作成し、以下の環境変数をセットアップしてください。

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-apikey
```

## 使用方法

### 基本的な使用方法

```bash
# 標準入力からテキストを読み込み
echo "こんにちは、世界！" | python main.py

# ファイルからテキストを読み込み
python main.py -f input.txt

# カスタムプロンプトを指定
python main.py -p "このテキストを要約してください：" -f document.txt

# 特定のモデルを指定
python main.py -m gemini-1.5-pro-latest -f input.txt
```

### セキュリティ機能の使用

```bash
# デフォルトのセキュリティレベル（medium）で実行
python main.py -f input.txt

# 高セキュリティレベルで実行
python main.py --security-level high -f input.txt

# セキュリティガードを無効にする
python main.py --disable-guard -f input.txt

# カスタム設定ファイルを使用
python main.py --config custom_security.yaml -f input.txt

# セキュリティログを無効にする
python main.py --no-log-security -f input.txt
```

### コマンドラインオプション

| オプション | 短縮形 | 説明 | デフォルト値 |
|-----------|--------|------|-------------|
| `--prompt` | `-p` | LLMに与えるプロンプト | "以下のテキストを処理してください:" |
| `--file` | `-f` | 処理するテキストファイルのパス | 標準入力 |
| `--model` | `-m` | 使用するGeminiモデル | "gemini-2.0-flash" |
| `--security-level` | - | セキュリティレベル (low/medium/high) | "medium" |
| `--enable-guard` | - | セキュリティガードを有効にする | 有効 |
| `--disable-guard` | - | セキュリティガードを無効にする | - |
| `--log-security` | - | セキュリティイベントをログに記録する | 有効 |
| `--config` | - | セキュリティ設定ファイルのパス | "config/security.yaml" |

### セキュリティレベル

| レベル | 説明 | 機能 |
|--------|------|------|
| `low` | 低セキュリティ | レート制限のみ |
| `medium` | 中セキュリティ | 基本的な入力・出力検証 |
| `high` | 高セキュリティ | 包括的なセキュリティ検証 |

## セキュリティ機能

### 入力検証

- **プロンプトインジェクション検出**: 悪意のあるプロンプトの検出
- **機密情報検出**: パスワード、APIキー、トークンなどの検出
- **URL検証**: 悪意のあるURLの検出
- **毒性コンテンツ検出**: 不適切なコンテンツの検出
- **禁止トピック検出**: 暴力、憎悪、自傷などのトピック検出

### 出力検証

- **機密情報漏洩検出**: 応答内の機密情報検出
- **不適切コンテンツ検出**: 毒性、偏見などの検出
- **悪意のあるURL検出**: 応答内の危険なリンク検出
- **事実一貫性チェック**: 応答の事実性検証

### レート制限

- **API呼び出し制限**: 1分間あたりの最大リクエスト数制限
- **バースト制御**: 短時間での大量リクエスト防止
- **指数バックオフ**: エラー時の自動リトライ制御

## 設定

### セキュリティ設定ファイル

`config/security.yaml`ファイルでセキュリティ設定をカスタマイズできます：

```yaml
# セキュリティレベル別設定
security_levels:
  medium:
    enable_input_scanning: true
    enable_output_scanning: true
    enable_rate_limiting: true
    max_requests_per_minute: 60

# カスタムルール設定
custom_rules:
  banned_substrings:
    - "password"
    - "secret"
    - "api_key"
```

### Google Cloud認証の設定

#### 方法1: サービスアカウントキー（推奨）

1. Google Cloud Consoleでサービスアカウントを作成
2. JSONキーをダウンロード
3. 環境変数に設定：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

#### 方法2: ユーザー認証

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `GOOGLE_API_KEY` | Gemini API アクセスキー | 必須 |
| `GOOGLE_CLOUD_PROJECT` | Google CloudプロジェクトID | 推奨 |

## 使用例

### テキスト要約

```bash
python main.py -p "以下のテキストを3行で要約してください：" -f long_document.txt
```

### コードレビュー（セキュリティ付き）

```bash
python main.py -p "このコードの問題点を指摘し、改善案を提案してください：" -f code.py --security-level high
```

### 翻訳

```bash
python main.py -p "このテキストを英語に翻訳してください：" -f japanese_text.txt
```

### セキュリティテスト

```bash
# セキュリティ機能のテスト
python test_security.py
```

## トラブルシューティング

### 認証エラー

```
UserWarning: Your application has authenticated using end user credentials from Google Cloud SDK without a quota project.
```

この警告が表示される場合：

1. サービスアカウントキーを使用する
2. プロジェクトIDを明示的に設定する
3. 適切なAPI権限が付与されていることを確認する

### API制限エラー

- Google Cloud ConsoleでGemini APIが有効化されていることを確認
- クォータ制限を確認
- 適切なプロジェクトIDが設定されていることを確認

### セキュリティエラー

```
セキュリティエラー: 入力がセキュリティポリシーに違反しています
```

このエラーが表示される場合：

1. 入力テキストに機密情報が含まれていないか確認
2. 不適切なコンテンツが含まれていないか確認
3. 必要に応じてセキュリティレベルを調整

## 開発

### 依存関係

- `google-generativeai>=0.8.5`: Google Gemini APIクライアント
- `python-dotenv>=1.1.1`: 環境変数管理
- `llm-guard>=1.0.0`: セキュリティ機能
- `PyYAML>=6.0`: 設定ファイル読み込み

### プロジェクト構造

```
LLM-Proxy-CLI/
├── main.py              # メインアプリケーション
├── security_guard.py    # セキュリティガード実装
├── config_loader.py     # 設定ファイル読み込み
├── test_security.py     # セキュリティ機能テスト
├── config/
│   └── security.yaml    # セキュリティ設定ファイル
├── pyproject.toml       # プロジェクト設定
├── README.md            # このファイル
└── uv.lock              # 依存関係ロックファイル
```

## セキュリティログ

セキュリティイベントは`security.log`ファイルに記録されます：

```
2024-01-01 12:00:00 - WARNING - 入力スキャンでリスク検出: 0.75
2024-01-01 12:00:01 - INFO - 入力スキャン完了: リスクスコア 0.25
2024-01-01 12:00:02 - WARNING - レート制限に達しました: 60 requests/min
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能リクエストは、GitHubのIssuesページでお知らせください。

## 更新履歴

- v0.2.0: セキュリティ機能追加
  - LLM-Guard統合
  - 入力・出力検証機能
  - レート制限機能
  - セキュリティログ機能
  - 設定ファイル対応
- v0.1.0: 初期リリース
  - 基本的なCLI機能
  - Gemini LLM連携
  - ファイル入力対応
