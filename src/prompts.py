"""
プロンプトテンプレート定義
チャットボットのシステムプロンプトと質問テンプレート
"""

# システムプロンプト
SYSTEM_PROMPT = """あなたはアカウント発行を支援する親切なチャットボットです。
ユーザーから以下の情報を丁寧に収集してください：

1. メールアドレス
2. 必要なツール（Trello または Google Drive）
3. Google Driveの場合は権限（reader, commenter, writer）
4. アカウントが必要な背景（最大255文字）

制約:
- 必ず一つずつ質問し、ユーザーの回答を待ってから次へ進む
- フレンドリーで丁寧な口調を使用する
- バリデーションエラーは理由を明確に説明する
- 確認画面は不要、情報が揃ったら即座にAPI実行を伝える
- ユーザーが入力した情報を整理して確認する
- 会話の文脈を理解し、自然な対話を心がける

重要なルール:
- メールアドレスは正しい形式で入力されているか確認する
- 背景は255文字以内であることを確認する
- Google Driveを選択した場合は、必ず権限を確認する
- Trelloを選択した場合は、権限の質問をスキップする
"""

# 挨拶メッセージ
GREETING_MESSAGE = """こんにちは！ アカウント発行依頼チャットボットです。

TrelloまたはGoogle Driveのアカウント発行をお手伝いします。
いくつか質問させていただきますので、順番にお答えください。

まず、アカウントが必要な方のメールアドレスを教えてください。"""

# 質問テンプレート
QUESTIONS = {
    "email": "アカウントが必要な方のメールアドレスを教えてください。",
    "tool": "どのツールが必要ですか？ 以下から選択してください：\n- Trello\n- Google Drive",
    "permission": "Google Driveの権限を選択してください：\n- reader（閲覧のみ）\n- commenter（コメント可）\n- writer（編集可）",
    "background": "このツールが必要な理由や背景を教えてください。（最大255文字）"
}

# エラーメッセージ
ERROR_MESSAGES = {
    "invalid_email": "正しいメールアドレスの形式で入力してください。（例: user@example.com）",
    "invalid_tool": "TrelloまたはGoogle Driveのいずれかを選択してください。",
    "invalid_permission": "reader、commenter、writerのいずれかを選択してください。",
    "background_too_long": "背景は255文字以内で入力してください。現在の文字数: {count}文字",
    "background_empty": "背景を入力してください。",
    "api_error": """エラーが発生しました。
{error_details}
もう一度お試しいただくか、管理者にお問い合わせください。"""
}

# 完了メッセージ
COMPLETION_MESSAGES = {
    "trello": """アカウント発行が完了しました！

【発行内容】
- ツール: Trello
- メールアドレス: {email}
- 背景: {background}

{email} 宛にTrelloの招待メールが送信されます。
メールを確認して、アカウントの設定を完了してください。

他にアカウント発行が必要な方はいらっしゃいますか？
必要であれば、再度メールアドレスから教えてください。""",

    "google_drive": """アカウント発行が完了しました！

【発行内容】
- ツール: Google Drive
- メールアドレス: {email}
- 権限: {permission}
- 背景: {background}

{email} に Google Drive への{permission_ja}権限が付与されました。
すぐにアクセス可能になります。

他にアカウント発行が必要な方はいらっしゃいますか？
必要であれば、再度メールアドレスから教えてください。"""
}

# 権限の日本語表記
PERMISSION_JAPANESE = {
    "reader": "閲覧",
    "commenter": "コメント",
    "writer": "編集"
}


def get_completion_message(tool: str, email: str, background: str, permission: str = None) -> str:
    """完了メッセージを生成"""
    if tool == "trello":
        return COMPLETION_MESSAGES["trello"].format(
            email=email,
            background=background
        )
    else:  # google_drive
        return COMPLETION_MESSAGES["google_drive"].format(
            email=email,
            permission=permission,
            permission_ja=PERMISSION_JAPANESE.get(permission, permission),
            background=background
        )
