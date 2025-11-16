"""
LangChain セットアップ
Gemini APIの初期化と会話状態の管理
"""

import os
import re
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI

from src.models import ConversationState


class ChatbotManager:
    """チャットボットの状態管理クラス"""

    def __init__(self):
        self.llm = None
        self.state = ConversationState()
        self.initialize_llm()

    def initialize_llm(self):
        """Gemini LLMを初期化"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません。")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )

    def reset_conversation(self):
        """会話をリセット"""
        self.state = ConversationState()

    def extract_information(self, user_input: str) -> Dict[str, Any]:
        """
        ユーザー入力から情報を抽出

        Args:
            user_input: ユーザーの入力テキスト

        Returns:
            抽出された情報
        """
        extracted = {}

        # メールアドレスの抽出
        if not self.state.email:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_input)
            if emails:
                extracted['email'] = emails[0]

        # ツールの抽出
        if not self.state.tool:
            user_lower = user_input.lower()
            if 'trello' in user_lower or 'トレロ' in user_input:
                extracted['tool'] = 'trello'
            elif 'google drive' in user_lower or 'googledrive' in user_lower or \
                 'グーグルドライブ' in user_input or 'ドライブ' in user_input:
                extracted['tool'] = 'google_drive'

        # 権限の抽出（Google Driveの場合）
        if self.state.tool == 'google_drive' and not self.state.permission:
            user_lower = user_input.lower()
            if 'reader' in user_lower or '閲覧' in user_input or 'リーダー' in user_input:
                extracted['permission'] = 'reader'
            elif 'commenter' in user_lower or 'コメント' in user_input or 'コメンター' in user_input:
                extracted['permission'] = 'commenter'
            elif 'writer' in user_lower or '編集' in user_input or 'ライター' in user_input:
                extracted['permission'] = 'writer'

        # 背景の抽出（他の情報が揃っている場合）
        if self.state.email and self.state.tool and not self.state.background:
            if self.state.tool == 'trello' or (self.state.tool == 'google_drive' and self.state.permission):
                # ユーザー入力全体を背景として扱う（255文字まで）
                background = user_input.strip()[:255]
                if len(background) > 0:
                    extracted['background'] = background

        return extracted

    def update_state(self, extracted_info: Dict[str, Any]) -> Dict[str, str]:
        """
        状態を更新し、バリデーションを実行

        Args:
            extracted_info: 抽出された情報

        Returns:
            バリデーションエラー
        """
        errors = {}

        # メールアドレスの更新
        if 'email' in extracted_info:
            try:
                # 簡易的なメール検証
                email = extracted_info['email']
                if '@' in email and '.' in email.split('@')[1]:
                    self.state.email = email
                else:
                    errors['email'] = '正しいメールアドレスの形式で入力してください。'
            except Exception as e:
                errors['email'] = '正しいメールアドレスの形式で入力してください。'

        # ツールの更新
        if 'tool' in extracted_info:
            self.state.tool = extracted_info['tool']

        # 権限の更新
        if 'permission' in extracted_info:
            self.state.permission = extracted_info['permission']

        # 背景の更新
        if 'background' in extracted_info:
            background = extracted_info['background']
            if len(background) > 255:
                errors['background'] = f'背景は255文字以内で入力してください。現在の文字数: {len(background)}文字'
            elif len(background.strip()) == 0:
                errors['background'] = '背景を入力してください。'
            else:
                self.state.background = background

        return errors

    def get_next_question(self) -> Optional[str]:
        """
        次に尋ねるべき質問を取得

        Returns:
            次の質問、または None（全ての情報が揃っている場合）
        """
        from src.prompts import QUESTIONS

        if not self.state.email:
            return QUESTIONS['email']
        elif not self.state.tool:
            return QUESTIONS['tool']
        elif self.state.tool == 'google_drive' and not self.state.permission:
            return QUESTIONS['permission']
        elif not self.state.background:
            return QUESTIONS['background']
        return None

    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        ユーザー入力を処理

        Args:
            user_input: ユーザーの入力

        Returns:
            処理結果
        """
        # 情報の抽出
        extracted = self.extract_information(user_input)

        # 状態の更新
        errors = self.update_state(extracted)

        # エラーがある場合
        if errors:
            return {
                'status': 'error',
                'errors': errors,
                'extracted': extracted
            }

        # 次の質問を取得
        next_question = self.get_next_question()

        # 全ての情報が揃っている場合
        if next_question is None and self.state.is_complete():
            return {
                'status': 'complete',
                'state': self.state
            }

        # まだ情報が必要な場合
        return {
            'status': 'continue',
            'next_question': next_question,
            'extracted': extracted
        }
