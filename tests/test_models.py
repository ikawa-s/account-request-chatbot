"""
Pydanticモデルの単体テスト
"""

import pytest
from pydantic import ValidationError
from src.models import AccountRequest, ConversationState


class TestAccountRequest:
    """AccountRequestモデルのテスト"""

    def test_valid_trello_request(self):
        """正常系: Trelloアカウント発行リクエスト"""
        request = AccountRequest(
            email="test@example.com",
            tool="trello",
            background="プロジェクト管理のため"
        )
        assert request.email == "test@example.com"
        assert request.tool == "trello"
        assert request.permission is None
        assert request.background == "プロジェクト管理のため"

    def test_valid_google_drive_request_reader(self):
        """正常系: Google Drive reader権限"""
        request = AccountRequest(
            email="viewer@example.com",
            tool="google_drive",
            permission="reader",
            background="資料を閲覧するため"
        )
        assert request.email == "viewer@example.com"
        assert request.tool == "google_drive"
        assert request.permission == "reader"

    def test_valid_google_drive_request_commenter(self):
        """正常系: Google Drive commenter権限"""
        request = AccountRequest(
            email="commenter@example.com",
            tool="google_drive",
            permission="commenter",
            background="コメントを追加するため"
        )
        assert request.permission == "commenter"

    def test_valid_google_drive_request_writer(self):
        """正常系: Google Drive writer権限"""
        request = AccountRequest(
            email="editor@example.com",
            tool="google_drive",
            permission="writer",
            background="資料を編集するため"
        )
        assert request.permission == "writer"

    def test_invalid_email_format(self):
        """異常系: 不正なメールアドレス形式"""
        with pytest.raises(ValidationError):
            AccountRequest(
                email="invalid-email",
                tool="trello",
                background="テスト"
            )

    def test_invalid_email_no_domain(self):
        """異常系: ドメインがないメールアドレス"""
        with pytest.raises(ValidationError):
            AccountRequest(
                email="test@",
                tool="trello",
                background="テスト"
            )

    def test_invalid_tool(self):
        """異常系: サポートされていないツール"""
        with pytest.raises(ValidationError):
            AccountRequest(
                email="test@example.com",
                tool="slack",  # サポート外
                background="テスト"
            )

    def test_invalid_permission(self):
        """異常系: 不正な権限"""
        with pytest.raises(ValidationError):
            AccountRequest(
                email="test@example.com",
                tool="google_drive",
                permission="admin",  # サポート外
                background="テスト"
            )

    def test_background_too_long(self):
        """異常系: 背景が255文字超過"""
        with pytest.raises(ValidationError) as exc_info:
            AccountRequest(
                email="test@example.com",
                tool="trello",
                background="あ" * 256
            )
        assert "255文字以内" in str(exc_info.value)

    def test_background_empty(self):
        """異常系: 背景が空"""
        with pytest.raises(ValidationError) as exc_info:
            AccountRequest(
                email="test@example.com",
                tool="trello",
                background="   "
            )
        assert "背景を入力してください" in str(exc_info.value)

    def test_background_exactly_255_chars(self):
        """境界値: 背景が255文字ちょうど"""
        request = AccountRequest(
            email="test@example.com",
            tool="trello",
            background="あ" * 255
        )
        assert len(request.background) == 255


class TestConversationState:
    """ConversationStateモデルのテスト"""

    def test_initial_state(self):
        """初期状態のテスト"""
        state = ConversationState()
        assert state.email is None
        assert state.tool is None
        assert state.permission is None
        assert state.background is None
        assert not state.is_complete()

    def test_incomplete_state_no_email(self):
        """不完全な状態: メールアドレスなし"""
        state = ConversationState(
            tool="trello",
            background="テスト"
        )
        assert not state.is_complete()

    def test_incomplete_state_no_tool(self):
        """不完全な状態: ツールなし"""
        state = ConversationState(
            email="test@example.com",
            background="テスト"
        )
        assert not state.is_complete()

    def test_incomplete_state_no_background(self):
        """不完全な状態: 背景なし"""
        state = ConversationState(
            email="test@example.com",
            tool="trello"
        )
        assert not state.is_complete()

    def test_complete_state_trello(self):
        """完全な状態: Trello"""
        state = ConversationState(
            email="test@example.com",
            tool="trello",
            background="テスト"
        )
        assert state.is_complete()

    def test_incomplete_state_google_drive_no_permission(self):
        """不完全な状態: Google Driveで権限なし"""
        state = ConversationState(
            email="test@example.com",
            tool="google_drive",
            background="テスト"
        )
        assert not state.is_complete()

    def test_complete_state_google_drive(self):
        """完全な状態: Google Drive"""
        state = ConversationState(
            email="test@example.com",
            tool="google_drive",
            permission="reader",
            background="テスト"
        )
        assert state.is_complete()

    def test_to_account_request_trello(self):
        """AccountRequestへの変換: Trello"""
        state = ConversationState(
            email="test@example.com",
            tool="trello",
            background="テスト"
        )
        request = state.to_account_request()
        assert isinstance(request, AccountRequest)
        assert request.email == "test@example.com"
        assert request.tool == "trello"
        assert request.permission is None

    def test_to_account_request_google_drive(self):
        """AccountRequestへの変換: Google Drive"""
        state = ConversationState(
            email="viewer@example.com",
            tool="google_drive",
            permission="reader",
            background="閲覧のため"
        )
        request = state.to_account_request()
        assert isinstance(request, AccountRequest)
        assert request.permission == "reader"
