# -*- coding: utf-8 -*-
import os
import yaml
from typing import Dict, Any
from security_guard import SecurityConfig


class ConfigLoader:
    """設定ファイル読み込みクラス"""

    def __init__(self, config_path: str = "config/security.yaml"):
        self.config_path = config_path
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                print(
                    f"警告: 設定ファイル '{self.config_path}' が見つかりません。デフォルト設定を使用します。"
                )
                return self._get_default_config()
        except Exception as e:
            print(
                f"警告: 設定ファイルの読み込みに失敗しました: {e}。デフォルト設定を使用します。"
            )
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を返す"""
        return {
            "default": {
                "security_level": "medium",
                "enable_input_scanning": True,
                "enable_output_scanning": True,
                "enable_rate_limiting": True,
                "max_requests_per_minute": 60,
                "log_security_events": True,
            },
            "security_levels": {
                "low": {
                    "enable_input_scanning": False,
                    "enable_output_scanning": False,
                    "enable_rate_limiting": True,
                    "max_requests_per_minute": 120,
                },
                "medium": {
                    "enable_input_scanning": True,
                    "enable_output_scanning": True,
                    "enable_rate_limiting": True,
                    "max_requests_per_minute": 60,
                },
                "high": {
                    "enable_input_scanning": True,
                    "enable_output_scanning": True,
                    "enable_rate_limiting": True,
                    "max_requests_per_minute": 30,
                },
            },
        }

    def get_security_config(
        self, security_level: str = "medium", enable_guard: bool = True
    ) -> SecurityConfig:
        """セキュリティ設定を取得"""
        if not enable_guard:
            return SecurityConfig(
                enable_input_scanning=False,
                enable_output_scanning=False,
                enable_rate_limiting=False,
                log_security_events=False,
            )

        # デフォルト設定を取得
        default_config = self.config_data.get("default", {})

        # セキュリティレベル別設定を取得
        level_config = self.config_data.get("security_levels", {}).get(
            security_level, {}
        )

        # 設定をマージ
        config_dict = {**default_config, **level_config}

        return SecurityConfig(
            security_level=security_level,
            enable_input_scanning=config_dict.get("enable_input_scanning", True),
            enable_output_scanning=config_dict.get("enable_output_scanning", True),
            enable_rate_limiting=config_dict.get("enable_rate_limiting", True),
            max_requests_per_minute=config_dict.get("max_requests_per_minute", 60),
            log_security_events=config_dict.get("log_security_events", True),
        )

    def get_custom_rules(self) -> Dict[str, Any]:
        """カスタムルールを取得"""
        return self.config_data.get("custom_rules", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定を取得"""
        return self.config_data.get("logging", {})

    def get_rate_limiting_config(self) -> Dict[str, Any]:
        """レート制限設定を取得"""
        return self.config_data.get("rate_limiting", {})

    def validate_config(self) -> bool:
        """設定の妥当性を検証"""
        try:
            # 必須設定の確認
            required_keys = ["default", "security_levels"]
            for key in required_keys:
                if key not in self.config_data:
                    print(f"エラー: 必須設定 '{key}' が見つかりません。")
                    return False

            # セキュリティレベルの確認
            security_levels = self.config_data.get("security_levels", {})
            required_levels = ["low", "medium", "high"]
            for level in required_levels:
                if level not in security_levels:
                    print(
                        f"エラー: セキュリティレベル '{level}' の設定が見つかりません。"
                    )
                    return False

            return True

        except Exception as e:
            print(f"設定の検証中にエラーが発生しました: {e}")
            return False

    def reload_config(self):
        """設定を再読み込み"""
        self.config_data = self._load_config()
        if not self.validate_config():
            print("警告: 設定の再読み込みに失敗しました。")
