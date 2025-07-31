# -*- coding: utf-8 -*-
import argparse
import sys
import os
import google.generativeai as genai # pip install google-generativeai
from dotenv import load_dotenv

os.environ["PYTHONIOENCODING"] = "utf-8"
print(os.getenv("PYTHONIOENCODING"))
load_dotenv()

genai.configure(
    api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
    client_options={"quota_project_id": os.environ.get("GOOGLE_CLOUD_PROJECT")}
)
def call_llm_gemini(prompt_text: str, model: str = "gemini-pro") -> str:
    """
    Gemini LLMにリクエストを送信し、結果を返す関数
    """
    try:
        # モデルをロード
        model_instance = genai.GenerativeModel(model)

        # コンテンツ生成
        response = model_instance.generate_content(prompt_text)

        # 応答を返す
        return response.text
    except Exception as e:
        return f"Gemini LLM呼び出し中にエラーが発生しました: {e}"

def main():
    parser = argparse.ArgumentParser(description="Google Gemini LLMを活用したCLIアプリケーション")
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        default="以下のテキストを処理してください:", # デフォルトのプロンプト
        help="LLMに与えるプロンプト。入力テキストと結合されます。"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="処理するテキストファイルのパス。"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="gemini-2.0-flash",
        help="使用するGemini LLMのモデル名 (例: gemini-2.0-flash)。"
    )

    args = parser.parse_args()

    input_text = ""
    if args.file:
        if not os.path.exists(args.file):
            print(f"エラー: 指定されたファイル '{args.file}' が見つかりません。", file=sys.stderr)
            sys.exit(1)
        with open(args.file, 'r', encoding='utf-8') as f:
            input_text = f.read()
    else:
        # ファイルが指定されていない場合は標準入力から読み込む
        if sys.stdin.isatty():
            # 標準入力が端末に接続されている場合（直接実行の場合）は、入力を促す
            print("テキストを入力してください (入力終了はCtrl+D / Ctrl+Z):")
        input_text = sys.stdin.read()

    if not input_text.strip():
        print("エラー: 処理する入力テキストがありません。", file=sys.stderr)
        sys.exit(1)

    # プロンプトと入力を結合
    full_prompt = f"{args.prompt}\n\n{input_text}"

    print(f"\n--- Gemini LLMに送信中のプロンプト（一部）---\n{full_prompt[:200]}...\n------------------------------------")

    # Gemini LLMを呼び出し
    response_content = call_llm_gemini(full_prompt, model=args.model)

    # 結果を出力
    print("\n--- Gemini LLMからの応答 ---")
    print(response_content)
    print("-------------------------")

if __name__ == "__main__":
    main()