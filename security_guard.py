# -*- coding: utf-8 -*-
import time
import logging
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from llm_guard import scan_prompt, scan_output
from llm_guard.input_scanners import (
    PromptInjection,
    BanSubstrings,
    BanTopics,
    Secrets,
    Toxicity,
)
from llm_guard.output_scanners import (
    BanSubstrings as OutputBanSubstrings,
    Sensitive,
    Toxicity as OutputToxicity,
)


@dataclass
class SecurityConfig:
    """セキュリティ設定クラス"""

    security_level: str = "medium"  # low, medium, high
    enable_input_scanning: bool = True
    enable_output_scanning: bool = True
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    log_security_events: bool = True


class SecurityGuard:
    """LLM-Guardを使用したセキュリティガードクラス"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.request_count = 0
        self.last_request_time = 0
        self.setup_logging()
        self.setup_scanners()

    def setup_logging(self):
        """ログ設定を初期化"""
        if self.config.log_security_events:
            # 既存のハンドラーをクリア
            logging.getLogger().handlers.clear()

            # ファイルハンドラーを設定
            file_handler = logging.FileHandler(
                "security.log", mode="w", encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)

            # コンソールハンドラーを設定
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # フォーマッターを設定
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # ルートロガーを設定
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)

            self.logger = root_logger
        else:
            self.logger = None

    def setup_scanners(self):
        """スキャナーの設定"""
        # 入力スキャナーの設定
        self.input_scanners = []
        if self.config.enable_input_scanning:
            if self.config.security_level in ["medium", "high"]:
                try:
                    self.input_scanners.extend(
                        [
                            PromptInjection(),
                            BanSubstrings(
                                substrings=[
                                    "password",
                                    "secret",
                                    "key",
                                    "token",
                                    "api_key",
                                    "private_key",
                                ]
                            ),
                            Secrets(),
                        ]
                    )
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"入力スキャナーの初期化に失敗: {e}")

            if self.config.security_level == "high":
                try:
                    self.input_scanners.extend(
                        [
                            BanTopics(
                                topics=["violence", "hate", "self-harm", "suicide"]
                            ),
                            Toxicity(),  # Toxicityスキャナーを追加
                        ]
                    )
                except Exception as e:
                    if self.logger:
                        self.logger.warning(
                            f"高レベル入力スキャナーの初期化に失敗: {e}"
                        )

        # 出力スキャナーの設定
        self.output_scanners = []
        if self.config.enable_output_scanning:
            if self.config.security_level in ["medium", "high"]:
                try:
                    self.output_scanners.extend(
                        [
                            OutputBanSubstrings(
                                substrings=[
                                    "password",
                                    "secret",
                                    "key",
                                    "token",
                                    "api_key",
                                    "private_key",
                                ]
                            ),
                            Sensitive(),
                        ]
                    )
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"出力スキャナーの初期化に失敗: {e}")

            if self.config.security_level == "high":
                try:
                    self.output_scanners.extend(
                        [
                            OutputToxicity(),  # 出力用Toxicityスキャナーを追加
                        ]
                    )
                except Exception as e:
                    if self.logger:
                        self.logger.warning(
                            f"高レベル出力スキャナーの初期化に失敗: {e}"
                        )

    def check_rate_limit(self) -> bool:
        """レート制限チェック（改善版）"""
        if not self.config.enable_rate_limiting:
            return True

        current_time = time.time()
        time_diff = current_time - self.last_request_time

        # 1分間の制限チェック
        if time_diff < 60:
            if self.request_count >= self.config.max_requests_per_minute:
                if self.logger:
                    self.logger.warning(
                        f"レート制限に達しました: {self.config.max_requests_per_minute} requests/min"
                    )
                return False
        else:
            # 1分経過したらリセット
            self.request_count = 0

        self.request_count += 1
        self.last_request_time = current_time
        return True

    def _process_scan_result(
        self, scan_result, default_text: str
    ) -> Tuple[bool, str, float, Dict[str, Any]]:
        """スキャン結果を統一された形式で処理"""

        def _has_invalid(results):
            if isinstance(results, dict) and "is_valid" in results:
                return results["is_valid"] is False
            if isinstance(results, dict):
                for v in results.values():
                    if _has_invalid(v):
                        return True
            elif isinstance(results, list):
                for v in results:
                    if _has_invalid(v):
                        return True
            elif isinstance(results, bool):
                return results is False
            return False

        try:
            # 戻り値の構造を確認して適切に処理
            if hasattr(scan_result, "is_valid"):
                # 新しい形式（オブジェクト）
                is_valid = scan_result.is_valid
                sanitized_text = getattr(scan_result, "sanitized_prompt", default_text)
                if not sanitized_text:
                    sanitized_text = getattr(
                        scan_result, "sanitized_output", default_text
                    )
                risk_score = getattr(scan_result, "risk_score", 0.0)
                scanners_results = getattr(scan_result, "scanners_results", {})
            elif isinstance(scan_result, dict):
                # 辞書形式の戻り値（LLM-Guard 0.3.16以降）
                is_valid = scan_result.get("is_valid", True)
                sanitized_text = scan_result.get("sanitized_prompt", default_text)
                if not sanitized_text:
                    sanitized_text = scan_result.get("sanitized_output", default_text)
                risk_score = scan_result.get("risk_score", 0.0)
                scanners_results = scan_result.get("scanners_results", {})
            elif isinstance(scan_result, (list, tuple)):
                # 古い形式（タプル/リスト）
                if len(scan_result) >= 3:
                    sanitized_text, scanners_results, scores = scan_result[:3]
                    # scanners_resultsのis_valid値を総合判定
                    if isinstance(scanners_results, dict):
                        # 1つでもFalseがあれば全体をFalse
                        is_valid = all(scanners_results.values())
                    else:
                        is_valid = True
                    risk_score = max(scores.values()) if scores else 0.0
                else:
                    is_valid = True
                    sanitized_text = default_text
                    risk_score = 0.0
                    scanners_results = {}
            else:
                # 予期しない形式の場合
                is_valid = True
                sanitized_text = default_text
                risk_score = 0.0
                scanners_results = {}

            # risk_scoreが辞書型の場合の処理
            if isinstance(risk_score, dict):
                # 辞書から最大値を取得
                if risk_score:
                    risk_score = max(risk_score.values())
                else:
                    risk_score = 0.0
            elif not isinstance(risk_score, (int, float)):
                # 数値以外の場合は0.0に設定
                risk_score = 0.0

            # is_validの判定を強化
            if isinstance(is_valid, bool):
                if _has_invalid(scanners_results):
                    is_valid = False
            elif isinstance(is_valid, (int, float)):
                is_valid = is_valid <= -1.0
            else:
                is_valid = True

            return is_valid, sanitized_text, float(risk_score), scanners_results

        except Exception as e:
            if self.logger:
                self.logger.error(f"スキャン結果の処理中にエラー: {e}")
            # エラーが発生した場合は安全のためブロック
            return False, default_text, 1.0, {"error": str(e)}

    def scan_input(self, prompt: str) -> Tuple[bool, str, Dict[str, Any]]:
        """入力テキストのスキャン（改善版）"""
        if not self.config.enable_input_scanning or not self.input_scanners:
            return True, prompt, {}

        try:
            # LLM-Guardのスキャンを実行
            scan_result = scan_prompt(self.input_scanners, prompt)

            # デバッグ: scan_resultの構造を確認
            if self.logger:
                self.logger.info(f"scan_result type: {type(scan_result)}")
                self.logger.info(f"scan_result: {scan_result}")

            # 結果を処理
            is_valid, sanitized_prompt, risk_score, scanners_results = (
                self._process_scan_result(scan_result, prompt)
            )

            if self.logger:
                self.logger.debug(f"scanners_results: {scanners_results}")
                if risk_score > 0.5:
                    self.logger.warning(f"入力スキャンでリスク検出: {risk_score}")
                else:
                    self.logger.info(f"入力スキャン完了: リスクスコア {risk_score}")

            # デバッグ情報を追加
            if self.logger:
                self.logger.debug(
                    f"スキャン結果: is_valid={is_valid}, risk_score={risk_score}"
                )

            return (
                is_valid,
                sanitized_prompt,
                {
                    "risk_score": risk_score,
                    "scanners_results": scanners_results,
                },
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"入力スキャン中にエラー: {e}")
                import traceback

                self.logger.error(f"詳細エラー: {traceback.format_exc()}")
            # エラーが発生した場合は安全のためブロック
            return False, "", {"error": str(e)}

    def scan_output(self, output: str, original_prompt: str = "") -> Tuple[bool, str, Dict[str, Any]]:
        """出力テキストのスキャン（改善版）"""
        if not self.config.enable_output_scanning or not self.output_scanners:
            return True, output, {}

        try:
            # LLM-Guardのスキャンを実行（正しい引数順序）
            from llm_guard import scan_output as llm_guard_scan_output
            scan_result = llm_guard_scan_output(
                scanners=self.output_scanners,
                prompt=original_prompt,
                output=output,
                fail_fast=False
            )

            # 結果を処理
            is_valid, sanitized_output, risk_score, scanners_results = (
                self._process_scan_result(scan_result, output)
            )

            if self.logger:
                if risk_score > 0.5:
                    self.logger.warning(f"出力スキャンでリスク検出: {risk_score}")
                else:
                    self.logger.info(f"出力スキャン完了: リスクスコア {risk_score}")

            # デバッグ情報を追加
            if self.logger:
                self.logger.debug(
                    f"スキャン結果: is_valid={is_valid}, risk_score={risk_score}"
                )

            return (
                is_valid,
                sanitized_output,
                {
                    "risk_score": risk_score,
                    "scanners_results": scanners_results,
                },
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"出力スキャン中にエラー: {e}")
                import traceback

                self.logger.error(f"詳細エラー: {traceback.format_exc()}")
            # エラーが発生した場合は安全のためブロック
            return False, "", {"error": str(e)}

    def validate_request(self, prompt: str) -> Tuple[bool, str, Dict[str, Any]]:
        """リクエストの完全な検証（改善版）"""
        # レート制限チェック
        if not self.check_rate_limit():
            return False, "", {"error": "レート制限に達しました"}

        # 入力スキャン
        is_valid, sanitized_prompt, scan_info = self.scan_input(prompt)

        if not is_valid:
            return (
                False,
                "",
                {
                    "error": "入力がセキュリティポリシーに違反しています",
                    "scan_info": scan_info,
                },
            )

        return True, sanitized_prompt, scan_info

    def validate_response(self, response: str, original_prompt: str = "") -> Tuple[bool, str, Dict[str, Any]]:
        """レスポンスの検証（改善版）"""
        is_valid, sanitized_response, scan_info = self.scan_output(response, original_prompt)

        if not is_valid:
            return (
                False,
                "",
                {
                    "error": "出力がセキュリティポリシーに違反しています",
                    "scan_info": scan_info,
                },
            )

        return True, sanitized_response, scan_info
