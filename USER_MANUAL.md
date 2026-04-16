# LightRAG ユーザーマニュアル

このマニュアルは、プログラミングの知識が全くない方でも LightRAG を使えるようになることを目的としています。

---

## 目次

1. [LightRAG とは何か？](#1-lightrag-とは何か)
2. [できること](#2-できること)
3. [事前準備](#3-事前準備)
4. [初回セットアップ](#4-初回セットアップ)
5. [LightRAG を起動する](#5-lightrag-を起動する)
6. [WebUI（操作画面）の使い方](#6-webui操作画面の使い方)
7. [ドキュメントを登録する](#7-ドキュメントを登録する)
8. [質問する（検索・対話）](#8-質問する検索対話)
9. [ナレッジグラフを見る](#9-ナレッジグラフを見る)
10. [LightRAG を停止・再起動する](#10-lightrag-を停止再起動する)
11. [困ったときは](#11-困ったときは)
12. [用語集](#12-用語集)
- [付録 A: よく使うコマンド一覧](#付録-a-よく使うコマンド一覧)
- [付録 B: `process_document.py`（上級者向けコマンドラインツール）のセットアップ](#付録-b-process_documentpy上級者向けコマンドラインツールのセットアップ)
- [付録 C: MCP サーバーで Claude Desktop から LightRAG を使う](#付録-c-mcp-サーバーで-claude-desktop-から-lightrag-を使う)

---

## 1. LightRAG とは何か？

**LightRAG（ライトラグ）** は、あなたが持っているたくさんの文書（PDF・Word・テキストなど）を AI に読み込ませて、まるで専門家に質問するように使えるシステムです。

### こんな経験はありませんか？

- 「会社のマニュアルが何百ページもあって、どこに何が書いてあるかわからない」
- 「過去の議事録から、特定の決定事項を探したいけど時間がかかる」
- 「専門書を読んでも内容が頭に入らないので、要点だけ知りたい」

LightRAG は、こうした悩みを解決します。文書を一度登録すれば、あとは自然な日本語で質問するだけで、AI が文書の内容に基づいて答えてくれます。

### 一般的な検索との違い

| 一般的な検索（Google など） | LightRAG |
|---|---|
| キーワードに合うページを表示 | 質問の意味を理解して**答え**を返す |
| 自分で答えを探す必要がある | AI が文書を読んで**まとめてくれる** |
| 文書間の関係はわからない | 関連する情報を**つなげて**回答する |

---

## 2. できること

LightRAG では次のようなことができます。

### ✅ 文書の登録
- PDF、Word、テキストファイルなどをアップロードできます
- 画像や表が含まれる文書も処理できます（RAG-Anything 機能）
- 何百個でも登録可能です

### ✅ 自然な質問
- 「○○について教えて」のような普通の日本語で質問できます
- 「3 つにまとめて」「箇条書きで」など、回答の形式も指定できます

### ✅ 知識のつながりを可視化
- 文書から自動的に「人物」「組織」「場所」などを抽出します
- これらの関係を**ナレッジグラフ**（点と線の図）で見ることができます

### ✅ 完全に日本語対応
- 操作画面は日本語
- 日本語の文書に最適化された処理
- 日本語で質問・回答

---

## 3. 事前準備

LightRAG を使うために、次の 3 つを準備してください。

### 3.1 パソコン環境

- **OS**: Mac、Windows、Linux のいずれでも動きます
- **メモリ**: 8GB 以上を推奨
- **ディスク空き容量**: 10GB 以上

### 3.2 Docker Desktop のインストール

LightRAG は **Docker（ドッカー）** という仕組みを使って動きます。Docker は、難しい設定をせずにアプリを起動できる便利な道具だと思ってください。

1. ブラウザで [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) を開きます
2. 「Download Docker Desktop」をクリックしてダウンロードします
3. ダウンロードしたファイルをダブルクリックしてインストールします
4. インストール後、Docker Desktop を起動します
5. 画面右下（Mac は右上）に**クジラのアイコン**が表示されたら準備完了です

> 💡 **わからなくても大丈夫**: Docker の中身を理解する必要はありません。「Docker Desktop が起動している＝LightRAG が動かせる状態」とだけ覚えてください。

### 3.3 OpenAI API キー

LightRAG は AI（GPT）を使うため、**OpenAI の API キー**が必要です。これは AI を使うための「鍵」のようなものです。

1. [https://platform.openai.com/](https://platform.openai.com/) にアクセスします
2. アカウントを作成します（メールアドレスが必要）
3. クレジットカードを登録して、最低 5 ドル程度をチャージします
4. 「API keys」のページで「Create new secret key」をクリックします
5. 表示された文字列（`sk-` で始まる長い文字列）を**メモ帳などにコピーして保存**します

> ⚠️ **重要**: API キーは一度しか表示されません。必ずコピーして大切に保管してください。他人に見せないようにしてください。
>
> 💰 **料金について**: 文書の量や質問の回数に応じて OpenAI の利用料がかかります。最初は数百円程度で十分試せます。

---

## 4. 初回セットアップ

LightRAG をはじめて使うときの手順です。**1 回だけ**行えば、次回以降は不要です。

### 4.1 LightRAG のフォルダを開く

このマニュアルがある `LightRAG` フォルダを開いてください。

### 4.2 API キーを設定する

1. `LightRAG` フォルダの中にある `.env` という名前のファイルをテキストエディタ（メモ帳・TextEdit など）で開きます
   - 隠しファイルになっている場合があります。Mac では `command + shift + .` で表示を切り替えられます
2. 次の 2 行を探します:
   ```
   LLM_BINDING_API_KEY=your_api_key
   EMBEDDING_BINDING_API_KEY=your_api_key
   ```
3. `your_api_key` の部分を、先ほどコピーした OpenAI の API キーに書き換えます
   - 例: `LLM_BINDING_API_KEY=sk-proj-AbCdEf...`
4. **必ず保存**してファイルを閉じます

> 💡 **ヒント**: API キーは前後にスペースを入れないでください。

### 4.3 Docker Desktop が起動していることを確認

画面右下（Mac は右上）にクジラのアイコンが表示されていることを確認してください。

---

## 5. LightRAG を起動する

### 5.1 ターミナルを開く

「ターミナル」とは、コンピュータに命令を文字で伝えるための画面です。怖くありません、コピペするだけです。

- **Mac**: `Launchpad` → `その他` → `ターミナル` をクリック
- **Windows**: スタートメニューで「PowerShell」と検索してクリック

### 5.2 LightRAG のフォルダに移動

ターミナルに次のように入力して Enter キーを押します（**フォルダのパスはご自身の環境に合わせて変更してください**）:

```
cd /Users/あなたの名前/Dev-Work/LightRAG
```

> 💡 **裏技**: ターミナルに `cd ` と入力した後、Finder（エクスプローラー）から LightRAG フォルダをターミナルにドラッグ＆ドロップすると、パスが自動入力されます。

### 5.3 LightRAG を起動

次のコマンドをコピペして Enter キーを押します:

```
docker compose up -d
```

しばらく待つと（初回は数分かかります）、次のような表示が出ます:

```
Container lightrag-lightrag-1  Started
```

これで LightRAG が起動しました！🎉

### 5.4 ブラウザで開く

ブラウザ（Chrome、Safari、Edge など）を開き、アドレスバーに次を入力します:

```
http://localhost:9621
```

LightRAG の操作画面が日本語で表示されたら成功です。

---

## 6. WebUI（操作画面）の使い方

### 画面の構成

LightRAG の画面は、上部にタブ（切り替えボタン）があります。

| タブ名 | 役割 |
|---|---|
| 📄 **ドキュメント** | 文書のアップロード・管理 |
| 🕸️ **ナレッジグラフ** | 知識のつながりを可視化 |
| 🔍 **検索** | 質問して回答を得る |
| 📚 **API** | 開発者向けの API ドキュメント（通常は使いません） |

右上の歯車アイコン（⚙️）から、言語やテーマ（ダーク/ライト）を変更できます。

---

## 7. ドキュメントを登録する

### 7.1 文書をアップロード

1. 画面上部の **📄 ドキュメント** タブをクリック
2. 「**アップロード**」または「**ファイルを追加**」ボタンをクリック
3. 登録したいファイルを選びます
   - **対応形式**: PDF、Word（.docx）、PowerPoint（.pptx）、Excel（.xlsx）、テキスト（.txt）、Markdown（.md）など
4. 「アップロード」を押すと処理が始まります

### 7.2 処理状況の確認

アップロードした文書は、次の段階を経て処理されます:

| ステータス | 意味 |
|---|---|
| **PENDING（待機中）** | 処理待ちの状態 |
| **PROCESSING（処理中）** | AI が文書を読んでいる最中 |
| **PROCESSED（完了）** | 処理が終わり、質問できる状態 |
| **FAILED（失敗）** | エラーが発生した状態 |

> ⏱️ **処理時間の目安**: 10 ページの PDF で 1〜3 分程度。文書の量と AI の応答速度によって変わります。

### 7.3 文書の削除

不要になった文書は、ドキュメント一覧の右側にあるゴミ箱アイコンから削除できます。

> ⚠️ 削除すると、その文書に関連する知識もナレッジグラフから消去されます。

---

## 8. 質問する（検索・対話）

### 8.1 基本的な質問

1. 画面上部の **🔍 検索** タブをクリック
2. 下部の入力欄に質問を日本語で入力します
   - 例: `この文書の要点を 3 つに分けて教えて`
   - 例: `2024 年に決定された施策は何ですか？`
3. Enter キー（または送信ボタン）を押す
4. AI が文書を参照して回答します

### 8.2 検索モードの選び方

質問入力欄の近くに「**モード**」という設定があります。質問の種類に応じて使い分けます。

| モード | 特徴 | こんなときに使う |
|---|---|---|
| **naive（ナイーブ）** | 単純なキーワード検索に近い | キーワードがはっきりしている質問 |
| **local（ローカル）** | 関連する詳細情報を集める | 特定のトピックを深く知りたい |
| **global（グローバル）** | 文書全体の傾向を把握 | 全体的な要約や傾向の質問 |
| **hybrid（ハイブリッド）** | local と global を組み合わせ | バランスの取れた回答が欲しい |
| **mix（ミックス）** | すべての方法を統合（推奨） | 迷ったらこれを選ぶ |

> 💡 **おすすめ**: 最初は **mix** を選んでおけば、ほとんどの質問にうまく答えられます。

### 8.3 上手な質問のコツ

- **具体的に書く**: ❌「教えて」→ ⭕「営業部の 2024 年度の目標について教えて」
- **形式を指定する**: 「箇条書きで」「表形式で」「3 つにまとめて」
- **対象を絞る**: 「○○の文書から」「△△に関する内容だけ」
- **追加質問する**: 1 回で完璧を求めず、回答を見て次の質問につなげる

### 8.4 履歴の確認

過去の質問と回答は画面に残ります。スクロールして確認できます。

---

## 9. ナレッジグラフを見る

### 9.1 ナレッジグラフとは？

文書から AI が自動的に抽出した「**エンティティ（名詞）**」と「**リレーション（関係）**」を、点と線で視覚化したものです。

例:
- 点（ノード）= 「田中さん」「営業部」「東京支店」
- 線（エッジ）= 「田中さん」**所属**→「営業部」、「営業部」**勤務地**→「東京支店」

### 9.2 グラフの操作

1. 画面上部の **🕸️ ナレッジグラフ** タブをクリック
2. グラフが表示されます
3. **マウス操作**:
   - **ドラッグ**: グラフを移動
   - **ホイール**: 拡大・縮小
   - **クリック**: ノード（点）を選択して詳細表示
4. 左上の **検索ボックス** に名前を入力すると、特定のノードを探せます

### 9.3 グラフのフィルタ

- **ラベル選択**: 特定の種類（人物・組織など）だけ表示
- **最大ノード数**: 表示する点の数を制限（多すぎると重くなります）
- **レイアウト**: グラフの並べ方を変更

---

## 10. LightRAG を停止・再起動する

### 10.1 停止

LightRAG を一時的に止めるときは、ターミナルで:

```
docker compose stop
```

> 💡 データは消えません。次回起動すれば、登録した文書はそのまま使えます。

### 10.2 再起動

```
docker compose start
```

### 10.3 完全に削除

LightRAG を消したいときは:

```
docker compose down
```

> ⚠️ `data/` フォルダの中身を削除しなければ、文書データは残ります。完全削除する場合は手動で `data/rag_storage` フォルダを削除してください。

### 10.4 ログ（動作記録）の確認

何か問題が起きたときは、次のコマンドで詳しい動作記録を見られます:

```
docker compose logs --tail 100
```

---

## 11. 困ったときは

### Q1. 「http://localhost:9621」を開いても画面が表示されない

**原因と対処**:
1. Docker Desktop が起動しているか確認してください
2. ターミナルで `docker compose ps` を実行し、`Up` と表示されているか確認
3. 起動直後は数十秒待ってから再度アクセスしてみてください

### Q2. ファイルをアップロードしても「FAILED」になる

**原因と対処**:
1. **API キーが間違っている**: `.env` ファイルの `LLM_BINDING_API_KEY` を確認
2. **OpenAI の残高不足**: [https://platform.openai.com/](https://platform.openai.com/) で残高を確認
3. **ファイル形式が非対応**: PDF・Word・テキストなどの一般的な形式を使ってください
4. **ファイルが大きすぎる**: 100MB 以下に分割してみてください

### Q3. 質問しても「I cannot find...」のような英語の答えが返る

**原因と対処**:
- まだ文書の処理（PROCESSING）が完了していない可能性があります
- ドキュメントタブで「PROCESSED」になっているか確認してください

### Q4. 回答が遅い

**原因と対処**:
- AI の処理には時間がかかります（5〜30 秒程度は普通）
- インターネット接続が不安定だと遅くなります
- 使用している OpenAI モデルを変更すると速くなる場合があります（`.env` の `LLM_MODEL`）

### Q5. OpenAI の料金が心配

**対処**:
- OpenAI のサイトで使用量と上限を設定できます
- [https://platform.openai.com/account/limits](https://platform.openai.com/account/limits) で月額上限を設定してください
- 使うときだけ Docker を起動し、終わったら停止すれば料金は発生しません

### Q6. パスワードや認証を設定したい

外部に公開する場合は認証が必要です。`.env` ファイルに次の行を追加してください:

```
LIGHTRAG_API_KEY=好きな英数字の文字列
AUTH_ACCOUNTS=admin:好きなパスワード
```

設定後、`docker compose restart` で再起動します。

### それでも解決しない場合

- ターミナルで `docker compose logs --tail 200` を実行し、エラーメッセージを確認してください
- 公式の問題報告ページ: [https://github.com/HKUDS/LightRAG/issues](https://github.com/HKUDS/LightRAG/issues)

---

## 12. 用語集

専門用語を簡単な言葉で説明します。

| 用語 | 意味 |
|---|---|
| **RAG（ラグ）** | Retrieval-Augmented Generation の略。「検索 + AI 生成」の組み合わせ。AI が文書を読んで答える仕組み |
| **LLM（エルエルエム）** | Large Language Model の略。ChatGPT のような「大規模言語モデル」のこと |
| **エンベディング（Embedding）** | 文章を数字のリストに変換すること。AI が「似た意味」を判断するために使う |
| **ナレッジグラフ** | 知識を「点」と「線」でつないだ図 |
| **エンティティ（Entity）** | 文書から抜き出した「名前」（人・組織・場所など） |
| **リレーション（Relation）** | エンティティ同士の関係（〇〇は△△に所属する、など） |
| **チャンク（Chunk）** | 長い文書を細かく分けた一つひとつの「かたまり」 |
| **トークン（Token）** | AI が文章を扱う最小単位。日本語ではだいたい 1 文字 = 1〜2 トークン |
| **API キー** | AI サービスを使うための「鍵」となる文字列 |
| **Docker（ドッカー）** | アプリケーションを簡単に動かすための仕組み |
| **WebUI（ウェブユーアイ）** | ブラウザで操作する画面のこと |

---

## 付録 A: よく使うコマンド一覧

ターミナルで使う基本コマンドの早見表です。

| やりたいこと | コマンド |
|---|---|
| LightRAG を起動 | `docker compose up -d` |
| LightRAG を停止 | `docker compose stop` |
| LightRAG を再起動 | `docker compose restart` |
| 状態を確認 | `docker compose ps` |
| ログを見る | `docker compose logs --tail 100` |
| 完全に停止 | `docker compose down` |

---

## 付録 B: `process_document.py`（上級者向けコマンドラインツール）のセットアップ

`process_document.py` は、PDF 内の画像・表・数式を含む複雑な文書をマルチモーダル解析してから LightRAG に取り込むためのコマンドラインツールです。**WebUI では不要**で、バッチ処理や自動化パイプラインを構築したい上級者向けの機能です。

> ⚠️ **注意**: このセクションは Python 環境の操作に慣れている方を対象としています。WebUI で文書登録する通常の使い方（[7. ドキュメントを登録する](#7-ドキュメントを登録する)）だけで用が足りる場合は、このセットアップは不要です。

### B.1 必要な依存関係

| 依存 | 役割 | 備考 |
|---|---|---|
| `raganything>=1.2.0` | マルチモーダル処理エンジン本体 | `--no-deps` で入れる必要あり（下記参照） |
| パーサーのいずれか | 文書の構造解析 | `mineru` / `docling` / `paddleocr` から選択 |

### B.2 `raganything` のインストール

`raganything` は通常の `uv sync` では入りません。内部依存の `mineru[core]` が他パッケージと競合するため、**`--no-deps` フラグ付きの手動インストール**が必要です（`pyproject.toml` のコメントにも明記されています）。

```bash
# LightRAG のルートディレクトリで仮想環境を有効化
source .venv/bin/activate     # macOS / Linux
# .venv\Scripts\activate       # Windows

# raganything を依存解決なしでインストール
uv pip install --no-deps 'raganything>=1.2.0'
```

> 💡 `--no-deps` を付け忘れると依存解決に失敗して `uv` がエラーを返します。必ず付けてください。

### B.3 パーサーのインストール（いずれか 1 つ）

`process_document.py` は `--parser` オプション（既定値は `mineru`）でパーサーを選択します。選んだパーサーに応じて追加インストールが必要です。

#### B.3.1 MinerU（既定・推奨）

```bash
uv pip install 'mineru[core]'
```

> 💡 初回実行時に ~2GB のモデルをダウンロードします。ディスク容量に注意してください。

#### B.3.2 Docling

```bash
uv sync --extra docling
```

> ⚠️ **macOS では使えません**。`docling` は PyTorch 経由で Objective-C のフレームワークを利用しますが、macOS ではフォークセーフではないため、gunicorn のマルチワーカーと互換性がありません（`pyproject.toml` で `sys_platform != 'darwin'` 条件付きになっています）。macOS では MinerU か PaddleOCR を使ってください。

#### B.3.3 PaddleOCR

```bash
uv pip install paddleocr
```

> 💡 GPU 版を使う場合は [PaddleOCR 公式ドキュメント](https://github.com/PaddlePaddle/PaddleOCR) の手順に従ってください。

### B.4 インストールの確認

次のコマンドで import エラーが出なければ成功です。

```bash
python -c "from raganything import RAGAnything; print('raganything OK')"
python -c "from lightrag.japanese_chunking import japanese_chunking; print('lightrag OK')"
```

### B.5 実行例

```bash
# 環境変数で API キー等を設定（.env を読み込みます）
python process_document.py path/to/document.pdf \
    --working_dir ./data/rag_storage \
    --output ./output \
    --parser mineru
```

主なオプション:

| オプション | 既定値 | 説明 |
|---|---|---|
| `file_path` | （必須） | 処理対象の文書パス |
| `--working_dir` / `-w` | `./data/rag_storage` | LightRAG のデータ保存先 |
| `--output` / `-o` | `./output` | パーサーの中間出力先 |
| `--api-key` | `LLM_BINDING_API_KEY` 環境変数 | OpenAI API キー |
| `--base-url` | `LLM_BINDING_HOST` 環境変数 | カスタム API エンドポイント |
| `--parser` | `PARSER` 環境変数 or `mineru` | 使用するパーサー |

### B.6 トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| `ModuleNotFoundError: No module named 'raganything'` | B.2 未実施 | `uv pip install --no-deps 'raganything>=1.2.0'` |
| `ModuleNotFoundError: No module named 'mineru'` | パーサー未インストール | B.3.1 を実施、または `--parser` で別パーサー指定 |
| macOS で docling インポート失敗 | プラットフォーム非対応 | MinerU か PaddleOCR を使用 |
| `raganything` の依存競合エラー | `--no-deps` 忘れ | `--no-deps` を付けて再インストール |

---

## 付録 C: MCP サーバーで Claude Desktop から LightRAG を使う

`lightrag_mcp_server.py` は、**Claude Desktop（および MCP 対応クライアント）から LightRAG の知識グラフに質問・登録できる**ようにする橋渡しスクリプトです。

### C.1 何ができるか

Claude Desktop のチャット画面で、次の 3 つのツールを LightRAG に対して実行できます。

| ツール | 動作 |
|---|---|
| `lightrag_query` | 知識グラフに質問して回答を取得（5 つの検索モード対応） |
| `lightrag_insert` | テキストを知識グラフに登録 |
| `lightrag_health` | LightRAG サーバーの稼働状況・パイプライン進捗を確認 |

### C.2 前提条件

- **LightRAG サーバーが起動している**こと（[5. LightRAG を起動する](#5-lightrag-を起動する) 参照）
- **Claude Desktop** がインストールされていること
- Python の仮想環境が LightRAG リポジトリで有効化できること

### C.3 セットアップ

#### C.3.1 MCP パッケージをインストール

```bash
# リポジトリルートで
uv sync --extra mcp
```

#### C.3.2 Claude Desktop の設定ファイルを編集

設定ファイルの場所:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

次の内容を追加します（既存の `mcpServers` があれば `lightrag` エントリを追記）:

```json
{
  "mcpServers": {
    "lightrag": {
      "command": "/Users/your-name/Dev-Work/LightRAG/.venv/bin/python",
      "args": ["/Users/your-name/Dev-Work/LightRAG/lightrag_mcp_server.py"],
      "env": {
        "LIGHTRAG_URL": "http://localhost:9621"
      }
    }
  }
}
```

> ⚠️ `command` と `args` のパスは**絶対パス**で、**ご自身の環境に合わせて書き換え**てください。

#### C.3.3 認証を有効化している場合

`.env` に `LIGHTRAG_API_KEY` を設定している場合は、`env` セクションに同じキーを指定します。

```json
"env": {
  "LIGHTRAG_URL": "http://localhost:9621",
  "LIGHTRAG_API_KEY": "your-configured-api-key"
}
```

#### C.3.4 Claude Desktop を再起動

設定ファイルを保存したら Claude Desktop を完全に終了し、再度起動します。チャット入力欄の近くに LightRAG ツールが表示されれば成功です。

### C.4 使用例

Claude Desktop のチャットで次のように依頼できます:

- 「LightRAG の knowledge graph に 2024 年の売上データをまとめて聞いて」
  → `lightrag_query` が呼ばれて結果が返る
- 「このメモを LightRAG に登録しておいて: ...」
  → `lightrag_insert` が呼ばれて知識グラフに追加
- 「LightRAG は今どんな状態？」
  → `lightrag_health` が呼ばれて稼働状況・処理中のチャンク数が返る

### C.5 環境変数

| 変数 | 既定値 | 説明 |
|---|---|---|
| `LIGHTRAG_URL` | `http://localhost:9621` | LightRAG API サーバーのベース URL |
| `LIGHTRAG_API_KEY` | （未設定） | LightRAG 側で API キー認証を有効化している場合に指定 |
| `LIGHTRAG_MCP_TIMEOUT` | `180` | API 呼び出しのタイムアウト（秒） |

### C.6 トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| Claude Desktop にツールが表示されない | 設定ファイルの JSON 構文エラー | JSON を検証ツールで確認 |
| `Connection error: ... is not reachable` | LightRAG サーバー未起動 | `docker compose up -d` で起動 |
| `Auth error (401)` / `Auth error (403)` | API キー不一致または未設定 | `.env` の `LIGHTRAG_API_KEY` と設定ファイルの env を一致させる |
| `Timeout` エラー | 大量データ登録で処理が長時間化 | `LIGHTRAG_MCP_TIMEOUT` を増やす（例: `"300"`） |
| `ModuleNotFoundError: No module named 'mcp'` | 依存未インストール | `uv sync --extra mcp` を実行 |

---

## おわりに

LightRAG を使えば、自分だけの「AI 専門家」を作ることができます。最初は戸惑うかもしれませんが、何度か使ううちに必ず慣れます。

**まずは小さな文書（数ページの PDF）をアップロードして、簡単な質問から試してみてください。**

楽しい AI ライフを！🚀
