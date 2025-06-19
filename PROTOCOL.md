# xonai 通信プロトコル仕様

## 概要

xonaiはAIモデルとの通信に、型付きResponseオブジェクトのストリーミングプロトコルを使用します。
AIは`Generator[Response, None, None]`を返し、各Responseは特定の意味を持ちます。

## Response型

### 1. InitResponse
**目的**: セッション開始の通知
```python
@dataclass
class InitResponse(Response):
    content: str              # AI名（例: "Claude Code"）
    session_id: Optional[str] # セッションID
    model: Optional[str]      # モデル名
    content_type: ContentType.TEXT
```

### 2. MessageResponse
**目的**: AIからのテキストメッセージ（ストリーミング対応）
```python
@dataclass
class MessageResponse(Response):
    content: str              # メッセージの一部または全体
    content_type: ContentType.MARKDOWN  # デフォルト
```

### 3. ToolUseResponse
**目的**: ツール使用の通知
```python
@dataclass
class ToolUseResponse(Response):
    content: str              # ツールへの入力（コマンド、ファイルパスなど）
    tool: str                 # ツール名（Bash, Read, Edit等）
    content_type: ContentType.TEXT
```

### 4. ToolResultResponse
**目的**: ツール実行結果
```python
@dataclass
class ToolResultResponse(Response):
    content: str              # ツールの出力
    tool: str                 # ツール名
    content_type: ContentType.TEXT
```

### 5. ErrorResponse
**目的**: エラー通知（ユーザーには表示されない）
```python
@dataclass
class ErrorResponse(Response):
    content: str              # エラーメッセージ
    error_type: Optional[ErrorType]
    content_type: ContentType.TEXT
```

### 6. ResultResponse
**目的**: セッション終了と統計情報
```python
@dataclass
class ResultResponse(Response):
    content: str              # 統計情報（duration_ms, cost_usd等）
    token: int                # トークン数
    content_type: ContentType.TEXT
```

## 通信フロー

1. **InitResponse** → セッション開始
2. **MessageResponse** → AIの説明文（オプション）
3. **ToolUseResponse** → ツール使用通知
4. **ToolResultResponse** → ツール結果（オプション）
5. 3-4を必要に応じて繰り返し
6. **MessageResponse** → 最終的な回答
7. **ResultResponse** → セッション終了

## 表示例

### パターン1: シンプルなコマンド実行
```
ユーザー: echo helloを実行して

🚀 Claude Code: model=claude-opus-4-20250514, id=abc123

I'll execute the echo hello command for you.
🔧 echo hello
  → hello

📊 duration_ms=1234, cost_usd=0.001000, input_tokens=10, output_tokens=20, next_session_tokens=30
```

### パターン2: ファイル操作
```
ユーザー: README.mdを読んで内容を説明して

🚀 Claude Code: model=claude-opus-4-20250514, id=def456

I'll read the README.md file and explain its contents.
📖 Reading README.md
  → Read 50 lines

The README.md file contains:
- Project overview for xonai
- Installation instructions using pip
- Usage examples with xontrib load
- Features list including AI integration

📊 duration_ms=2345, cost_usd=0.002000, input_tokens=15, output_tokens=100, next_session_tokens=115
```

### パターン3: 複数ツール使用
```
ユーザー: 現在のディレクトリの状況を教えて

🚀 Claude Code: model=claude-opus-4-20250514, id=ghi789

I'll check the current directory status.
🔧 pwd
  → /home/user/project
🔧 ls -la
  → Output: 15 lines
🔧 git status
  → Output: 8 lines

You're in /home/user/project with:
- 10 Python files
- Clean git working tree
- Virtual environment active

📊 duration_ms=3456, cost_usd=0.003000, input_tokens=20, output_tokens=150, next_session_tokens=170
```

### パターン4: 検索と編集
```
ユーザー: configという単語を含むファイルを探して

🚀 Claude Code: model=claude-opus-4-20250514, id=jkl012

I'll search for files containing "config".
🔍 Searching for: config
  → Found 3 matches
📖 Reading settings.py
  → Read 120 lines

Found configuration files:
- settings.py - Application configuration
- config.json - JSON configuration file  
- tests/test_config.py - Configuration tests

📊 duration_ms=4567, cost_usd=0.004000, input_tokens=25, output_tokens=200, next_session_tokens=225
```

### パターン5: エラーケース（エラーは表示されない）
```
ユーザー: 存在しないファイルを読んで

🚀 Claude Code: model=claude-opus-4-20250514, id=mno345

I'll try to read that file.
📖 Reading nonexistent.txt

I couldn't find the file "nonexistent.txt". The file doesn't exist in the current directory.

📊 duration_ms=1000, cost_usd=0.001000, input_tokens=10, output_tokens=30, next_session_tokens=40
```

## 表示ルール

1. **InitResponse**: 空行の後に表示
2. **MessageResponse**: ストリーミングで連続表示
3. **ToolUseResponse**: 絵文字付きで簡潔に表示
4. **ToolResultResponse**: インデント付きで要約表示
5. **ErrorResponse**: 表示しない（ユーザーに見せない）
6. **ResultResponse**: 空行の後に統計情報表示

## ツール別の表示

- **Bash** (🔧): コマンドを表示、結果は行数または短い出力
- **Read** (📖): ファイル名表示、結果は読み込み行数
- **Edit/Write** (✏️): ファイル名表示、結果は更新完了通知
- **LS** (📁): パス表示、結果はアイテム数
- **Search/Grep** (🔍): 検索パターン表示、結果はマッチ数
- **TodoRead** (📋): "Reading todos"、結果はTodo数
- **TodoWrite** (📝): "Updating todos"、結果は更新完了
- **WebSearch** (🔍): 検索クエリ表示
- **WebFetch** (🌐): URL表示