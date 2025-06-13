# xonai テスト構造

## ディレクトリ構成

```
tests/
├── unit/              # 単体テスト
├── integration/       # 結合テスト  
├── interactive/       # インタラクティブテスト
└── conftest.py        # 共通テスト設定
```

## テストタイプ別説明

### 🧪 単体テスト (`tests/unit/`)
個別コンポーネントの機能をテストします。

### 🔗 結合テスト (`tests/integration/`)
xonsh環境での統合動作をテストします。

### 🎯 インタラクティブテスト (`tests/interactive/`)
手動・自動でのユーザーインタラクション体験をテストします。

### 🤖 ダミーAIテスト
XONAI_DUMMY=1 環境変数を設定することで、実際のAI APIを使わずダミー実装でのテストを行います。

## テスト実行方法

```bash
# 全テスト実行
make test

# カテゴリ別実行
python3 -m pytest tests/unit/ -v           # 単体テスト
python3 -m pytest tests/integration/ -v    # 結合テスト
python3 -m pytest tests/interactive/ -v    # インタラクティブテスト
XONAI_DUMMY=1 python3 -m pytest tests/ -v  # ダミーAI使用でのテスト

# 手動テスト実行
python3 tests/interactive/test_xoncc_manual.py
```