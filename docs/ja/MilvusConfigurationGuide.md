# vector_db_storage_cls_kwargs による Milvus 設定

## 概要

Milvus のインデックスパラメータは `vector_db_storage_cls_kwargs` を通じて設定できます。これはフレームワーク統合シナリオ（例：RAGAnything や LightRAG 上に構築された他のフレームワークを使用する場合）における**推奨アプローチ**です。

## なぜ vector_db_storage_cls_kwargs を使用するのか？

✅ **フレームワーク統合**: 環境変数の変更なしに、フレームワーク層を通じて設定を渡すことが可能
✅ **プログラムによる設定**: 環境変数に依存せず、コード内でパラメータを設定
✅ **動的な設定**: 異なる RAG インスタンスに対して異なる設定が可能
✅ **クリーンな API**: 初期化時にすべてのパラメータを一箇所で渡せる

## サポートされるパラメータ

MilvusIndexConfig の全 11 パラメータが `vector_db_storage_cls_kwargs` で設定可能です：

### 基本設定
- `index_type`: インデックスタイプ（AUTOINDEX, HNSW, HNSW_SQ, IVF_FLAT 等）
- `metric_type`: 距離メトリック（COSINE, L2, IP）

### HNSW パラメータ
- `hnsw_m`: レイヤーごとの接続数（2-2048、デフォルト: 16）
- `hnsw_ef_construction`: 構築時の動的候補リストサイズ（デフォルト: 360）
- `hnsw_ef`: 検索時の動的候補リストサイズ（デフォルト: 200）

### HNSW_SQ パラメータ（Milvus 2.6.8 以降が必要）
- `sq_type`: 量子化タイプ（SQ4U, SQ6, SQ8, BF16, FP16、デフォルト: SQ8）
- `sq_refine`: リファインメントの有効化（デフォルト: False）
- `sq_refine_type`: リファインメントタイプ（SQ6, SQ8, BF16, FP16, FP32、デフォルト: FP32）
- `sq_refine_k`: リファインする候補数（デフォルト: 10）

### IVF パラメータ
- `ivf_nlist`: クラスタユニット数（1-65536、デフォルト: 1024）
- `ivf_nprobe`: クエリ対象ユニット数（デフォルト: 16）

## 設定の優先順位

設定は以下の順序で解決されます：
1. **vector_db_storage_cls_kwargs で渡されたパラメータ**（最優先）
2. 環境変数（MILVUS_INDEX_TYPE 等）
3. デフォルト値

## 使用例

### 基本的な設定

```python
from lightrag import LightRAG

rag = LightRAG(
    working_dir="./demo",
    vector_storage="MilvusVectorDBStorage",
    vector_db_storage_cls_kwargs={
        "cosine_better_than_threshold": 0.2,
        "index_type": "HNSW",
        "metric_type": "COSINE",
        "hnsw_m": 32,
        "hnsw_ef_construction": 256,
        "hnsw_ef": 150,
    }
)
```

### RAGAnything フレームワーク統合

```python
# In RAGAnything framework code:
def create_lightrag_instance(user_config):
    """Create LightRAG instance with user-provided Milvus configuration"""

    # User configuration from RAGAnything
    milvus_config = {
        "cosine_better_than_threshold": user_config.get("threshold", 0.2),
        "index_type": user_config.get("index_type", "HNSW"),
        "hnsw_m": user_config.get("hnsw_m", 32),
        # ... other parameters
    }

    # Pass configuration to LightRAG
    rag = LightRAG(
        working_dir=user_config["working_dir"],
        vector_storage="MilvusVectorDBStorage",
        vector_db_storage_cls_kwargs=milvus_config,
    )

    return rag
```

### HNSW_SQ を使用した高度な設定

```python
rag = LightRAG(
    working_dir="./demo",
    vector_storage="MilvusVectorDBStorage",
    vector_db_storage_cls_kwargs={
        "cosine_better_than_threshold": 0.2,
        "index_type": "HNSW_SQ",  # Requires Milvus 2.6.8+
        "metric_type": "COSINE",
        "hnsw_m": 48,
        "hnsw_ef_construction": 400,
        "hnsw_ef": 200,
        "sq_type": "SQ8",
        "sq_refine": True,
        "sq_refine_type": "FP32",
        "sq_refine_k": 20,
    }
)
```

### IVF 設定

```python
rag = LightRAG(
    working_dir="./demo",
    vector_storage="MilvusVectorDBStorage",
    vector_db_storage_cls_kwargs={
        "cosine_better_than_threshold": 0.2,
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "ivf_nlist": 2048,
        "ivf_nprobe": 32,
    }
)
```

## 実装の詳細

### 動作の仕組み

1. `MilvusVectorDBStorage.__post_init__()` が呼び出されると：
   ```python
   kwargs = self.global_config.get("vector_db_storage_cls_kwargs", {})
   index_config_keys = MilvusIndexConfig.get_config_field_names()
   index_config_params = {
       k: v for k, v in kwargs.items() if k in index_config_keys
   }
   self.index_config = MilvusIndexConfig(**index_config_params)
   ```

2. `MilvusIndexConfig.get_config_field_names()` がデータクラスから有効なパラメータ名を動的に抽出
3. kwargs から有効な Milvus インデックスパラメータのみが抽出される
4. パラメータは `MilvusIndexConfig` に渡され、デフォルト値の適用とバリデーションが行われる
5. kwargs で提供されなかったパラメータには環境変数がフォールバックとして使用される

### 自動同期

この実装は `MilvusIndexConfig.get_config_field_names()` を使用して有効なパラメータを動的に抽出します。これにより：
- ✅ `MilvusIndexConfig` に追加された新しいパラメータは**自動的に認識される**
- ✅ 重複するパラメータリストの管理が不要
- ✅ 設定パラメータの単一の信頼できる情報源を維持

## テスト

`vector_db_storage_cls_kwargs` を通じた設定は十分にテストされています：

```bash
# Run all kwargs bridge tests
python -m pytest tests/test_milvus_kwargs_bridge.py -v

# Test RAGAnything integration scenario specifically
python -m pytest tests/test_milvus_kwargs_bridge.py::TestMilvusKwargsParameterBridge::test_raganything_framework_integration_scenario -v

# Test all parameters support
python -m pytest tests/test_milvus_kwargs_bridge.py::TestMilvusKwargsParameterBridge::test_all_milvus_parameters_supported_via_kwargs -v
```

## サンプル

完全な動作サンプルは `examples/milvus_kwargs_configuration_demo.py` を参照してください。

## 後方互換性

✅ 既存のコードとの**100% 後方互換性**を維持
✅ 環境変数による設定は引き続き動作
✅ 既存のテストはすべてパス

## よくある質問

### Q: kwargs と環境変数を混在させることはできますか？
**A:** はい。`vector_db_storage_cls_kwargs` のパラメータが環境変数より優先されます。

### Q: kwargs 内の Milvus 以外のパラメータはどうなりますか？
**A:** 無視されます。有効な MilvusIndexConfig パラメータのみが抽出されます。これにより、フレームワークは Milvus 設定と並行して独自のパラメータを渡すことができます。

### Q: 環境変数を設定する必要がありますか？
**A:** いいえ。`vector_db_storage_cls_kwargs` を使用する場合、環境変数はオプションです。フォールバック値として機能します。

### Q: このアプローチは RAGAnything に推奨されますか？
**A:** はい。これは LightRAG 上に構築されるすべてのフレームワークにおける**推奨アプローチ**です。フレームワーク層を通じたクリーンな設定の受け渡しが可能になります。

## リファレンス

- テストスイート: `tests/test_milvus_kwargs_bridge.py`
- 実装: `lightrag/kg/milvus_impl.py`（1237-1272行目）
- サンプル: `examples/milvus_kwargs_configuration_demo.py`
- MilvusIndexConfig: `lightrag/kg/milvus_impl.py`（75-303行目）
