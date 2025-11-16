"""
Pydanticモデル定義
アカウント発行依頼に必要なデータ構造を定義
"""

from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class AccountRequest(BaseModel):
    """アカウント発行依頼のデータモデル"""

    email: EmailStr = Field(description="ユーザーのメールアドレス")
    tool: Literal["trello", "google_drive"] = Field(description="必要なツール")
    permission: Optional[Literal["reader", "commenter", "writer"]] = Field(
        None, description="Google Drive権限（Google Driveのみ）"
    )
    background: str = Field(
        description="アカウントが必要な背景（最大255文字）",
        max_length=255
    )

    @field_validator("background")
    @classmethod
    def validate_background(cls, v: str) -> str:
        """背景の文字数をバリデーション"""
        if len(v) > 255:
            raise ValueError("背景は255文字以内で入力してください。")
        if not v.strip():
            raise ValueError("背景を入力してください。")
        return v

    @field_validator("permission")
    @classmethod
    def validate_permission(cls, v: Optional[str], info) -> Optional[str]:
        """Google Driveの場合は権限が必須"""
        # info.dataを使って他のフィールドの値にアクセス
        data = info.data
        if "tool" in data and data["tool"] == "google_drive" and not v:
            raise ValueError("Google Driveの場合は権限を選択してください。")
        return v


class ConversationState(BaseModel):
    """会話の状態を管理するモデル"""

    email: Optional[EmailStr] = None
    tool: Optional[Literal["trello", "google_drive"]] = None
    permission: Optional[Literal["reader", "commenter", "writer"]] = None
    background: Optional[str] = None

    def is_complete(self) -> bool:
        """必要な情報が全て揃っているかチェック"""
        if not self.email or not self.tool or not self.background:
            return False
        if self.tool == "google_drive" and not self.permission:
            return False
        return True

    def to_account_request(self) -> AccountRequest:
        """AccountRequestモデルに変換"""
        return AccountRequest(
            email=self.email,
            tool=self.tool,
            permission=self.permission,
            background=self.background
        )
