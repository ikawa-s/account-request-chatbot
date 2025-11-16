# アカウント発行依頼チャットボット

TrelloとGoogle Driveのアカウント発行を自動化するチャットボットアプリケーションです。

## 機能

- チャット形式でのアカウント発行依頼
- TrelloボードへのメンバーUNITE
- Google Driveファイルへの権限付与（reader/commenter/writer）
- LangChainによる会話管理
- Google Gemini APIによる自然言語処理
- Streamlitによる直感的なUI

## 技術スタック

- **Python 3.10+**
- **LangChain**: 会話チェーンとメモリ管理
- **Google Gemini API**: gemini-2.0-flash-exp モデル
- **Streamlit**: チャットUI
- **Pydantic**: データバリデーション
- **Trello API**: ボードメンバー管理
- **Google Drive API**: ファイル権限管理

## ディレクトリ構造

```
account-request-chatbot/
├── .env                    # 環境変数（作成が必要）
├── .env.example            # 環境変数のテンプレート
├── .gitignore              # Git除外設定
├── requirements.txt        # 依存パッケージ
├── README.md              # このファイル
├── app.py                 # Streamlitメインアプリ
├── src/
│   ├── __init__.py        # パッケージ初期化
│   ├── models.py          # Pydanticモデル
│   ├── langchain_setup.py # LangChain設定
│   ├── api_clients.py     # API クライアント
│   └── prompts.py         # プロンプトテンプレート
└── service-account.json   # Google サービスアカウント（作成が必要）
```

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd account-request-chatbot
```

### 2. Python仮想環境の作成

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

`.env` ファイルの編集:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Trello API
TRELLO_API_KEY=your_trello_api_key
TRELLO_API_TOKEN=your_trello_api_token
TRELLO_BOARD_ID=your_board_id

# Google Drive API
GOOGLE_DRIVE_FILE_ID=1_5kgU6PcBD954KyCqm-LsIv9VibDC9wOVGj7CLWVBoE
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json
```

### 5. API キーの取得

#### Gemini API

1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. 「Create API Key」をクリック
3. 生成されたAPIキーを `.env` の `GEMINI_API_KEY` に設定

#### Trello API

1. [Trello Developer Portal](https://trello.com/power-ups/admin) にアクセス
2. 「New」→「Create new Power-Up」
3. API KeyとTokenを取得
4. `.env` に設定

#### Google Drive API

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成
3. Google Drive APIを有効化
4. サービスアカウントを作成
5. JSONキーをダウンロードし、`service-account.json` として保存
6. `.env` の `GOOGLE_SERVICE_ACCOUNT_JSON` にパスを設定

### 6. アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 使い方

1. アプリケーションを起動
2. チャットボットの挨拶メッセージを確認
3. メールアドレスを入力
4. 必要なツール（TrelloまたはGoogle Drive）を選択
5. Google Driveの場合は権限（reader/commenter/writer）を選択
6. アカウントが必要な背景・理由を入力（最大255文字）
7. 自動でアカウント発行が実行される
8. 完了メッセージを確認

## 会話フロー

```
1. 挨拶とボットの説明
   ↓
2. メールアドレスを質問
   ↓
3. ツール選択（Trello / Google Drive）
   ↓
4. [Google Driveの場合のみ] 権限選択
   ↓
5. 背景・理由を質問
   ↓
6. API実行（Trello or Google Drive）
   ↓
7. 完了メッセージ表示
   ↓
8. 新しい依頼の開始を促す
```

## バリデーション

### メールアドレス
- 正しい形式のメールアドレス（例: `user@example.com`）
- エラー時: 「正しいメールアドレスの形式で入力してください。」

### ツール選択
- `Trello` または `Google Drive`
- 大文字小文字は区別しない

### 権限（Google Driveのみ）
- `reader`: 閲覧のみ
- `commenter`: コメント可
- `writer`: 編集可

### 背景
- 最大255文字
- 空白のみは不可
- エラー時: 「背景は255文字以内で入力してください。」

## エラーハンドリング

### バリデーションエラー
- LLMが自動的に再質問を生成
- エラー理由を丁寧に説明

### API エラー
- エラーメッセージを表示
- リトライなし（ユーザーに再度依頼を促す）

## トラブルシューティング

### Gemini API エラー

```
Error: API key not valid
```

→ `.env` の `GEMINI_API_KEY` が正しく設定されているか確認

### Trello API エラー

```
Error: unauthorized permission requested
```

→ Trello API TokenとKeyの権限を確認

### Google Drive API エラー

```
Error: File not found
```

→ `.env` の `GOOGLE_DRIVE_FILE_ID` が正しいか確認
→ サービスアカウントがファイルへのアクセス権限を持っているか確認

### モジュールインポートエラー

```
ModuleNotFoundError: No module named 'src'
```

→ プロジェクトのルートディレクトリから `streamlit run app.py` を実行

## テストケース

以下のシナリオでテストすることを推奨します：

1. **正常フロー（Trello）**
   - メールアドレス入力 → Trello選択 → 背景入力 → 完了

2. **正常フロー（Google Drive）**
   - メールアドレス入力 → Google Drive選択 → 権限選択 → 背景入力 → 完了

3. **不正なメールアドレス**
   - `invalid-email` などを入力して、エラーメッセージが表示されることを確認

4. **255文字超過の背景**
   - 256文字以上の文字列を入力して、エラーメッセージが表示されることを確認

5. **API失敗**
   - 誤った環境変数を設定して、適切なエラーメッセージが表示されることを確認

6. **新しい依頼の開始**
   - 完了後、新しいメールアドレスを入力して、新しい依頼が開始できることを確認

## セキュリティ

- `.env` と `service-account.json` は `.gitignore` に含まれており、Gitにコミットされません
- APIキーやトークンは環境変数で管理
- 本番環境では詳細なエラーメッセージを非表示にすることを推奨

## 開発

### コードスタイル

- PEP 8に準拠
- 型ヒントを使用
- Docstringでドキュメント化

### 拡張方法

#### 新しいツールの追加

1. `src/models.py` の `tool` Literalに新しいツールを追加
2. `src/api_clients.py` に新しいAPIクライアントを実装
3. `src/prompts.py` に新しいツール用のメッセージを追加
4. `app.py` の処理フローに新しいツールを統合

#### プロンプトのカスタマイズ

`src/prompts.py` を編集して、質問文やエラーメッセージをカスタマイズできます。

## ライセンス

MIT License

## サポート

問題が発生した場合は、以下を確認してください：

1. `.env` ファイルが正しく設定されているか
2. すべての依存パッケージがインストールされているか
3. Python 3.10以上を使用しているか
4. Streamlitが最新バージョンか

## 更新履歴

### v1.0.0 (2025-11-16)
- 初回リリース
- TrelloとGoogle Driveのアカウント発行機能
- チャット形式のUI
- LangChainによる会話管理
