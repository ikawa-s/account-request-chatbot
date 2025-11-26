"""
エンドツーエンド（E2E）テスト
実際のアプリケーションフローをテストする
"""

import os
import pytest
from unittest.mock import patch, Mock, MagicMock
from src.langchain_setup import ChatbotManager
from src.api_clients import execute_account_request


class TestTrelloAccountRequestFlow:
    """Trelloアカウント発行フローのE2Eテスト"""

    def test_complete_trello_flow(self):
        """正常系: Trelloの完全なフロー"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # ステップ1: メールアドレス入力
            result1 = manager.process_user_input('test@example.com')
            assert result1['status'] == 'continue'
            assert manager.state.email == 'test@example.com'

            # ステップ2: ツール選択
            result2 = manager.process_user_input('Trello')
            assert result2['status'] == 'continue'
            assert manager.state.tool == 'trello'

            # ステップ3: 背景入力
            result3 = manager.process_user_input('プロジェクト管理のため')
            assert result3['status'] == 'complete'
            assert manager.state.background == 'プロジェクト管理のため'
            assert manager.state.is_complete()

    def test_trello_flow_with_japanese_keywords(self):
        """正常系: 日本語キーワードでのTrelloフロー"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # メールアドレス
            manager.process_user_input('test@example.com')

            # トレロを選択
            result = manager.process_user_input('トレロを使いたいです')
            assert manager.state.tool == 'trello'

    def test_trello_flow_step_by_step_extraction(self):
        """正常系: 段階的な情報抽出"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # 初期状態
            assert not manager.state.is_complete()

            # メールアドレスのみ
            manager.process_user_input('user@example.com')
            assert manager.state.email == 'user@example.com'
            assert not manager.state.is_complete()

            # ツール追加
            manager.process_user_input('Trello')
            assert manager.state.tool == 'trello'
            assert not manager.state.is_complete()

            # 背景追加
            manager.process_user_input('タスク管理が必要です')
            assert manager.state.background == 'タスク管理が必要です'
            assert manager.state.is_complete()


class TestGoogleDriveAccountRequestFlow:
    """Google Driveアカウント発行フローのE2Eテスト"""

    def test_complete_google_drive_reader_flow(self):
        """正常系: Google Drive（reader）の完全なフロー"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # メールアドレス
            manager.process_user_input('viewer@example.com')
            assert manager.state.email == 'viewer@example.com'

            # Google Drive選択
            manager.process_user_input('Google Drive')
            assert manager.state.tool == 'google_drive'

            # reader権限選択
            result = manager.process_user_input('reader')
            assert manager.state.permission == 'reader'
            assert result['status'] == 'continue'

            # 背景入力
            result = manager.process_user_input('資料を閲覧したいです')
            assert result['status'] == 'complete'
            assert manager.state.is_complete()

    def test_complete_google_drive_commenter_flow(self):
        """正常系: Google Drive（commenter）の完全なフロー"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            manager.process_user_input('commenter@example.com')
            manager.process_user_input('Google Drive')
            manager.process_user_input('commenter')
            result = manager.process_user_input('コメントを追加したい')

            assert result['status'] == 'complete'
            assert manager.state.permission == 'commenter'

    def test_complete_google_drive_writer_flow(self):
        """正常系: Google Drive（writer）の完全なフロー"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            manager.process_user_input('editor@example.com')
            manager.process_user_input('Google Drive')
            manager.process_user_input('writer')
            result = manager.process_user_input('資料を編集したい')

            assert result['status'] == 'complete'
            assert manager.state.permission == 'writer'

    def test_google_drive_incomplete_without_permission(self):
        """異常系: Google Driveで権限未選択"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            manager.process_user_input('test@example.com')
            manager.process_user_input('Google Drive')
            # 権限を選択せずに背景を入力
            result = manager.process_user_input('アクセスしたい')

            # 権限が必要なので完了にならない
            assert result['status'] == 'continue'
            assert not manager.state.is_complete()


class TestValidationErrors:
    """バリデーションエラーのE2Eテスト"""

    def test_invalid_email_format(self):
        """異常系: 不正なメールアドレス形式"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # 不正なメールアドレス
            result = manager.process_user_input('invalid-email')
            # メールアドレスとして認識されない
            assert manager.state.email is None

    def test_background_too_long(self):
        """異常系: 背景が255文字超過"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            manager.process_user_input('test@example.com')
            manager.process_user_input('Trello')

            # 256文字の背景
            long_text = 'あ' * 256
            result = manager.process_user_input(long_text)

            assert result['status'] == 'error'
            assert '255文字以内' in result['errors']['background']


class TestConversationReset:
    """会話リセットのE2Eテスト"""

    def test_reset_after_complete_flow(self):
        """正常系: 完了後のリセット"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # 1件目の依頼
            manager.process_user_input('first@example.com')
            manager.process_user_input('Trello')
            manager.process_user_input('1件目の依頼')
            assert manager.state.is_complete()

            # リセット
            manager.reset_conversation()
            assert not manager.state.is_complete()
            assert manager.state.email is None
            assert manager.state.tool is None

            # 2件目の依頼
            manager.process_user_input('second@example.com')
            assert manager.state.email == 'second@example.com'


class TestMultipleRequests:
    """複数依頼のE2Eテスト"""

    def test_consecutive_requests(self):
        """正常系: 連続した複数の依頼"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # 1件目: Trello
            manager.process_user_input('user1@example.com')
            manager.process_user_input('Trello')
            result1 = manager.process_user_input('1件目')
            assert result1['status'] == 'complete'

            # リセット
            manager.reset_conversation()

            # 2件目: Google Drive
            manager.process_user_input('user2@example.com')
            manager.process_user_input('Google Drive')
            manager.process_user_input('reader')
            result2 = manager.process_user_input('2件目')
            assert result2['status'] == 'complete'
            assert manager.state.permission == 'reader'


class TestAPIIntegration:
    """API統合のE2Eテスト"""

    @patch('src.api_clients.TrelloAPIClient')
    def test_trello_api_integration(self, mock_client):
        """正常系: Trello API統合"""
        mock_instance = mock_client.return_value
        mock_instance.add_member_to_board.return_value = {
            'success': True,
            'data': {'id': '123'}
        }

        result = execute_account_request(
            email='test@example.com',
            tool='trello',
            background='テスト'
        )

        assert result['success'] is True
        mock_instance.add_member_to_board.assert_called_once_with('test@example.com')

    @patch('src.api_clients.GoogleDriveAPIClient')
    def test_google_drive_api_integration(self, mock_client):
        """正常系: Google Drive API統合"""
        mock_instance = mock_client.return_value
        mock_instance.add_permission.return_value = {
            'success': True,
            'data': {'id': 'permission_123'}
        }

        result = execute_account_request(
            email='viewer@example.com',
            tool='google_drive',
            background='閲覧のため',
            permission='reader'
        )

        assert result['success'] is True
        mock_instance.add_permission.assert_called_once_with('viewer@example.com', 'reader')


class TestEdgeCases:
    """エッジケースのE2Eテスト"""

    def test_email_in_sentence(self):
        """エッジケース: 文章中のメールアドレス抽出"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            result = manager.process_user_input('太郎さん（taro@example.com）のアカウントが必要です')
            assert manager.state.email == 'taro@example.com'

    def test_background_exactly_255_chars(self):
        """境界値: 背景が255文字ちょうど"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            manager.process_user_input('test@example.com')
            manager.process_user_input('Trello')

            # 255文字の背景
            text_255 = 'あ' * 255
            result = manager.process_user_input(text_255)

            assert result['status'] == 'complete'
            assert len(manager.state.background) == 255

    def test_multiple_emails_in_input(self):
        """エッジケース: 複数のメールアドレスが含まれる入力"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ChatbotManager()

            # 最初のメールアドレスが抽出される
            manager.process_user_input('first@example.com と second@example.com')
            assert manager.state.email == 'first@example.com'
