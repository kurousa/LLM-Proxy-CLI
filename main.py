# -*- coding: utf-8 -*-
import argparse
import sys
import os
import logging
import google.generativeai as genai  # pip install google-generativeai
from dotenv import load_dotenv
from security_guard import SecurityGuard, SecurityConfig
from config_loader import ConfigLoader

# LLM-Guardのログを抑制
logging.getLogger("llm_guard").setLevel(logging.WARNING)
logging.getLogger("llmguard").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

os.environ["PYTHONIOENCODING"] = "utf-8"
print(os.getenv("PYTHONIOENCODING"))
load_dotenv()

genai.configure(
    api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
    client_options={"quota_project_id": os.environ.get("GOOGLE_CLOUD_PROJECT")},
)


def create_security_guard(
    security_level: str, enable_guard: bool, log_security: bool, config_path: str = None
) -> SecurityGuard:
    """セキュリティガードの作成"""
    if not enable_guard:
        config = SecurityConfig(
            enable_input_scanning=False,
            enable_output_scanning=False,
            enable_rate_limiting=False,
            log_security_events=False,
        )
    else:
        # 設定ファイルから設定を読み込み
        config_loader = ConfigLoader(config_path or "config/security.yaml")
        config = config_loader.get_security_config(security_level, enable_guard)
        config.log_security_events = log_security

    return SecurityGuard(config)


def call_llm_gemini(
    prompt_text: str, model: str = "gemini-pro", security_guard: SecurityGuard = None
) -> str:
    """
    Gemini LLMにリクエストを送信し、結果を返す関数
    セキュリティガードが指定されている場合は検証を実行
    """
    try:
        # セキュリティガードが有効な場合、入力検証を実行
        if security_guard:
            is_valid, sanitized_prompt, scan_info = security_guard.validate_request(
                prompt_text
            )

            if not is_valid:
                error_msg = scan_info.get("error", "セキュリティ検証に失敗しました")
                return f"セキュリティエラー: {error_msg}"

            # サニタイズされたプロンプトを使用
            prompt_text = sanitized_prompt

            if scan_info.get("risk_score", 0) > 0.5:
                print(
                    f"⚠️  警告: 入力にリスクが検出されました (スコア: {scan_info['risk_score']:.2f})"
                )

        # モデルをロード
        model_instance = genai.GenerativeModel(model)

        # コンテンツ生成
        response = model_instance.generate_content(prompt_text)

        # セキュリティガードが有効な場合、出力検証を実行
        if security_guard:
            is_valid, sanitized_response, scan_info = security_guard.validate_response(
                response.text
            )

            if not is_valid:
                error_msg = scan_info.get("error", "セキュリティ検証に失敗しました")
                return f"セキュリティエラー: {error_msg}"

            # サニタイズされたレスポンスを使用
            response_text = sanitized_response

            if scan_info.get("risk_score", 0) > 0.5:
                print(
                    f"⚠️  警告: 出力にリスクが検出されました (スコア: {scan_info['risk_score']:.2f})"
                )
        else:
            response_text = response.text

        # 応答を返す
        return response_text

    except Exception as e:
        return f"Gemini LLM呼び出し中にエラーが発生しました: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Google Gemini LLMを活用したCLIアプリケーション（セキュリティ機能付き）"
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        default="以下のテキストを処理してください:",  # デフォルトのプロンプト
        help="LLMに与えるプロンプト。入力テキストと結合されます。",
    )
    parser.add_argument(
        "-f", "--file", type=str, help="処理するテキストファイルのパス。"
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="gemini-2.0-flash",
        help="使用するGemini LLMのモデル名 (例: gemini-2.0-flash)。",
    )
    parser.add_argument(
        "--security-level",
        type=str,
        choices=["low", "medium", "high"],
        default="medium",
        help="セキュリティレベル (low/medium/high)",
    )
    parser.add_argument(
        "--enable-guard",
        action="store_true",
        default=True,
        help="セキュリティガードを有効にする",
    )
    parser.add_argument(
        "--disable-guard", action="store_true", help="セキュリティガードを無効にする"
    )
    parser.add_argument(
        "--log-security",
        action="store_true",
        default=True,
        help="セキュリティイベントをログに記録する",
    )
    parser.add_argument("--config", type=str, help="セキュリティ設定ファイルのパス")

    args = parser.parse_args()

    # セキュリティガードの設定
    enable_guard = args.enable_guard and not args.disable_guard
    security_guard = create_security_guard(
        security_level=args.security_level,
        enable_guard=enable_guard,
        log_security=args.log_security,
        config_path=args.config,
    )

    input_text = ""
    if args.file:
        if not os.path.exists(args.file):
            print(
                f"エラー: 指定されたファイル '{args.file}' が見つかりません。",
                file=sys.stderr,
            )
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
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

    print("\n--- Gemini LLMに送信中のプロンプト（一部）---")
    print(f"セキュリティレベル: {args.security_level}")
    print(f"セキュリティガード: {'有効' if enable_guard else '無効'}")
    if args.config:
        print(f"設定ファイル: {args.config}")
    print(f"{full_prompt[:200]}...")
    print("------------------------------------")

    # Gemini LLMを呼び出し
    response_content = call_llm_gemini(
        full_prompt, model=args.model, security_guard=security_guard
    )

    # 結果を出力
    print("\n--- Gemini LLMからの応答 ---")
    print(response_content)
    print("-------------------------")


if __name__ == "__main__":
    main()
