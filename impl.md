# xoncc プロジェクト実装詳細

## 📁 プロジェクト構造

```
xoncc/
├── 🔧 設定・ビルドファイル
│   ├── pyproject.toml         # パッケージ設定とビルド設定
│   ├── setup.py              # セットアップスクリプト  
│   ├── setup.cfg             # セットアップ設定
│   ├── Makefile              # ビルド・テストタスク
│   └── MANIFEST.in           # パッケージ配布ファイル指定
├── 📚 ドキュメント
│   ├── README.md             # プロジェクト概要
│   ├── CLAUDE.md             # 開発ノート・実装詳細
│   └── DEPLOYMENT.md         # デプロイメント手順
├── 🎯 メインコード
│   ├── scripts/xoncc         # メインコマンドラインスクリプト
│   ├── xoncc/               # Pythonパッケージ
│   └── xontrib/             # xonsh拡張プラグイン
├── 🧪 テスト
│   ├── tests/               # 自動テストスイート
│   └── manual_tests/        # 手動テスト用スクリプト
└── 🔄 CI/CD
    └── .github/workflows/   # GitHub Actions設定
```

---

## 🎯 1. メインコード実装

### 1.1 エントリーポイント

#### `scripts/xoncc` (Shell Script)
```bash
#!/bin/bash
# xonshを起動してxonccプラグインをロード
exec xonsh --rc ~/.xonshrc -D 'xontrib load xoncc'
```

**機能:**
- xonshシェルを起動
- xonccプラグインを自動ロード
- exec使用でシグナル処理を適切に委譲

---

### 1.2 xontrib プラグイン (メインロジック)

#### `xontrib/xoncc.py` - メインプラグイン
**主要関数:**

1. **`call_claude_direct(query: str) -> None`**
   - Claude CLIを直接呼び出し
   - ストリーミングJSON出力を処理
   - ログインエラーの自動検出・回復
   - リアルタイム応答表示

2. **`handle_command_not_found(cmd: List[str], **kwargs) -> Optional[bool]`**
   - command-not-found イベントハンドラー
   - 自然言語クエリをClaudeに転送
   - 一般的なコマンドタイプは除外

3. **`_load_xontrib_(xsh, **kwargs) -> Dict`**
   - プラグイン初期化関数
   - `SubprocSpec._run_binary`の関数オーバーライド実装
   - command-not-foundエラーの無効化
   - 重複ロード防止機能

4. **`xoncc_run_binary(self, kwargs)`**
   - xonshのサブプロセス実行をインターセプト
   - XonshErrorの「command not found」を捕捉
   - 自然言語クエリをClaudeに転送して成功プロセスを返す

#### `xontrib/xoncc_v2.py` - 代替実装（未使用）
**機能:**
- よりシンプルな実装アプローチ
- 現在は使用されていない

---

### 1.3 xoncc パッケージ

#### `xoncc/__init__.py`
```python
__version__ = "0.0.1"
```

#### `xoncc/main.py` - CLI メインエントリー
**主要関数:**
1. **`main()`** - コマンドライン引数解析とClaude呼び出し

#### `xoncc/cc.py` - Claude呼び出しロジック
**主要関数:**
1. **`call_claude(query: str)`** - Claude CLI実行
2. **`extract_session_id(output: str)`** - セッションID抽出

#### `xoncc/cc.sh` - シェルスクリプト版Claude呼び出し
```bash
#!/bin/bash
# Claude CLIのラッパースクリプト
# セッション管理とパイプ処理
```

#### `xoncc/setup_claude.py` - Claude CLI セットアップ
**主要関数:**
1. **`get_user_language()`** - ユーザー言語検出
2. **`check_claude_cli()`** - Claude CLIインストール・ログイン状態確認
3. **`setup_claude_cli()`** - セットアップガイド表示
4. **`open_claude_docs()`** - ブラウザでドキュメント開く

---

### 1.4 フォーマッター (出力整形)

#### `xoncc/formatters/__init__.py`
```python
from .realtime import format_claude_json_stream
```

#### `xoncc/formatters/realtime.py` - リアルタイム出力フォーマッター
**RealtimeClaudeFormatter クラス:**
1. **`process_json_line(line: str)`** - JSON行の処理
2. **`extract_content_from_json(data: Dict)`** - コンテンツ抽出
3. **`extract_usage_info(data: Dict)`** - トークン・コスト情報抽出
4. **`update_token_display(tokens: int)`** - トークンカウンター表示
5. **`finalize_output()`** - 最終サマリー表示

#### `xoncc/formatters/tools.py` - ツール使用フォーマッター
**ToolFormatter クラス:**
1. **`format_tool_use(data: Dict)`** - ツール実行時フォーマット
2. **`format_tool_result(data: Dict)`** - ツール結果フォーマット
3. **`format_thinking(data: Dict)`** - AI思考過程フォーマット

#### `xoncc/formatters/log.py` - ログフォーマッター
**LogFormatter クラス:**
1. **`format_log_entry(data: Dict)`** - ログエントリーフォーマット
2. **`format_timestamp(timestamp: str)`** - タイムスタンプフォーマット

#### `xoncc/claude_json_formatter.py` - レガシーフォーマッター
#### `xoncc/realtime_json_formatter.py` - レガシーフォーマッター

---

## 🧪 2. テスト実装

### 2.1 テスト構造
```
tests/
├── conftest.py              # pytest設定・フィクスチャ
├── dummy_claude/           # ダミーClaude統合テスト
├── integration/            # 統合テスト
├── interactive/            # インタラクティブテスト
└── unit/                   # ユニットテスト
```

### 2.2 ダミーClaude テスト (`tests/dummy_claude/`)

#### `dummy_claude.py` - モックClaude CLI
**機能:**
- 実際のClaude CLIをシミュレート
- ストリーミングJSON応答生成
- テスト環境用

#### `test_claude_cli_integration.py` - Claude CLI統合テスト
**テストクラス: TestClaudeCLIIntegration**
1. `test_claude_cli_available()` - Claude CLI可用性テスト
2. `test_claude_cli_version()` - バージョンチェックテスト
3. `test_call_claude_direct_real()` - 直接呼び出しテスト
4. `test_auto_login_flow()` - 自動ログインフローテスト

#### `test_xoncc_simple.py` - シンプルなxonccテスト
**テストクラス: TestXonccSimple**
1. `test_call_claude()` - Claude呼び出しテスト
2. `test_session_resume()` - セッション継続テスト
3. `test_handle_command_not_found()` - command-not-foundハンドラーテスト
4. `test_natural_language_queries()` - 自然言語クエリテスト
5. `test_edge_cases()` - エッジケーステスト
6. `test_skip_common_typos()` - 一般的なタイプミス除外テスト

#### `test_xoncc_minimal.py` - 最小構成テスト
**同様のテスト構成だが、より軽量**

### 2.3 統合テスト (`tests/integration/`)

#### `test_integration.py` - メイン統合テスト
**TestXonccIntegration クラス:**
1. `test_no_error_message_displayed()` - エラーメッセージ非表示テスト
2. `test_function_override_works()` - 関数オーバーライド動作テスト
3. `test_mock_claude_streaming()` - モックClaudeストリーミングテスト
4. `test_normal_commands_unaffected()` - 通常コマンド影響なしテスト
5. `test_multilingual_queries()` - 多言語クエリテスト (英語、日本語、フランス語、ロシア語)

#### `test_ai_response.py` - AI応答テスト
**TestAIResponse クラス:**
1. `test_ai_integration_no_errors()` - AI統合エラーなしテスト
2. `test_function_override_prevents_errors()` - 関数オーバーライドエラー防止テスト
3. `test_normal_commands_still_work()` - 通常コマンド動作テスト
4. `test_real_claude_integration()` - 実Claude統合テスト

#### `test_xoncc_formatters_integration.py` - フォーマッター統合テスト
**TestFormatterIntegration クラス:**
1. `test_realtime_formatter_backward_compatibility()` - リアルタイムフォーマッター後方互換性
2. `test_log_formatter_backward_compatibility()` - ログフォーマッター後方互換性

#### `test_mock_claude_integration.py` - モックClaude統合テスト
1. `test_xoncc_with_mock_claude()` - モックClaudeとの統合テスト

### 2.4 インタラクティブテスト (`tests/interactive/`)

#### `test_xoncc_practical.py` - 実用的テスト
**TestXonccPractical クラス:**
1. `test_xoncc_startup()` - xoncc起動テスト
2. `test_simple_commands_work()` - シンプルコマンド動作テスト
3. `test_python_execution()` - Python実行テスト
4. `test_natural_language_ai_response()` - 自然言語AI応答テスト
5. `test_ctrl_c_handling()` - Ctrl-Cハンドリングテスト (スキップ)
6. `test_ctrl_d_exit()` - Ctrl-D終了テスト
7. `test_shell_functionality_preserved()` - シェル機能保持テスト

#### `test_xoncc_manual.py` - 手動テスト
**機能:**
- 手動実行用テスト関数
- インタラクティブテスト指示
- 実環境テスト向け

#### `test_interactive_simulation.py` - インタラクティブシミュレーション
**機能:**
1. `simulate_claude_streaming_response()` - Claudeストリーミング応答シミュレート
2. `test_interactive_xoncc()` - インタラクティブxonccテスト
3. `test_real_xoncc_behavior()` - 実xoncc動作テスト

#### expectスクリプト
- `test_claude_cli_expect.exp` - Claude CLI expectテスト
- `test_interactive_expect.exp` - インタラクティブexpectテスト

### 2.5 ユニットテスト (`tests/unit/`)

#### `test_formatters_realtime.py` - リアルタイムフォーマッターテスト
**TestRealtimeFormatter クラス:**
1. `test_process_content_block_delta()` - コンテンツブロックデルタ処理
2. `test_process_assistant_message()` - アシスタントメッセージ処理
3. `test_extract_usage_info()` - 使用情報抽出
4. `test_finalize_output()` - 出力最終化
5. `test_clear_current_line()` - 現在行クリア
6. `test_token_display()` - トークン表示

#### `test_formatters_tools.py` - ツールフォーマッターテスト
**TestToolFormatter クラス:**
1. `test_format_tool_use()` - ツール使用フォーマット
2. `test_format_tool_result()` - ツール結果フォーマット
3. `test_format_thinking()` - 思考過程フォーマット

#### `test_formatters_log.py` - ログフォーマッターテスト
**TestLogFormatter クラス:**
1. `test_format_log_entry()` - ログエントリーフォーマット
2. `test_format_timestamp()` - タイムスタンプフォーマット

#### `test_setup_claude.py` - Claude セットアップテスト
**TestSetupClaude クラス:**
1. `test_get_user_language()` - ユーザー言語取得
2. `test_check_claude_cli()` - Claude CLI確認
3. `test_setup_claude_cli()` - Claude CLIセットアップ

#### `test_cc_command.py` - CCコマンドテスト
**TestCCCommand クラス:**
1. `test_call_claude()` - Claude呼び出し
2. `test_extract_session_id()` - セッションID抽出 (スキップ)

#### `test_main.py` - メインモジュールテスト
**TestMain クラス:**
1. `test_main_function()` - main関数テスト
2. `test_argument_parsing()` - 引数解析テスト

### 2.6 テスト設定

#### `tests/conftest.py` - pytest設定
**フィクスチャ:**
1. `dummy_claude_env` - ダミーClaude環境設定
2. `test_environment` - テスト環境設定

---

## 🛠️ 3. 設定・ビルドファイル

### 3.1 パッケージ設定

#### `pyproject.toml` - メイン設定ファイル
```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "xoncc"
version = "0.0.1"
description = "Minimal Claude Code integration for xonsh"
dependencies = [
    "xonsh>=0.13.0",
    "gnureadline>=8.1.2; sys_platform == 'darwin'"
]

[project.scripts]
xoncc = "xoncc.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

#### `setup.py` - セットアップスクリプト
```python
from setuptools import setup, find_packages

setup(
    name="xoncc",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xoncc=xoncc.main:main',
        ],
        'xontrib': [
            'xoncc=xontrib.xoncc',
        ],
    },
)
```

#### `setup.cfg` - セットアップ設定
```ini
[metadata]
name = xoncc
version = 0.0.1

[options]
packages = find:
install_requires = 
    xonsh>=0.13.0
```

#### `MANIFEST.in` - 配布ファイル指定
```
include README.md
include CLAUDE.md
include scripts/xoncc
recursive-include xoncc *.py
recursive-include xontrib *.py
```

### 3.2 ビルド・テスト

#### `Makefile` - ビルドタスク
```makefile
.PHONY: all install test clean lint
all: install test
install:
	pip install -e .
test:
	python -m pytest
clean:
	rm -rf build/ dist/ *.egg-info/
lint:
	python -m black .
	python -m mypy .
```

---

## 📚 4. ドキュメント

### 4.1 `README.md` - プロジェクト概要
- インストール手順
- 使用方法
- 機能説明

### 4.2 `CLAUDE.md` - 開発ノート
- アーキテクチャ概要
- 実装課題と解決策
- 設計原則
- 既知の制限事項
- 将来の改善点

### 4.3 `DEPLOYMENT.md` - デプロイメント手順
- PyPIパブリッシュ手順
- リリースプロセス
- バージョン管理

---

## 🔄 5. CI/CD設定

### 5.1 GitHub Actions (`.github/workflows/`)

#### `test.yml` - テスト自動化
- 複数Python版でのテスト実行
- macOS, Ubuntu, Windows対応
- カバレッジ測定

#### `publish.yml` - PyPI自動パブリッシュ
- タグプッシュ時の自動パブリッシュ
- TestPyPIでの事前テスト

#### `release.yml` - リリース自動化
- GitHub Release作成
- CHANGELOG生成

---

## 🎯 6. 手動テスト

### 6.1 手動テストスクリプト (`manual_tests/`)

#### `test_simple_query.xsh` - シンプルクエリテスト
```xonsh
xontrib load xoncc
how do I list files
```

#### `test_full_functionality.xsh` - 全機能テスト
```xonsh
xontrib load xoncc
# 各種自然言語クエリのテスト
```

#### `test_debug_override.xsh` - デバッグオーバーライドテスト
#### `test_error_elimination.xsh` - エラー除去テスト
#### `test_xoncc_live.xsh` - ライブテスト

---

## 📊 7. テスト結果

**最終テスト結果: 142 passed, 4 skipped, 0 failed**

### スキップされたテスト:
1. `test_ctrl_c_handling` - CI環境で不安定
2. `test_extract_session_id` (3個) - 削除された関数

### テストカバレッジ:
- **xontrib/xoncc.py**: 57% カバレッジ
- **全体**: 47% カバレッジ

---

## 🔧 8. 主要機能

### 8.1 実装された機能
✅ **コマンドエラー除去** - 自然言語クエリで「command not found」エラーを表示しない  
✅ **リアルタイム出力** - Claude応答のストリーミング表示  
✅ **トークンカウント** - 処理中・完了時のトークン数表示  
✅ **多言語対応** - 英語、日本語、フランス語、ロシア語対応  
✅ **自動ログイン** - Claude CLIログインエラーの自動検出・回復  
✅ **セッション管理** - 会話の継続機能  
✅ **Ctrl-Cハンドリング** - 適切な割り込み処理  
✅ **関数オーバーライド** - xonshサブプロセス実行のインターセプト  
✅ **包括的テスト** - 142個のテストケース  

### 8.2 未実装・今後の機能
🔲 **シェルコンテキスト送信** - 履歴、環境変数、現在ディレクトリ  
🔲 **並列実行** - AI処理とシェル実行の並列化  
🔲 **出力キャプチャ** - Claude応答のスクリプト利用  
🔲 **パイプライン対応** - 自然言語クエリのパイプライン  
🔲 **分割画面UI** - 上部AI、下部シェル  
🔲 **キュー管理** - 複数AI指示の管理  

---

## 🎯 9. 設計原則

1. **シンプルさ** - 可能な限りシンプルな実装を維持
2. **非侵入性** - 通常のxonsh操作に干渉しない
3. **透明性** - xonshの本来機能を活かす
4. **信頼性** - 複雑な回避策より動作する制限を優先

---

この実装により、xonshシェルに自然言語AI機能を統合し、「command not found」エラーを自動的にClaude AIが解釈・回答する環境が構築されています。