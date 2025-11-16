"""
アカウント発行依頼チャットボット - Streamlit UI
"""

import os
import streamlit as st
from dotenv import load_dotenv

from src.langchain_setup import ChatbotManager
from src.api_clients import execute_account_request
from src.prompts import GREETING_MESSAGE, ERROR_MESSAGES, get_completion_message

# 環境変数の読み込み
load_dotenv()


def initialize_session_state():
    """セッション状態を初期化"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chatbot_manager" not in st.session_state:
        st.session_state.chatbot_manager = ChatbotManager()

    if "conversation_active" not in st.session_state:
        st.session_state.conversation_active = True

    if "api_executing" not in st.session_state:
        st.session_state.api_executing = False


def reset_conversation():
    """会話をリセット"""
    st.session_state.messages = []
    st.session_state.chatbot_manager.reset_conversation()
    st.session_state.conversation_active = True
    st.session_state.api_executing = False


def display_sidebar():
    """サイドバーを表示"""
    with st.sidebar:
        st.header("対応ツール")
        st.markdown("""
        - **Trello**: プロジェクト管理ツール
        - **Google Drive**: ファイル共有・ストレージ
        """)

        st.header("使い方")
        st.markdown("""
        1. メールアドレスを入力
        2. 必要なツールを選択
        3. Google Driveの場合は権限を選択
        4. 背景・理由を入力
        5. 自動でアカウントを発行
        """)

        st.divider()

        if st.button("会話をリセット", type="secondary", use_container_width=True):
            reset_conversation()
            st.rerun()

        st.divider()
        st.caption("v1.0.0 - Powered by Gemini & LangChain")


def generate_bot_response(user_input: str) -> str:
    """
    ボットの応答を生成

    Args:
        user_input: ユーザーの入力

    Returns:
        ボットの応答
    """
    manager = st.session_state.chatbot_manager

    # ユーザー入力を処理
    result = manager.process_user_input(user_input)

    # エラーがある場合
    if result['status'] == 'error':
        error_messages = []
        for field, error in result['errors'].items():
            error_messages.append(error)
        return "\n\n".join(error_messages)

    # 情報が全て揃った場合
    if result['status'] == 'complete':
        return "情報が全て揃いました。アカウント発行を実行します..."

    # 次の質問を返す
    if 'next_question' in result:
        # 抽出された情報を確認
        extracted = result.get('extracted', {})
        confirmation = ""

        if 'email' in extracted:
            confirmation += f"メールアドレス: {extracted['email']} を確認しました。\n\n"
        if 'tool' in extracted:
            tool_name = "Trello" if extracted['tool'] == 'trello' else "Google Drive"
            confirmation += f"ツール: {tool_name} を確認しました。\n\n"
        if 'permission' in extracted:
            permission_names = {
                'reader': '閲覧のみ',
                'commenter': 'コメント可',
                'writer': '編集可'
            }
            confirmation += f"権限: {permission_names.get(extracted['permission'], extracted['permission'])} を確認しました。\n\n"

        return confirmation + result['next_question']

    return "申し訳ございません。処理中にエラーが発生しました。"


def execute_api_call():
    """API呼び出しを実行"""
    manager = st.session_state.chatbot_manager
    state = manager.state

    try:
        # API実行
        result = execute_account_request(
            email=state.email,
            tool=state.tool,
            background=state.background,
            permission=state.permission
        )

        if result['success']:
            # 成功メッセージ
            completion_msg = get_completion_message(
                tool=state.tool,
                email=state.email,
                background=state.background,
                permission=state.permission
            )
            return completion_msg
        else:
            # エラーメッセージ
            error_msg = ERROR_MESSAGES['api_error'].format(
                error_details=result.get('error', '不明なエラー')
            )
            return error_msg

    except Exception as e:
        error_msg = ERROR_MESSAGES['api_error'].format(
            error_details=str(e)
        )
        return error_msg


def main():
    """メイン関数"""
    # ページ設定
    st.set_page_config(
        page_title="アカウント発行依頼チャットボット",
        page_icon="🤖",
        layout="wide"
    )

    # セッション状態の初期化
    initialize_session_state()

    # サイドバー表示
    display_sidebar()

    # メインコンテンツ
    st.title("🤖 アカウント発行依頼チャットボット")
    st.caption("TrelloとGoogle Driveのアカウント発行を自動化します")

    # 初回の挨拶メッセージを表示
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "assistant",
            "content": GREETING_MESSAGE
        })

    # チャット履歴を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください..."):
        # ユーザーメッセージを追加
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ボット応答を生成
        with st.chat_message("assistant"):
            with st.spinner("考え中..."):
                response = generate_bot_response(prompt)

                # 情報が全て揃った場合、API実行
                if response == "情報が全て揃いました。アカウント発行を実行します...":
                    st.markdown(response)

                    # API実行
                    with st.spinner("アカウント発行中..."):
                        api_response = execute_api_call()
                        response = api_response

                st.markdown(response)

        # ボットメッセージを追加
        st.session_state.messages.append({"role": "assistant", "content": response})

        # API実行後、会話をリセット（次の依頼を受け付ける準備）
        if "アカウント発行が完了しました" in response:
            # 状態をリセット（メッセージ履歴は保持）
            st.session_state.chatbot_manager.reset_conversation()


if __name__ == "__main__":
    main()
