"""
API クライアント
Trello API と Google Drive API の呼び出しを管理
"""

import os
import requests
from typing import Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class TrelloAPIClient:
    """Trello API クライアント"""

    def __init__(self):
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.api_token = os.getenv("TRELLO_API_TOKEN")
        self.board_id = os.getenv("TRELLO_BOARD_ID")

        if not all([self.api_key, self.api_token, self.board_id]):
            raise ValueError("Trello API の環境変数が設定されていません。")

    def add_member_to_board(self, email: str) -> Dict[str, Any]:
        """
        ボードにメンバーを追加

        Args:
            email: 追加するメンバーのメールアドレス

        Returns:
            APIレスポンス

        Raises:
            Exception: API呼び出しエラー
        """
        url = f"https://api.trello.com/1/boards/{self.board_id}/members"

        params = {
            "email": email,
            "type": "normal",
            "key": self.api_key,
            "token": self.api_token
        }

        try:
            response = requests.put(url, params=params, timeout=30)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_message = f"{error_message}\n詳細: {error_detail}"
                except:
                    error_message = f"{error_message}\nステータスコード: {e.response.status_code}"
            raise Exception(f"Trello APIエラー: {error_message}")


class GoogleDriveAPIClient:
    """Google Drive API クライアント"""

    def __init__(self):
        self.file_id = os.getenv("GOOGLE_DRIVE_FILE_ID")
        self.service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

        if not all([self.file_id, self.service_account_file]):
            raise ValueError("Google Drive API の環境変数が設定されていません。")

        if not os.path.exists(self.service_account_file):
            raise ValueError(f"サービスアカウントファイルが見つかりません: {self.service_account_file}")

        # サービスアカウント認証
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)

    def add_permission(self, email: str, role: str) -> Dict[str, Any]:
        """
        ファイルに権限を追加

        Args:
            email: 権限を付与するユーザーのメールアドレス
            role: 権限の種類 (reader, commenter, writer)

        Returns:
            APIレスポンス

        Raises:
            Exception: API呼び出しエラー
        """
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }

        try:
            result = self.service.permissions().create(
                fileId=self.file_id,
                body=permission,
                sendNotificationEmail=True,
                fields='id'
            ).execute()
            return {"success": True, "data": result}
        except HttpError as e:
            error_message = f"Google Drive APIエラー: {str(e)}"
            if e.resp.status == 404:
                error_message += "\nファイルが見つかりません。GOOGLE_DRIVE_FILE_IDを確認してください。"
            elif e.resp.status == 403:
                error_message += "\n権限がありません。サービスアカウントの権限を確認してください。"
            raise Exception(error_message)
        except Exception as e:
            raise Exception(f"Google Drive APIエラー: {str(e)}")


def execute_account_request(email: str, tool: str, background: str, permission: str = None) -> Dict[str, Any]:
    """
    アカウント発行リクエストを実行

    Args:
        email: メールアドレス
        tool: ツール名 (trello または google_drive)
        background: 背景
        permission: 権限 (Google Driveの場合のみ)

    Returns:
        実行結果

    Raises:
        Exception: API実行エラー
    """
    try:
        if tool == "trello":
            client = TrelloAPIClient()
            result = client.add_member_to_board(email)
            return {
                "success": True,
                "tool": "trello",
                "email": email,
                "background": background,
                "result": result
            }
        elif tool == "google_drive":
            if not permission:
                raise ValueError("Google Driveの場合は権限を指定してください。")
            client = GoogleDriveAPIClient()
            result = client.add_permission(email, permission)
            return {
                "success": True,
                "tool": "google_drive",
                "email": email,
                "permission": permission,
                "background": background,
                "result": result
            }
        else:
            raise ValueError(f"未対応のツール: {tool}")
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
