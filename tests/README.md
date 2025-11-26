# テストガイド

アカウント発行依頼チャットボットのテストスイート

## テストの種類

### 1. 単体テスト（Unit Tests）
**ファイル**: `test_models.py`

Pydanticモデルの動作を検証します。

- AccountRequestモデルのバリデーション
- ConversationStateモデルの状態管理
- エッジケースと境界値テスト

### 2. 統合テスト（Integration Tests）
**ファイル**: `test_api_clients.py`

API クライアントの動作を検証します（モックを使用）。

- Trello APIクライアント
- Google Drive APIクライアント
- エラーハンドリング

### 3. E2Eテスト（End-to-End Tests）
**ファイル**: `test_e2e.py`

実際のアプリケーションフローを検証します。

- Trelloアカウント発行フロー
- Google Driveアカウント発行フロー
- バリデーションエラー処理
- 複数依頼の処理

## セットアップ

### 1. テスト用パッケージのインストール

```bash
# venv環境をアクティベート
source venv/bin/activate

# pytestとモックライブラリをインストール
pip install pytest pytest-mock pytest-cov
```

### 2. 環境変数の設定（オプション）

テストは主にモックを使用しますが、実際のAPI呼び出しをテストする場合は`.env`ファイルを設定してください。

## テストの実行

### 全テストを実行

```bash
pytest
```

### 特定のテストファイルを実行

```bash
# 単体テストのみ
pytest tests/test_models.py

# 統合テストのみ
pytest tests/test_api_clients.py

# E2Eテストのみ
pytest tests/test_e2e.py
```

### 特定のテストクラスを実行

```bash
pytest tests/test_models.py::TestAccountRequest
```

### 特定のテスト関数を実行

```bash
pytest tests/test_models.py::TestAccountRequest::test_valid_trello_request
```

### 詳細な出力で実行

```bash
pytest -v
```

### カバレッジレポート付きで実行

```bash
pytest --cov=src --cov-report=html
```

カバレッジレポートは`htmlcov/index.html`で確認できます。

### 失敗したテストのみ再実行

```bash
pytest --lf
```

### マーカーを使用して実行

```bash
# 単体テストのみ（将来的にマーカーを追加する場合）
pytest -m unit

# E2Eテストのみ
pytest -m e2e
```

## テスト結果の例

### 成功時

```
tests/test_models.py ✓✓✓✓✓✓✓✓✓✓✓✓ 100%
tests/test_api_clients.py ✓✓✓✓✓✓✓✓ 100%
tests/test_e2e.py ✓✓✓✓✓✓✓✓✓✓ 100%

=========== 30 passed in 2.34s ===========
```

### 失敗時

```
tests/test_models.py::TestAccountRequest::test_invalid_email_format FAILED

==================== FAILURES ====================
___ TestAccountRequest.test_invalid_email_format ___

    def test_invalid_email_format(self):
        with pytest.raises(ValidationError):
>           AccountRequest(
                email="invalid-email",
                tool="trello",
                background="テスト"
            )
E       Failed: DID NOT RAISE <class 'pydantic.error_wrappers.ValidationError'>

tests/test_models.py:45: Failed
=========== 1 failed, 29 passed in 2.45s ===========
```

## テストケース一覧

### test_models.py (12テスト)

| テスト名 | 目的 | 期待結果 |
|---------|------|---------|
| test_valid_trello_request | Trelloリクエストの正常系 | ✅ 成功 |
| test_valid_google_drive_request_reader | Google Drive reader権限 | ✅ 成功 |
| test_valid_google_drive_request_commenter | Google Drive commenter権限 | ✅ 成功 |
| test_valid_google_drive_request_writer | Google Drive writer権限 | ✅ 成功 |
| test_invalid_email_format | 不正なメール形式 | ❌ ValidationError |
| test_invalid_email_no_domain | ドメインなしメール | ❌ ValidationError |
| test_invalid_tool | 未対応のツール | ❌ ValidationError |
| test_invalid_permission | 不正な権限 | ❌ ValidationError |
| test_background_too_long | 背景256文字以上 | ❌ ValidationError |
| test_background_empty | 背景が空 | ❌ ValidationError |
| test_background_exactly_255_chars | 背景255文字ちょうど | ✅ 成功 |
| test_complete_state_google_drive | 完全な状態確認 | ✅ 成功 |

### test_api_clients.py (11テスト)

| テスト名 | 目的 | 期待結果 |
|---------|------|---------|
| test_initialization_success | Trelloクライアント初期化 | ✅ 成功 |
| test_initialization_missing_env_vars | 環境変数未設定 | ❌ ValueError |
| test_add_member_success | メンバー追加成功 | ✅ 成功 |
| test_add_member_api_error | API呼び出しエラー | ❌ Exception |
| test_add_permission_success | 権限追加成功 | ✅ 成功 |
| test_add_permission_file_not_found | ファイル404エラー | ❌ Exception |
| test_execute_trello_request_success | Trello実行成功 | ✅ 成功 |
| test_execute_google_drive_request_success | Google Drive実行成功 | ✅ 成功 |
| test_execute_trello_request_api_error | APIエラー処理 | ❌ エラー返却 |
| test_execute_google_drive_request_no_permission | 権限未指定 | ❌ エラー返却 |
| test_execute_invalid_tool | 未対応ツール | ❌ エラー返却 |

### test_e2e.py (15テスト)

| テスト名 | 目的 | 期待結果 |
|---------|------|---------|
| test_complete_trello_flow | Trello完全フロー | ✅ 成功 |
| test_complete_google_drive_reader_flow | Google Drive readerフロー | ✅ 成功 |
| test_complete_google_drive_commenter_flow | Google Drive commenterフロー | ✅ 成功 |
| test_complete_google_drive_writer_flow | Google Drive writerフロー | ✅ 成功 |
| test_google_drive_incomplete_without_permission | 権限未選択 | ❌ 未完了 |
| test_invalid_email_format | 不正メール形式 | ❌ 認識されない |
| test_background_too_long | 背景256文字超過 | ❌ エラー |
| test_reset_after_complete_flow | リセット機能 | ✅ 成功 |
| test_consecutive_requests | 連続依頼 | ✅ 成功 |
| test_trello_api_integration | Trello API統合 | ✅ 成功 |
| test_google_drive_api_integration | Google Drive API統合 | ✅ 成功 |
| test_email_in_sentence | 文章中のメール抽出 | ✅ 成功 |
| test_background_exactly_255_chars | 背景255文字境界値 | ✅ 成功 |
| test_multiple_emails_in_input | 複数メールアドレス | ✅ 最初を抽出 |
| test_trello_flow_with_japanese_keywords | 日本語キーワード | ✅ 成功 |

## CI/CDでの実行

### GitHub Actions の例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## トラブルシューティング

### モジュールが見つからない

```bash
# PYTHONPATHを設定
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest
```

または

```bash
# プロジェクトルートから実行
python -m pytest tests/
```

### 環境変数エラー

テストはモックを使用するため、実際の環境変数は不要ですが、エラーが出る場合は`.env.test`ファイルを作成してください。

```bash
cp .env.example .env.test
```

### ImportError

```bash
# srcパッケージをインストール
pip install -e .
```

## ベストプラクティス

1. **テストの独立性**: 各テストは独立して実行可能であること
2. **モックの使用**: 外部APIはモックを使用してテスト
3. **境界値テスト**: 255文字、空文字列などの境界値を必ずテスト
4. **エラーケース**: 正常系だけでなく異常系も必ずテスト
5. **テストの命名**: `test_<テスト対象>_<期待結果>`の形式で命名

## 今後の拡張

- [ ] パフォーマンステストの追加
- [ ] セキュリティテストの追加
- [ ] ブラウザテスト（Selenium/Playwright）
- [ ] 負荷テスト（Locust）
- [ ] スナップショットテスト

## 参考資料

- [Pytest公式ドキュメント](https://docs.pytest.org/)
- [Pytest-mock](https://github.com/pytest-dev/pytest-mock)
- [Pytest-cov](https://github.com/pytest-dev/pytest-cov)
