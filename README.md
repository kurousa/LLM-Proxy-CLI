# LLM-Proxy-CLI

Google Gemini LLMを活用したコマンドラインインターフェース（CLI）アプリケーションです。
テキストファイルや標準入力からテキストを受け取り、Gemini LLMに送信して処理結果を取得できます。

## 機能

- 📝 テキストファイルの処理
- ⌨️ 標準入力からのテキスト読み込み
- 🤖 Google Gemini LLMとの連携
- ⚙️ カスタマイズ可能なプロンプト
- 🎯 複数のGeminiモデル対応
- 🔧 環境変数による設定管理

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

### コマンドラインオプション

| オプション | 短縮形 | 説明 | デフォルト値 |
|-----------|--------|------|-------------|
| `--prompt` | `-p` | LLMに与えるプロンプト | "以下のテキストを処理してください:" |
| `--file` | `-f` | 処理するテキストファイルのパス | 標準入力 |
| `--model` | `-m` | 使用するGeminiモデル | "gemini-2.0-flash" |

### 利用可能なモデル

Gemini API
- `gemini-2.0-flash` (デフォルト)

## 設定

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

### コードレビュー

```bash
python main.py -p "このコードの問題点を指摘し、改善案を提案してください：" -f code.py
```

### 翻訳

```bash
python main.py -p "このテキストを英語に翻訳してください：" -f japanese_text.txt
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

## 開発

### 依存関係

- `google-generativeai>=0.8.5`: Google Gemini APIクライアント
- `python-dotenv>=1.1.1`: 環境変数管理

### プロジェクト構造

```
LLM-Proxy-CLI/
├── main.py          # メインアプリケーション
├── pyproject.toml   # プロジェクト設定
├── README.md        # このファイル
└── uv.lock          # 依存関係ロックファイル
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能リクエストは、GitHubのIssuesページでお知らせください。

## 更新履歴

- v0.1.0: 初期リリース
  - 基本的なCLI機能
  - Gemini LLM連携
  - ファイル入力対応