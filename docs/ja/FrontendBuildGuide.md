# フロントエンドビルドガイド

## 概要

LightRAG プロジェクトには React ベースの WebUI フロントエンドが含まれています。このガイドでは、さまざまなシナリオにおけるフロントエンドビルドの仕組みを説明します。

## 基本原則

- **Git リポジトリ**: フロントエンドのビルド成果物は**含まれません**（クリーンな状態を維持）
- **PyPI パッケージ**: フロントエンドのビルド成果物が**含まれます**（すぐに使用可能）
- **ビルドツール**: **Bun** を推奨しますが、**Node.js/npm** もフォールバックとして完全にサポートされています

## インストールシナリオ

### 1. エンドユーザー（PyPI から） ✨

**コマンド:**
```bash
pip install lightrag-hku[api]
```

**動作内容:**
- フロントエンドはすでにビルド済みでパッケージに含まれています
- 追加の手順は不要です
- Web インターフェースはすぐに使用できます

---

### 2. 開発モード（コントリビューター向け推奨） 🔧

**コマンド:**
```bash
# リポジトリをクローン
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG

# 編集可能モードでインストール（フロントエンドのビルドはまだ不要）
pip install -e ".[api]"

# 必要に応じてフロントエンドをビルド（いつでも実行可能）
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..
```

**利点:**
- まずインストールし、後でビルド（柔軟なワークフロー）
- 変更が即座に反映（シンボリックリンクモード）
- 再インストールなしでいつでもフロントエンドを再ビルド可能

**仕組み:**
- ソースディレクトリへのシンボリックリンクを作成
- フロントエンドのビルド出力は `lightrag/api/webui/` に格納
- インストール済みパッケージに変更が即座に反映

---

### 3. 通常インストール（パッケージビルドのテスト） 📦

**コマンド:**
```bash
# リポジトリをクローン
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG

# ⚠️ 先にフロントエンドをビルドする必要があります
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..

# インストール
pip install ".[api]"
```

**動作内容:**
- フロントエンドファイルが site-packages に**コピー**されます
- ビルド後の変更はインストール済みパッケージに影響しません
- 更新するには再ビルドと再インストールが必要です

**使用場面:**
- 完全なインストールプロセスのテスト
- パッケージ設定の検証
- PyPI ユーザー体験のシミュレーション

---

### 4. 配布パッケージの作成 🚀

**コマンド:**
```bash
# まずフロントエンドをビルド
cd lightrag_webui
bun install --frozen-lockfile --production
bun run build
cd ..

# 配布パッケージを作成
python -m build

# 出力: dist/lightrag_hku-*.whl および dist/lightrag_hku-*.tar.gz
```

**動作内容:**
- `setup.py` がフロントエンドのビルド済みかどうかをチェック
- 未ビルドの場合、分かりやすいエラーメッセージとともにインストールが失敗
- 生成されたパッケージにはすべてのフロントエンドファイルが含まれます

---

## GitHub Actions（自動リリース）

GitHub でリリースを作成すると:

1. Bun を使用して**フロントエンドを自動ビルド**
2. ビルドの成功を**検証**
3. フロントエンドを含む **Python パッケージを作成**
4. 既存のトラステッドパブリッシャー設定を使用して **PyPI に公開**

**手動操作は不要です！**

---

## クイックリファレンス

| シナリオ | コマンド | フロントエンドの要否 | 後からビルド可能か |
|----------|---------|-------------------|-----------------|
| PyPI から | `pip install lightrag-hku[api]` | 含まれています | いいえ（インストール済み） |
| 開発 | `pip install -e ".[api]"` | 不要 | ✅ はい（いつでも） |
| 通常インストール | `pip install ".[api]"` | ✅ 必要（事前に） | いいえ（再インストールが必要） |
| パッケージ作成 | `python -m build` | ✅ 必要（事前に） | N/A |

---

## Bun のインストール

Bun がインストールされていない場合:

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# Windows
powershell -c "irm bun.sh/install.ps1 | iex"
```

公式ドキュメント: https://bun.sh

---

## ファイル構成

```
LightRAG/
├── lightrag_webui/          # フロントエンドソースコード
│   ├── src/                 # React コンポーネント
│   ├── package.json         # 依存関係
│   └── vite.config.ts       # ビルド設定
│       └── outDir: ../lightrag/api/webui  # ビルド出力先
│
├── lightrag/
│   └── api/
│       └── webui/           # フロントエンドビルド出力（gitignore 対象）
│           ├── index.html   # ビルド済みファイル（bun run build 実行後）
│           └── assets/      # ビルド済みアセット
│
├── setup.py                 # ビルドチェック
├── pyproject.toml           # パッケージ設定
└── .gitignore               # lightrag/api/webui/* を除外（.gitkeep を除く）
```

---

## トラブルシューティング

### Q: 開発モードでインストールしましたが、Web インターフェースが動作しません

**A:** フロントエンドをビルドしてください:
```bash
cd lightrag_webui && bun run build
```

### Q: フロントエンドをビルドしましたが、インストール済みパッケージに反映されていません

**A:** おそらくビルド後に `pip install .` を使用したためです。以下のいずれかを試してください:
- 開発用に `pip install -e ".[api]"` を使用する
- または再インストール: `pip uninstall lightrag-hku && pip install ".[api]"`

### Q: ビルド済みフロントエンドファイルはどこにありますか？

**A:** `bun run build` 実行後、`lightrag/api/webui/` にあります

### Q: Bun の代わりに npm や yarn を使用できますか？

**A:** はい。ビルドスクリプト（`dev`、`build`、`preview`、`lint`）はランタイムに依存せず、Bun と Node.js/npm の両方で動作します:
```bash
npm install
npm run build
```
速度の面で Bun を推奨しますが、npm も完全にサポートされています。テスト（`bun test`）には引き続き Bun が必要です。

### Q: `Cannot find package '@/lib'` でビルドが失敗します

**A:** これは `vite.config.ts` が TypeScript パスエイリアス（`@/`）を使用しており、設定読み込み時に Bun のみが解決できたことが原因でした。相対インポートで修正された最新バージョンに更新してください。

---

## まとめ

✅ **PyPI ユーザー**: 操作不要、フロントエンドは含まれています
✅ **開発者**: `pip install -e ".[api]"` を使用し、必要に応じてフロントエンドをビルド
✅ **CI/CD**: GitHub Actions で自動ビルド
✅ **Git**: フロントエンドビルド出力はコミットされません

質問や問題がある場合は、GitHub issue を作成してください。
