# 高度な機能

## マルチモーダルドキュメント処理（RAG-Anything 統合）

LightRAG は [RAG-Anything](https://github.com/HKUDS/RAG-Anything) と統合されています。これは、PDF、画像、Office ドキュメント、テーブル、数式など、多様なドキュメント形式にわたる高度な解析と RAG 機能を実現する**オールインワン マルチモーダルドキュメント処理 RAG システム**です。

**主な機能:**
- エンドツーエンドのマルチモーダルパイプライン：ドキュメント取り込みからマルチモーダルクエリ応答までの完全なワークフロー
- ユニバーサルドキュメントサポート：PDF、Office ドキュメント（DOC/DOCX/PPT/PPTX/XLS/XLSX）、画像、および多様なファイル形式
- 特化型コンテンツ分析：画像、テーブル、数式用の専用プロセッサ
- マルチモーダルナレッジグラフ：自動エンティティ抽出とクロスモーダルな関係性の発見
- ハイブリッドインテリジェント検索：テキストおよびマルチモーダルコンテンツにまたがる高度な検索

### クイックスタート

* Rag-Anything のインストール

```bash
pip install raganything
```

* RAGAnything の使用例

```python
import asyncio
from raganything import RAGAnything
from lightrag import LightRAG
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
import os

async def load_existing_lightrag():
    lightrag_working_dir = "./existing_lightrag_storage"

    from functools import partial

    lightrag_instance = LightRAG(
        working_dir=lightrag_working_dir,
        llm_model_func=lambda prompt, system_prompt=None, history_messages=[], **kwargs: openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key="your-api-key",
            **kwargs,
        ),
        embedding_func=EmbeddingFunc(
            embedding_dim=3072,
            max_token_size=8192,
            model="text-embedding-3-large",
            func=partial(
                openai_embed.func,
                model="text-embedding-3-large",
                api_key=api_key,
                base_url=base_url,
            ),
        )
    )

    await lightrag_instance.initialize_storages()

    rag = RAGAnything(
        lightrag=lightrag_instance,
        vision_model_func=lambda prompt, system_prompt=None, history_messages=[], image_data=None, **kwargs: openai_complete_if_cache(
            "gpt-4o",
            "",
            system_prompt=None,
            history_messages=[],
            messages=[
                {"role": "system", "content": system_prompt} if system_prompt else None,
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]} if image_data else {"role": "user", "content": prompt}
            ],
            api_key="your-api-key",
            **kwargs,
        ) if image_data else openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key="your-api-key",
            **kwargs,
        )
    )

    result = await rag.query_with_multimodal(
        "What data has been processed in this LightRAG instance?",
        mode="hybrid"
    )
    print("Query result:", result)

    await rag.process_document_complete(
        file_path="path/to/new/multimodal_document.pdf",
        output_dir="./output"
    )

if __name__ == "__main__":
    asyncio.run(load_existing_lightrag())
```

* 詳細なドキュメントと高度な使い方については、[RAG-Anything リポジトリ](https://github.com/HKUDS/RAG-Anything)を参照してください。

---

## トークン使用量の追跡

**概要と使い方**

LightRAG は、大規模言語モデルによるトークン消費量を監視・管理するための `TokenTracker` ツールを提供しています。この機能は、API コストの管理やパフォーマンスの最適化に役立ちます。

```python
from lightrag.utils import TokenTracker

token_tracker = TokenTracker()

# 方法1：コンテキストマネージャを使用（推奨）
with token_tracker:
    result1 = await llm_model_func("your question 1")
    result2 = await llm_model_func("your question 2")

# 方法2：手動でトークン使用量の記録を追加
token_tracker.reset()

rag.insert()

rag.query("your question 1", param=QueryParam(mode="naive"))
rag.query("your question 2", param=QueryParam(mode="mix"))

print("Token usage:", token_tracker.get_usage())
```

**使い方のヒント：**
- 長時間のセッションやバッチ操作では、コンテキストマネージャを使用してすべてのトークン消費量を自動的に追跡しましょう
- セグメント別の統計には、手動モードを使用し、適切なタイミングで `reset()` を呼び出してください
- トークン使用量を定期的に確認することで、異常な消費を早期に検出できます

**サンプルファイル：**
- `examples/lightrag_gemini_track_token_demo.py`：Google Gemini でのトークン追跡
- `examples/lightrag_siliconcloud_track_token_demo.py`：SiliconCloud でのトークン追跡

---

## データエクスポート機能

LightRAG では、分析、共有、バックアップのために、ナレッジグラフデータをさまざまな形式でエクスポートできます。

**基本的な使い方**

```python
# 基本的な CSV エクスポート（デフォルト形式）
rag.export_data("knowledge_graph.csv")

# 任意の形式を指定
rag.export_data("output.xlsx", file_format="excel")
```

**サポートされるファイル形式**

```python
rag.export_data("graph_data.csv", file_format="csv")
rag.export_data("graph_data.xlsx", file_format="excel")
rag.export_data("graph_data.md", file_format="md")
rag.export_data("graph_data.txt", file_format="txt")
```

**追加オプション**

ベクトル埋め込みをエクスポートに含める（オプション）：

```python
rag.export_data("complete_data.csv", include_vector_data=True)
```

すべてのエクスポートには、エンティティ情報（名前、ID、メタデータ）、リレーションデータ（エンティティ間の接続）、およびベクトルデータベースからの関係情報が含まれます。

---

## キャッシュ管理

**キャッシュのクリア**

`aclear_cache()` は `llm_response_cache` 内のすべてのキャッシュエントリをクリアします。モードやキャッシュタイプによる選択的なクリーンアップはサポートしていません。

```python
# 非同期
await rag.aclear_cache()

# 同期
rag.clear_cache()
```

クエリ関連のキャッシュを選択的にクリーンアップするには、`lightrag.tools.clean_llm_query_cache` ツールを使用し、[lightrag/tools/README_CLEAN_LLM_QUERY_CACHE.md](../lightrag/tools/README_CLEAN_LLM_QUERY_CACHE.md) のガイドを参照してください。このツールは `mix`、`hybrid`、`local`、`global` モードのクエリキャッシュとキーワードキャッシュを管理します。`default:extract:*` や `default:summary:*` などの抽出キャッシュはクリーン**しません**。

---

## Langfuse オブザーバビリティ統合

Langfuse は OpenAI クライアントのドロップイン代替を提供し、すべての LLM インタラクションを自動的に追跡します。これにより、開発者は RAG システムの監視、デバッグ、最適化が可能になります。

### インストール

```bash
pip install lightrag-hku[observability]
# または、ソースからインストール：
pip install -e ".[observability]"
```

### 設定

`.env` ファイルに以下を追加します：

```
## Langfuse オブザーバビリティ（オプション）
LANGFUSE_SECRET_KEY=""
LANGFUSE_PUBLIC_KEY=""
LANGFUSE_HOST="https://cloud.langfuse.com"  # またはセルフホストインスタンス
LANGFUSE_ENABLE_TRACE=true
```

### 機能

インストールと設定が完了すると、Langfuse はすべての OpenAI LLM 呼び出しを自動的にトレースします。ダッシュボードの機能：
- **トレーシング**：LLM 呼び出しチェーンの完全な表示
- **アナリティクス**：トークン使用量、レイテンシ、コストメトリクス
- **デバッグ**：プロンプトとレスポンスの検査
- **評価**：モデル出力の比較
- **モニタリング**：リアルタイムアラート

> **注意**：LightRAG は現在、OpenAI 互換 API 呼び出しのみを Langfuse と統合しています。Ollama、Azure、AWS Bedrock などの API は、Langfuse オブザーバビリティではまだサポートされていません。

---

## RAGAS ベースの評価

**RAGAS**（Retrieval Augmented Generation Assessment）は、LLM を使用した RAG システムの参照不要な評価フレームワークです。LightRAG は RAGAS に基づく評価スクリプトを提供しています。詳細については、[RAGAS ベースの評価フレームワーク](../lightrag/evaluation/README_EVALUASTION_RAGAS.md)を参照してください。
