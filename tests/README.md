# xoncc テスト構造

## ディレクトリ構成

```
tests/
├── unit/              # 単体テスト
├── integration/       # 結合テスト  
├── interactive/       # インタラクティブテスト
├── dummy_claude/      # ダミーClaude CLIテスト
└── conftest.py        # 共通テスト設定
```

## テストタイプ別説明

### 🧪 単体テスト (`tests/unit/`)
個別コンポーネントの機能をテストします。

### 🔗 結合テスト (`tests/integration/`)
xonsh環境での統合動作をテストします。

### 🎯 インタラクティブテスト (`tests/interactive/`)
手動・自動でのユーザーインタラクション体験をテストします。

### 🤖 ダミーClaude CLIテスト (`tests/dummy_claude/`)
実際のClaude APIを使わず、ダミー実装でのテストを行います。

## テスト実行方法

```bash
# 全テスト実行
make test

# カテゴリ別実行
python3 -m pytest tests/unit/ -v           # 単体テスト
python3 -m pytest tests/integration/ -v    # 結合テスト
python3 -m pytest tests/interactive/ -v    # インタラクティブテスト
python3 -m pytest tests/dummy_claude/ -v   # ダミーClaude CLIテスト

# 手動テスト実行
python3 tests/interactive/test_xoncc_manual.py
```