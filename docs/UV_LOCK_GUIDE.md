# uv.lock 更新ガイド

## uv.lock とは？

`uv.lock` は uv のロックファイルです。推移的な依存関係を含む、すべての依存関係の正確なバージョンを記録します。以下と同様の役割を果たします:
- Node.js `package-lock.json`
- Rust `Cargo.lock`
- Python Poetry `poetry.lock`

`uv.lock` をバージョン管理に含めることで、全員が同じ依存関係セットをインストールすることが保証されます。

## uv.lock はいつ変更されるか？

### 自動的に変更され*ない*ケース

- `uv sync --frozen` の実行
- `uv sync --frozen` を呼び出す Docker イメージのビルド
- 依存関係のメタデータに触れずにソースコードを編集

### 変更されるケース

1. **`uv lock` または `uv lock --upgrade`**

   ```bash
   uv lock                # 現在の制約に従って解決
   uv lock --upgrade      # 再解決し、互換性のある最新リリースにアップグレード
   ```

   `pyproject.toml` を変更した後、新しい依存関係バージョンが必要な場合、またはロックファイルが削除・破損した場合にこれらのコマンドを使用します。

2. **`uv add`**

   ```bash
    uv add requests           # 依存関係を追加し、両ファイルを更新
    uv add --dev pytest       # 開発用依存関係を追加
   ```

   `uv add` は `pyproject.toml` を編集し、`uv.lock` を一度に更新します。

3. **`uv remove`**

   ```bash
   uv remove requests
   ```

   `pyproject.toml` から依存関係を削除し、`uv.lock` を再書き込みします。

4. **`--frozen` なしの `uv sync`**

   ```bash
   uv sync
   ```

   通常はロック済みの内容のみをインストールします。ただし、`pyproject.toml` と `uv.lock` が一致しない場合やロックファイルが存在しない場合、uv は `uv.lock` を再生成・更新します。CI や本番ビルドでは、意図しない更新を防ぐために `uv sync --frozen` を使用することをお勧めします。

## ワークフロー例

### シナリオ 1: 新しい依存関係の追加

```bash
# 推奨: uv に両ファイルを処理させる
uv add fastapi
git add pyproject.toml uv.lock
git commit -m "Add fastapi dependency"

# 手動の代替方法
# 1. pyproject.toml を編集
# 2. ロックファイルを再生成
uv lock
git add pyproject.toml uv.lock
git commit -m "Add fastapi dependency"
```

### シナリオ 2: バージョン制約の緩和または厳格化

```bash
# 1. pyproject.toml の要件を編集
#    例: openai>=1.0.0,<2.0.0 -> openai>=1.5.0,<2.0.0

# 2. ロックファイルを再解決
uv lock

# 3. 両ファイルをコミット
git add pyproject.toml uv.lock
git commit -m "Update openai to >=1.5.0"
```

### シナリオ 3: すべてを互換性のある最新バージョンにアップグレード

```bash
uv lock --upgrade
git diff uv.lock
git add uv.lock
git commit -m "Upgrade dependencies to latest compatible versions"
```

### シナリオ 4: チームメンバーのプロジェクト同期

```bash
git pull               # 最新のコードとロックファイルを取得
uv sync --frozen       # uv.lock で指定された通りにインストール
```

## Docker での uv.lock の使用

```dockerfile
RUN uv sync --frozen --no-dev --extra api
```

`--frozen` は再現可能なビルドを保証します。uv はロックされたバージョンから逸脱することを拒否します。
`--extra api` は API サーバーをインストールします

## オフライン依存関係を含むロックファイルの生成

`uv.lock` がオプションのオフラインスタックをキャプチャする必要がある場合、関連するエクストラを有効にして再生成します:

```bash
uv lock --extra api --extra offline
```

このコマンドは、ベースプロジェクトの要件に加えて `api` と `offline` の両方のオプション依存関係セットを解決し、下流の `uv sync --frozen --extra api --extra offline` インストールがさらなる解決なしに動作することを保証します。

## よくある質問

- **`uv.lock` は約 1 MB あります。問題ですか？**
  いいえ。このファイルは依存関係の解決時にのみ読み取られます。

- **`uv.lock` をコミットすべきですか？**
  はい。コラボレーターや CI ジョブが同じ依存関係グラフを共有できるようにコミットしてください。

- **ロックファイルを誤って削除してしまいました？**
  `uv lock` を実行して `pyproject.toml` から再生成してください。

- **`uv.lock` と `requirements.txt` は共存できますか？**
  可能ですが、両方を維持するのは冗長です。可能な限り `uv.lock` のみに依存することをお勧めします。

- **ロックされたバージョンを確認するには？**
  ```bash
  uv tree
  grep -A5 'name = "openai"' uv.lock
  ```

## ベストプラクティス

### 推奨事項

1. `uv.lock` を `pyproject.toml` と一緒にコミットする。
2. CI、Docker、その他の再現可能な環境では `uv sync --frozen` を使用する。
3. ローカル開発では、uv にロックを調整させたい場合は通常の `uv sync` を使用する。
4. 互換性のある最新リリースを取得するために定期的に `uv lock --upgrade` を実行する。
5. 依存関係の制約を変更した後は、直ちにロックファイルを再生成する。

### 避けるべきこと

1. CI や本番パイプラインで `--frozen` なしの `uv sync` を実行すること。
2. `uv.lock` を手動で編集すること -- uv が手動の変更を上書きします。
3. コードレビューでロックファイルの差分を無視すること -- 予期しない依存関係の変更がビルドを壊す可能性があります。

## まとめ

| コマンド               | `uv.lock` を更新するか | 一般的な用途                               |
|-----------------------|-------------------|-------------------------------------------|
| `uv lock`             | ✅ はい            | 制約の編集後                 |
| `uv lock --upgrade`   | ✅ はい            | 互換性のある最新バージョンにアップグレード |
| `uv add <pkg>`        | ✅ はい            | 依存関係の追加                          |
| `uv remove <pkg>`     | ✅ はい            | 依存関係の削除                       |
| `uv sync`             | ⚠️ 場合による          | ローカル開発; ロックを再生成する可能性あり |
| `uv sync --frozen`    | ❌ いいえ             | CI/CD、Docker、再現可能なビルド        |

覚えておいてください: `uv.lock` は、変更を指示するコマンドを実行した場合にのみ変更されます。プロジェクトと同期を保ち、変更があるたびにコミットしてください。
