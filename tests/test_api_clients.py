"""
API クライアントの統合テスト
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_clients import TrelloAPIClient, GoogleDriveAPIClient, execute_account_request


class TestTrelloAPIClient:
    """Trello APIクライアントのテスト"""

    def test_initialization_success(self):
        """正常系: 初期化成功"""
        with patch.dict(os.environ, {
            'TRELLO_API_KEY': 'test_key',
            'TRELLO_API_TOKEN': 'test_token',
            'TRELLO_BOARD_ID': 'test_board_id'
        }):
            client = TrelloAPIClient()
            assert client.api_key == 'test_key'
            assert client.api_token == 'test_token'
            assert client.board_id == 'test_board_id'

    def test_initialization_missing_env_vars(self):
        """異常系: 環境変数未設定"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                TrelloAPIClient()
            assert "環境変数が設定されていません" in str(exc_info.value)

    @patch('src.api_clients.requests.put')
    def test_add_member_success(self, mock_put):
        """正常系: メンバー追加成功"""
        # モックの設定
        mock_response = Mock()
        mock_response.json.return_value = {'id': '123', 'email': 'test@example.com'}
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        with patch.dict(os.environ, {
            'TRELLO_API_KEY': 'test_key',
            'TRELLO_API_TOKEN': 'test_token',
            'TRELLO_BOARD_ID': 'test_board_id'
        }):
            client = TrelloAPIClient()
            result = client.add_member_to_board('test@example.com')

        assert result['success'] is True
        assert 'data' in result
        mock_put.assert_called_once()

    @patch('src.api_clients.requests.put')
    def test_add_member_api_error(self, mock_put):
        """異常系: API呼び出しエラー"""
        # モックの設定
        mock_put.side_effect = Exception("API Error")

        with patch.dict(os.environ, {
            'TRELLO_API_KEY': 'test_key',
            'TRELLO_API_TOKEN': 'test_token',
            'TRELLO_BOARD_ID': 'test_board_id'
        }):
            client = TrelloAPIClient()
            with pytest.raises(Exception) as exc_info:
                client.add_member_to_board('test@example.com')
            assert "Trello APIエラー" in str(exc_info.value)


class TestGoogleDriveAPIClient:
    """Google Drive APIクライアントのテスト"""

    def test_initialization_missing_env_vars(self):
        """異常系: 環境変数未設定"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                GoogleDriveAPIClient()
            assert "環境変数が設定されていません" in str(exc_info.value)

    def test_initialization_missing_service_account_file(self):
        """異常系: サービスアカウントファイルが見つからない"""
        with patch.dict(os.environ, {
            'GOOGLE_DRIVE_FILE_ID': 'test_file_id',
            'GOOGLE_SERVICE_ACCOUNT_JSON': 'nonexistent.json'
        }):
            with pytest.raises(ValueError) as exc_info:
                GoogleDriveAPIClient()
            assert "サービスアカウントファイルが見つかりません" in str(exc_info.value)

    @patch('src.api_clients.build')
    @patch('src.api_clients.service_account.Credentials.from_service_account_file')
    @patch('os.path.exists')
    def test_add_permission_success(self, mock_exists, mock_creds, mock_build):
        """正常系: 権限追加成功"""
        # モックの設定
        mock_exists.return_value = True
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_permissions = mock_service.permissions.return_value
        mock_create = mock_permissions.create.return_value
        mock_create.execute.return_value = {'id': 'permission_123'}

        with patch.dict(os.environ, {
            'GOOGLE_DRIVE_FILE_ID': 'test_file_id',
            'GOOGLE_SERVICE_ACCOUNT_JSON': 'test.json'
        }):
            client = GoogleDriveAPIClient()
            result = client.add_permission('test@example.com', 'reader')

        assert result['success'] is True
        assert 'data' in result
        mock_permissions.create.assert_called_once()

    @patch('src.api_clients.build')
    @patch('src.api_clients.service_account.Credentials.from_service_account_file')
    @patch('os.path.exists')
    def test_add_permission_file_not_found(self, mock_exists, mock_creds, mock_build):
        """異常系: ファイルが見つからない（404エラー）"""
        from googleapiclient.errors import HttpError

        # モックの設定
        mock_exists.return_value = True
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_permissions = mock_service.permissions.return_value
        mock_create = mock_permissions.create.return_value

        # 404エラーを生成
        mock_response = Mock()
        mock_response.status = 404
        mock_create.execute.side_effect = HttpError(mock_response, b'File not found')

        with patch.dict(os.environ, {
            'GOOGLE_DRIVE_FILE_ID': 'invalid_file_id',
            'GOOGLE_SERVICE_ACCOUNT_JSON': 'test.json'
        }):
            client = GoogleDriveAPIClient()
            with pytest.raises(Exception) as exc_info:
                client.add_permission('test@example.com', 'reader')
            assert "ファイルが見つかりません" in str(exc_info.value)


class TestExecuteAccountRequest:
    """execute_account_request関数のテスト"""

    @patch('src.api_clients.TrelloAPIClient')
    def test_execute_trello_request_success(self, mock_trello_client):
        """正常系: Trelloアカウント発行成功"""
        # モックの設定
        mock_instance = mock_trello_client.return_value
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
        assert result['tool'] == 'trello'
        assert result['email'] == 'test@example.com'

    @patch('src.api_clients.GoogleDriveAPIClient')
    def test_execute_google_drive_request_success(self, mock_gdrive_client):
        """正常系: Google Driveアカウント発行成功"""
        # モックの設定
        mock_instance = mock_gdrive_client.return_value
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
        assert result['tool'] == 'google_drive'
        assert result['permission'] == 'reader'

    @patch('src.api_clients.TrelloAPIClient')
    def test_execute_trello_request_api_error(self, mock_trello_client):
        """異常系: Trello APIエラー"""
        # モックの設定
        mock_instance = mock_trello_client.return_value
        mock_instance.add_member_to_board.side_effect = Exception("API Error")

        result = execute_account_request(
            email='test@example.com',
            tool='trello',
            background='テスト'
        )

        assert result['success'] is False
        assert 'error' in result

    def test_execute_google_drive_request_no_permission(self):
        """異常系: Google Driveで権限未指定"""
        result = execute_account_request(
            email='test@example.com',
            tool='google_drive',
            background='テスト',
            permission=None
        )

        assert result['success'] is False
        assert 'error' in result

    def test_execute_invalid_tool(self):
        """異常系: 未対応のツール"""
        result = execute_account_request(
            email='test@example.com',
            tool='slack',
            background='テスト'
        )

        assert result['success'] is False
        assert 'error' in result
        assert '未対応のツール' in result['error']
