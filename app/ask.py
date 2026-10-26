"""第1回 宿題（実装）: 会話履歴を保ったまま続けて質問できるスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"   # 最初の質問を指定して会話を開始
    uv run python -m app.ask                        # 対話モードで開始

終了するには exit / quit を入力するか、何も入力せずに Enter（または Ctrl+C）。

元の版は1回だけ質問して終わる「素の」呼び出しだった。
この版では client.chats でチャットセッションを作り、
これまでのやり取り（会話履歴）を毎回モデルに渡すことで、前の発言を踏まえて答えられるようにした。
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"

EXIT_WORDS = {"", "exit", "quit", "q"}


def print_usage(response) -> None:
    """1回のやり取りで使ったトークン数を表示する。"""
    usage = response.usage_metadata
    if usage is None:
        print("[トークン] 使用量情報を取得できませんでした")
    else:
        # 履歴を毎回送るので、ターンを重ねるほど入力トークンが増えていく
        print(
            f"[トークン] 入力: {usage.prompt_token_count} / "
            f"出力: {usage.candidates_token_count}"
        )


def chat_loop(first_question: str | None) -> None:
    client = genai.Client(api_key=get_api_key())
    # チャットセッション: 送受信した内容を履歴として内部に保持してくれる
    chat = client.chats.create(model=MODEL)

    question = first_question
    turn = 1
    while True:
        if question is None:
            try:
                question = input(f"\n[質問 {turn}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
        else:
            print(f"\n[質問 {turn}] > {question}")

        if question.lower() in EXIT_WORDS:
            break

        try:
            response = chat.send_message(question)
        except errors.APIError as e:
            # レート制限などで失敗しても会話は終了せず、続けて質問できるようにする
            print(api_error_message(e.code, e.message))
            question = None
            continue

        print()
        print(response.text)
        print_usage(response)

        question = None
        turn += 1

    print(f"会話を終了しました（{len(chat.get_history())} 件のメッセージ）")


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保ったままLLMに質問する")
    parser.add_argument("question", nargs="?", default=None)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print("終了: exit / quit / 空Enter")
    if args.question is None:
        print(f"（例: {DEFAULT_QUESTION}）")

    chat_loop(args.question)


if __name__ == "__main__":
    main()