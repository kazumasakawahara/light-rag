<div align="center">

<div style="margin: 20px 0;">
  <img src="./assets/logo.png" width="120" height="120" alt="LightRAG Logo" style="border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 217, 255, 0.3);">
</div>

# 🚀 LightRAG: シンプルで高速な検索拡張生成

<div align="center">
    <a href="https://trendshift.io/repositories/13043" target="_blank"><img src="https://trendshift.io/api/badge/repositories/13043" alt="HKUDS%2FLightRAG | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</div>

<div align="center">
  <div style="width: 100%; height: 2px; margin: 20px 0; background: linear-gradient(90deg, transparent, #00d9ff, transparent);"></div>
</div>

<div align="center">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 25px; text-align: center;">
    <p>
      <a href='https://github.com/HKUDS/LightRAG'><img src='https://img.shields.io/badge/🔥Project-Page-00d9ff?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e'></a>
      <a href='https://arxiv.org/abs/2410.05779'><img src='https://img.shields.io/badge/📄arXiv-2410.05779-ff6b6b?style=for-the-badge&logo=arxiv&logoColor=white&labelColor=1a1a2e'></a>
      <a href="https://github.com/HKUDS/LightRAG/stargazers"><img src='https://img.shields.io/github/stars/HKUDS/LightRAG?color=00d9ff&style=for-the-badge&logo=star&logoColor=white&labelColor=1a1a2e' /></a>
    </p>
    <p>
      <img src="https://img.shields.io/badge/🐍Python-3.10-4ecdc4?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e">
      <a href="https://pypi.org/project/lightrag-hku/"><img src="https://img.shields.io/pypi/v/lightrag-hku.svg?style=for-the-badge&logo=pypi&logoColor=white&labelColor=1a1a2e&color=ff6b6b"></a>
    </p>
    <p>
      <a href="https://discord.gg/yF2MmDJyGJ"><img src="https://img.shields.io/badge/💬Discord-Community-7289da?style=for-the-badge&logo=discord&logoColor=white&labelColor=1a1a2e"></a>
      <a href="https://github.com/HKUDS/LightRAG/issues/285"><img src="https://img.shields.io/badge/💬WeChat-Group-07c160?style=for-the-badge&logo=wechat&logoColor=white&labelColor=1a1a2e"></a>
    </p>
    <p>
      <a href="README-zh.md"><img src="https://img.shields.io/badge/🇨🇳中文版-1a1a2e?style=for-the-badge"></a>
      <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸English-1a1a2e?style=for-the-badge"></a>
      <a href="README-ja.md"><img src="https://img.shields.io/badge/🇯🇵日本語版-1a1a2e?style=for-the-badge"></a>
    </p>
    <p>
      <a href="https://pepy.tech/projects/lightrag-hku"><img src="https://static.pepy.tech/personalized-badge/lightrag-hku?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads"></a>
    </p>
  </div>
</div>

</div>

<div align="center" style="margin: 30px 0;">
  <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="800">
</div>

<div align="center" style="margin: 30px 0;">
    <img src="./README.assets/b2aaf634151b4706892693ffb43d9093.png" width="800" alt="LightRAG Diagram">
</div>

---

<div align="center">
  <table>
    <tr>
      <td style="vertical-align: middle;">
        <img src="./assets/LiteWrite.png"
             width="56"
             height="56"
             alt="LiteWrite"
             style="border-radius: 12px;" />
      </td>
      <td style="vertical-align: middle; padding-left: 12px;">
        <a href="https://litewrite.ai">
          <img src="https://img.shields.io/badge/🚀%20LiteWrite-AI%20Native%20LaTeX%20Editor-ff6b6b?style=for-the-badge&logoColor=white&labelColor=1a1a2e">
        </a>
      </td>
    </tr>
  </table>
</div>

---

## 🎉 ニュース
- [2026.03]🎯[新機能]: 統合ストレージバックエンドとして**OpenSearch**を統合し、LightRAGの4つすべてのストレージを包括的にサポートしました。
- [2026.03]🎯[新機能]: セットアップウィザードを導入しました。Dockerによるエンベディング、リランキング、ストレージバックエンドのローカルデプロイをサポートします。
- [2025.11]🎯[新機能]: **RAGASによる評価**と**Langfuseによるトレーシング**を統合しました。コンテキスト精度メトリクスをサポートするために、クエリ結果とともに取得されたコンテキストを返すようAPIを更新しました。
- [2025.10]🎯[スケーラビリティ強化]: 処理のボトルネックを排除し、**大規模データセットの効率的な処理**をサポートしました。
- [2025.09]🎯[新機能] Qwen3-30B-A3Bなどの**オープンソースLLM**におけるナレッジグラフ抽出精度を向上しました。
- [2025.08]🎯[新機能] **リランカー**をサポートし、混合クエリのパフォーマンスを大幅に向上しました（デフォルトのクエリモードとして設定）。
- [2025.08]🎯[新機能] 最適なクエリパフォーマンスを確保するための自動KG再生成を伴う**ドキュメント削除**機能を追加しました。
- [2025.06]🎯[新リリース] 私たちのチームは[RAG-Anything](https://github.com/HKUDS/RAG-Anything)をリリースしました。テキスト、画像、表、数式をシームレスに処理する**オールインワンマルチモーダルRAG**システムです。
- [2025.06]🎯[新機能] LightRAGは[RAG-Anything](https://github.com/HKUDS/RAG-Anything)統合により、PDF、画像、Officeドキュメント、表、数式など多様なフォーマットにわたるシームレスなドキュメント解析とRAG機能を実現する包括的なマルチモーダルデータ処理をサポートします。詳細は新しい[マルチモーダルセクション](https://github.com/HKUDS/LightRAG/?tab=readme-ov-file#multimodal-document-processing-rag-anything-integration)をご参照ください。
- [2025.03]🎯[新機能] LightRAGが引用機能をサポートし、適切なソース帰属と強化されたドキュメント追跡が可能になりました。
- [2025.02]🎯[新機能] MongoDBを統合データ管理のためのオールインワンストレージソリューションとして利用できるようになりました。
- [2025.02]🎯[新リリース] 私たちのチームは[VideoRAG](https://github.com/HKUDS/VideoRAG)をリリースしました。超長尺動画を理解するためのRAGシステムです。
- [2025.01]🎯[新リリース] 私たちのチームは[MiniRAG](https://github.com/HKUDS/MiniRAG)をリリースしました。小規模モデルでRAGをよりシンプルにします。
- [2025.01]🎯PostgreSQLをデータ管理のためのオールインワンストレージソリューションとして利用できるようになりました。
- [2024.11]🎯[新リソース] LightRAGの包括的なガイドが[LearnOpenCV](https://learnopencv.com/lightrag)で公開されました。詳細なチュートリアルとベストプラクティスをご覧ください。ブログ著者の素晴らしい貢献に深く感謝いたします！
- [2024.11]🎯[新機能] LightRAG WebUIを導入しました。直感的なWebベースのダッシュボードでLightRAGナレッジの挿入、クエリ、可視化が可能なインターフェースです。
- [2024.11]🎯[新機能] [Neo4Jをストレージとして使用](https://github.com/HKUDS/LightRAG?tab=readme-ov-file#using-neo4j-for-storage)できるようになりました。グラフデータベースをサポートします。
- [2024.10]🎯[新機能] [LightRAG紹介動画](https://youtu.be/oageL-1I0GE)へのリンクを追加しました。LightRAGの機能をウォークスルーで紹介しています。著者の素晴らしい貢献に感謝いたします！
- [2024.10]🎯[新チャンネル] [Discordチャンネル](https://discord.gg/yF2MmDJyGJ)を開設しました！💬 共有、議論、コラボレーションのためのコミュニティにぜひご参加ください！ 🎉🎉

<details>
  <summary style="font-size: 1.4em; font-weight: bold; cursor: pointer; display: list-item;">
    アルゴリズムフローチャート
  </summary>

![LightRAG Indexing Flowchart](https://learnopencv.com/wp-content/uploads/2024/11/LightRAG-VectorDB-Json-KV-Store-Indexing-Flowchart-scaled.jpg)
*図1: LightRAG インデキシングフローチャート - 画像出典 : [Source](https://learnopencv.com/lightrag/)*
![LightRAG Retrieval and Querying Flowchart](https://learnopencv.com/wp-content/uploads/2024/11/LightRAG-Querying-Flowchart-Dual-Level-Retrieval-Generation-Knowledge-Graphs-scaled.jpg)
*図2: LightRAG 検索・クエリフローチャート - 画像出典 : [Source](https://learnopencv.com/lightrag/)*

</details>

## インストール

**💡 uvによるパッケージ管理の使用**: このプロジェクトでは、高速で信頼性の高いPythonパッケージ管理のために[uv](https://docs.astral.sh/uv/)を使用しています。まずuvをインストールしてください：`curl -LsSf https://astral.sh/uv/install.sh | sh`（Unix/macOS）または `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`（Windows）

> **注意**: pipも使用できますが、より優れたパフォーマンスとより信頼性の高い依存関係管理のためにuvを推奨します。
>
> **📦 オフラインデプロイメント**: オフラインまたはエアギャップ環境の場合、すべての依存関係とキャッシュファイルの事前インストール手順については[オフラインデプロイメントガイド](./docs/OfflineDeployment.md)をご参照ください。

### LightRAG Serverのインストール

LightRAG Serverは、Web UIとAPIサポートを提供するように設計されています。Web UIはドキュメントのインデキシング、ナレッジグラフの探索、シンプルなRAGクエリインターフェースを提供します。LightRAG ServerはOllama互換インターフェースも提供しており、LightRAGをOllamaチャットモデルとしてエミュレートすることを目的としています。これにより、Open WebUIなどのAIチャットボットがLightRAGに簡単にアクセスできます。

* PyPIからのインストール

```bash
### uvを使用してLightRAG Serverをツールとしてインストール（推奨）
uv tool install "lightrag-hku[api]"

### またはpipを使用
# python -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
# pip install "lightrag-hku[api]"

### フロントエンドアーティファクトのビルド
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..

# envファイルのセットアップ
# GitHubリポジトリルートからダウンロードするか、
# ローカルソースチェックアウトからコピーしてenv.exampleファイルを取得してください。
cp env.example .env  # .envをLLMおよびエンベディングの設定で更新してください
# サーバーの起動
lightrag-server
```

* ソースからのインストール

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG

# 開発環境のブートストラップ（推奨）
make dev
source .venv/bin/activate  # 仮想環境の有効化（Linux/macOS）
# Windowsの場合: .venv\Scripts\activate

# make devはテストツールチェーンと完全なオフラインスタック
# （API、ストレージバックエンド、プロバイダー統合）をインストールし、フロントエンドをビルドします。
# サーバーを起動する前にmake env-baseを実行するか、env.exampleを.envにコピーしてください。

# uvによる同等の手動ステップ
# 注意: uv syncは自動的に.venv/に仮想環境を作成します
uv sync --extra test --extra offline
source .venv/bin/activate  # 仮想環境の有効化（Linux/macOS）
# Windowsの場合: .venv\Scripts\activate

### またはpipと仮想環境を使用
# python -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
# pip install -e ".[test,offline]"

# フロントエンドアーティファクトのビルド
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..

# envファイルのセットアップ
make env-base  # または: cp env.example .env として手動で更新
# API-WebUIサーバーの起動
lightrag-server
```

* Docker ComposeによるLightRAG Serverの起動

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
cp env.example .env  # .envをLLMおよびエンベディングの設定で更新してください
# .envでLLMとエンベディングの設定を変更
docker compose up
```

> LightRAG Dockerイメージの過去のバージョンはこちらから確認できます：[LightRAG Docker Images]( https://github.com/HKUDS/LightRAG/pkgs/container/lightrag)

### セットアップツールによる.envファイルの作成

`env.example`を手動で編集する代わりに、対話型セットアップウィザードを使用して設定済みの`.env`と、必要に応じて`docker-compose.final.yml`を生成できます：

```bash
make env-base           # 必須の最初のステップ: LLM、エンベディング、リランカー
make env-storage        # オプション: ストレージバックエンドとデータベースサービス
make env-server         # オプション: サーバーポート、認証、SSL
make env-base-rewrite   # オプション: ウィザード管理のcomposeサービスを強制再生成
make env-storage-rewrite # オプション: ウィザード管理のcomposeサービスを強制再生成
make env-security-check # オプション: 現在の.envのセキュリティリスクを監査
```

すべてのターゲットの詳細な説明については[docs/InteractiveSetup.md](./docs/InteractiveSetup.md)をご参照ください。
セットアップウィザードは設定のみを更新します。デプロイメント前に現在の`.env`のセキュリティリスクを監査するには、`make env-security-check`を別途実行してください。
デフォルトでは、セットアップを再実行すると変更されていないウィザード管理のcomposeサービスブロックは保持されます。管理対象ブロックをバンドルされたテンプレートから再構築する必要がある場合にのみ`*-rewrite`ターゲットを使用してください。

### LightRAG Coreのインストール

* ソースからのインストール（推奨）

```bash
cd LightRAG
# 注意: uv syncは自動的に.venv/に仮想環境を作成します
uv sync
source .venv/bin/activate  # 仮想環境の有効化（Linux/macOS）
# Windowsの場合: .venv\Scripts\activate

# または: pip install -e .
```

* PyPIからのインストール

```bash
uv pip install lightrag-hku
# または: pip install lightrag-hku
```

## クイックスタート

### LightRAGに必要なLLMと技術スタック

LightRAGはドキュメントからエンティティ・関係抽出タスクをLLMに要求するため、従来のRAGと比較して大規模言語モデル（LLM）の能力に対する要求が大幅に高くなっています。適切なエンベディングモデルとリランカーモデルを設定することも、クエリパフォーマンスの向上に不可欠です。

- **LLMの選択**:
  - 少なくとも320億パラメータのLLMを使用することを推奨します。
  - コンテキスト長は少なくとも32KBが必要で、64KBを推奨します。
  - ドキュメントインデキシング段階では推論モデルの選択は推奨しません。
  - クエリ段階では、より良いクエリ結果を得るために、インデキシング段階で使用したモデルよりも高い能力を持つモデルを選択することを推奨します。
- **エンベディングモデル**:
  - 高性能なエンベディングモデルはRAGに不可欠です。
  - `BAAI/bge-m3`や`text-embedding-3-large`などの主要な多言語エンベディングモデルの使用を推奨します。
  - **重要な注意**: エンベディングモデルはドキュメントインデキシング前に決定する必要があり、ドキュメントクエリフェーズでも同じモデルを使用する必要があります。特定のストレージソリューション（例：PostgreSQL）では、初回テーブル作成時にベクトル次元を定義する必要があります。そのため、エンベディングモデルを変更する場合は、既存のベクトル関連テーブルを削除し、LightRAGが新しい次元で再作成できるようにする必要があります。
- **リランカーモデルの設定**:
  - リランカーモデルを設定することで、LightRAGの検索パフォーマンスを大幅に向上させることができます。
  - リランカーモデルが有効な場合、デフォルトのクエリモードとして「mixモード」を設定することを推奨します。
  - `BAAI/bge-reranker-v2-m3`やJinaなどのサービスが提供するモデルなど、主要なリランカーモデルの使用を推奨します。

### LightRAG Serverのクイックスタート

LightRAG Serverは、Web UIとAPIサポートを提供するように設計されています。LightRAG Serverは包括的なナレッジグラフ可視化機能を提供します。さまざまな重力レイアウト、ノードクエリ、サブグラフフィルタリングなどをサポートしています。LightRAG Serverの詳細については、[LightRAG Server](./docs/LightRAG-API-Server.md)をご参照ください。

![iShot_2025-03-23_12.40.08](./README.assets/iShot_2025-03-23_12.40.08.png)


### LightRAG Coreのクイックスタート

LightRAG Coreを使い始めるには、`examples`フォルダにあるサンプルコードをご参照ください。また、ローカルセットアップの手順を案内する[動画デモ](https://www.youtube.com/watch?v=g21royNJ4fw)も提供しています。OpenAI APIキーをお持ちであれば、すぐにデモを実行できます：

```bash
### プロジェクトフォルダでデモコードを実行してください
cd LightRAG
### OpenAIのAPI-KEYを設定
export OPENAI_API_KEY="sk-...your_opeai_key..."
### Charles Dickensの「A Christmas Carol」のデモドキュメントをダウンロード
curl https://raw.githubusercontent.com/gusye1234/nano-graphrag/main/tests/mock_data.txt > ./book.txt
### デモコードを実行
python examples/lightrag_openai_demo.py
```

ストリーミングレスポンスの実装例については、`examples/lightrag_openai_compatible_demo.py`をご参照ください。実行前に、サンプルコードのLLMおよびエンベディング設定を適切に変更してください。

**注意1**: デモプログラム実行時、テストスクリプトによって使用するエンベディングモデルが異なる場合があります。別のエンベディングモデルに切り替える場合は、データディレクトリ（`./dickens`）をクリアする必要があります。そうしないとプログラムがエラーになる可能性があります。LLMキャッシュを保持したい場合は、データディレクトリをクリアする際に`kv_store_llm_response_cache.json`ファイルを保存しておくことができます。

**注意2**: `lightrag_openai_demo.py`と`lightrag_openai_compatible_demo.py`のみが公式にサポートされているサンプルコードです。その他のサンプルファイルは、完全なテストと最適化が行われていないコミュニティの貢献です。

## LightRAG Coreを使ったプログラミング

Core APIの完全なリファレンス（初期化パラメータ、`QueryParam`、LLM/エンベディングプロバイダーの例（OpenAI、Ollama、Azure、Gemini、HuggingFace、LlamaIndex）、リランカーインジェクション、挿入操作、エンティティ/リレーション管理、削除/マージ）については、**[docs/ProgramingWithCore.md](./docs/ProgramingWithCore.md)**をご参照ください。

> ⚠️ **LightRAGをプロジェクトに統合する場合は、LightRAG Serverが提供するREST APIの利用を推奨します**。LightRAG Coreは通常、組み込みアプリケーション向け、または研究・評価を実施したい研究者向けです。

### 高度な機能

LightRAGは、トークン使用量の追跡、ナレッジグラフデータのエクスポート、LLMキャッシュ管理、Langfuseオブザーバビリティ統合、RAGASベースの評価などの追加機能を提供します。**[docs/AdvancedFeatures.md](./docs/AdvancedFeatures.md)**をご参照ください。

### マルチモーダルドキュメント処理（RAG-Anything統合）

LightRAGは[RAG-Anything](https://github.com/HKUDS/RAG-Anything)と統合し、PDF、Officeドキュメント、画像、表、数式にわたるエンドツーエンドのマルチモーダルRAGを実現します。セットアップと使用例については、**[docs/AdvancedFeatures.md](./docs/AdvancedFeatures.md)**をご参照ください。

> LightRAG Serverは、近日中にRAG-Anythingのマルチモーダル処理機能をファイル処理パイプラインに統合する予定です。ご期待ください。

## 論文の実験結果の再現

LightRAGは、農業、コンピュータサイエンス、法律、混合ドメインにおいて、NaiveRAG、RQ-RAG、HyDE、GraphRAGを一貫して上回っています。完全な評価方法、プロンプト、再現手順については、**[docs/Reproduce.md](./docs/Reproduce.md)**をご参照ください。

**全体パフォーマンステーブル**

||**Agriculture**||**CS**||**Legal**||**Mix**||
|----------------------|---------------|------------|------|------------|---------|------------|-------|------------|
||NaiveRAG|**LightRAG**|NaiveRAG|**LightRAG**|NaiveRAG|**LightRAG**|NaiveRAG|**LightRAG**|
|**Comprehensiveness**|32.4%|**67.6%**|38.4%|**61.6%**|16.4%|**83.6%**|38.8%|**61.2%**|
|**Diversity**|23.6%|**76.4%**|38.0%|**62.0%**|13.6%|**86.4%**|32.4%|**67.6%**|
|**Empowerment**|32.4%|**67.6%**|38.8%|**61.2%**|16.4%|**83.6%**|42.8%|**57.2%**|
|**Overall**|32.4%|**67.6%**|38.8%|**61.2%**|15.2%|**84.8%**|40.0%|**60.0%**|
||RQ-RAG|**LightRAG**|RQ-RAG|**LightRAG**|RQ-RAG|**LightRAG**|RQ-RAG|**LightRAG**|
|**Comprehensiveness**|31.6%|**68.4%**|38.8%|**61.2%**|15.2%|**84.8%**|39.2%|**60.8%**|
|**Diversity**|29.2%|**70.8%**|39.2%|**60.8%**|11.6%|**88.4%**|30.8%|**69.2%**|
|**Empowerment**|31.6%|**68.4%**|36.4%|**63.6%**|15.2%|**84.8%**|42.4%|**57.6%**|
|**Overall**|32.4%|**67.6%**|38.0%|**62.0%**|14.4%|**85.6%**|40.0%|**60.0%**|
||HyDE|**LightRAG**|HyDE|**LightRAG**|HyDE|**LightRAG**|HyDE|**LightRAG**|
|**Comprehensiveness**|26.0%|**74.0%**|41.6%|**58.4%**|26.8%|**73.2%**|40.4%|**59.6%**|
|**Diversity**|24.0%|**76.0%**|38.8%|**61.2%**|20.0%|**80.0%**|32.4%|**67.6%**|
|**Empowerment**|25.2%|**74.8%**|40.8%|**59.2%**|26.0%|**74.0%**|46.0%|**54.0%**|
|**Overall**|24.8%|**75.2%**|41.6%|**58.4%**|26.4%|**73.6%**|42.4%|**57.6%**|
||GraphRAG|**LightRAG**|GraphRAG|**LightRAG**|GraphRAG|**LightRAG**|GraphRAG|**LightRAG**|
|**Comprehensiveness**|45.6%|**54.4%**|48.4%|**51.6%**|48.4%|**51.6%**|**50.4%**|49.6%|
|**Diversity**|22.8%|**77.2%**|40.8%|**59.2%**|26.4%|**73.6%**|36.0%|**64.0%**|
|**Empowerment**|41.2%|**58.8%**|45.2%|**54.8%**|43.6%|**56.4%**|**50.8%**|49.2%|
|**Overall**|45.2%|**54.8%**|48.0%|**52.0%**|47.2%|**52.8%**|**50.4%**|49.6%|


## 🔗 関連プロジェクト

*エコシステムと拡張機能*

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/HKUDS/RAG-Anything">
          <div style="width: 100px; height: 100px; background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 217, 255, 0.05) 100%); border-radius: 15px; border: 1px solid rgba(0, 217, 255, 0.2); display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <span style="font-size: 32px;">📸</span>
          </div>
          <b>RAG-Anything</b><br>
          <sub>マルチモーダルRAG</sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/HKUDS/VideoRAG">
          <div style="width: 100px; height: 100px; background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 217, 255, 0.05) 100%); border-radius: 15px; border: 1px solid rgba(0, 217, 255, 0.2); display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <span style="font-size: 32px;">🎥</span>
          </div>
          <b>VideoRAG</b><br>
          <sub>超長尺動画RAG</sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/HKUDS/MiniRAG">
          <div style="width: 100px; height: 100px; background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 217, 255, 0.05) 100%); border-radius: 15px; border: 1px solid rgba(0, 217, 255, 0.2); display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <span style="font-size: 32px;">✨</span>
          </div>
          <b>MiniRAG</b><br>
          <sub>超シンプルRAG</sub>
        </a>
      </td>
    </tr>
  </table>
</div>

---

## ⭐ Star履歴

[![Star History Chart](https://api.star-history.com/svg?repos=HKUDS/LightRAG&type=Date)](https://star-history.com/#HKUDS/LightRAG&Date)

## 🤝 コントリビューション

<div align="center">
  バグ修正、新機能、ドキュメントの改善など、あらゆる種類のコントリビューションを歓迎します。<br>
  プルリクエストを送信する前に、<a href=".github/CONTRIBUTING.md"><strong>コントリビューションガイド</strong></a>をお読みください。
</div>

<br>

<div align="center">
  貴重なコントリビューションをいただいたすべてのコントリビューターに感謝いたします。
</div>

<div align="center">
  <a href="https://github.com/HKUDS/LightRAG/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=HKUDS/LightRAG" style="border-radius: 15px; box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);" />
  </a>
</div>


## 📖 引用

```python
@article{guo2024lightrag,
title={LightRAG: Simple and Fast Retrieval-Augmented Generation},
author={Zirui Guo and Lianghao Xia and Yanhua Yu and Tu Ao and Chao Huang},
year={2024},
eprint={2410.05779},
archivePrefix={arXiv},
primaryClass={cs.IR}
}
```

---

<div align="center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 30px; margin: 30px 0;">
  <div>
    <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="500">
  </div>
  <div style="margin-top: 20px;">
    <a href="https://github.com/HKUDS/LightRAG" style="text-decoration: none;">
      <img src="https://img.shields.io/badge/⭐%20Star%20us%20on%20GitHub-1a1a2e?style=for-the-badge&logo=github&logoColor=white">
    </a>
    <a href="https://github.com/HKUDS/LightRAG/issues" style="text-decoration: none;">
      <img src="https://img.shields.io/badge/🐛%20Report%20Issues-ff6b6b?style=for-the-badge&logo=github&logoColor=white">
    </a>
    <a href="https://github.com/HKUDS/LightRAG/discussions" style="text-decoration: none;">
      <img src="https://img.shields.io/badge/💬%20Discussions-4ecdc4?style=for-the-badge&logo=github&logoColor=white">
    </a>
  </div>
</div>

<div align="center">
  <div style="width: 100%; max-width: 600px; margin: 20px auto; padding: 20px; background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 217, 255, 0.05) 100%); border-radius: 15px; border: 1px solid rgba(0, 217, 255, 0.2);">
    <div style="display: flex; justify-content: center; align-items: center; gap: 15px;">
      <span style="font-size: 24px;">⭐</span>
      <span style="color: #00d9ff; font-size: 18px;">LightRAGをご覧いただきありがとうございます！</span>
      <span style="font-size: 24px;">⭐</span>
    </div>
  </div>
</div>
