import os
import time
import numpy as np
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

fmt = "=== {:30} ==="
search_latency_fmt = "search latency = {:.4f}s"
num_entities, dim = 2, 8  #3000, 8

def connect_to_milvus():
    # Add a new connection alias `default` for Milvus server in `localhost:19530`
    # Actually the "default" alias is a built-in into PyMilvus.
    # If the address of Milvus is the same as `localhost:19530`, you can omit all
    # parameters and call the method as: `connections.connect()`.
    #
    # Note: the `using` parameter of the following methods is default to "default".
    print(fmt.format("Connecting to Milvus"))
    connections.connect(host='127.0.0.1', port='19530')
    # connections.connect(host='192.3.2.21', port='19530')
    # connections.connect(host='milvus-default.apac-consulting-cluster-0c5bc49aeb77d71c8b1376de07ab7b72-0000.us-south.containers.appdomain.cloud/')

    return connections

def collection_exists(collection_name):
    has = utility.has_collection(collection_name)
    print(f"Does collection {collection_name} exist in Milvus: {has}")
    return has

def create_collection(collection_name):
    # We're going to create a collection with 3 fields.
    # +-+------------+------------+------------------+------------------------------+
    # | | field name | field type | other attributes |       field description      |
    # +-+------------+------------+------------------+------------------------------+
    # |1|    "pk"    |   VarChar  |  is_primary=True |      "primary field"         |
    # | |            |            |   auto_id=False  |                              |
    # +-+------------+------------+------------------+------------------------------+
    # |2|  "random"  |    Double  |                  |      "a double field"        |
    # +-+------------+------------+------------------+------------------------------+
    # |3|"embeddings"| FloatVector|     dim=8        |  "float vector with dim 8"   |
    # +-+------------+------------+------------------+------------------------------+

    fields = [
        FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
        FieldSchema(name="random", dtype=DataType.DOUBLE),
        FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dim)
    ]

    schema = CollectionSchema(fields, "hello_milvus is the simplest demo to introduce the APIs")

    print(fmt.format(f"Create collection {collection_name}"))
    collection = Collection(collection_name, schema, consistency_level="Strong")
    return collection

def insert_data(collection):
    # We are going to insert 3000 rows of data into the collection
    # Data to be inserted must be organized in fields.
    #
    # The insert() method returns:
    # - either automatically generated primary keys by Milvus if auto_id=True in the schema;
    # - or the existing primary key field from the entities if auto_id=False in the schema.

    print(fmt.format("Start inserting entities"))
    rng = np.random.default_rng(seed=19530)
    entities = [
        # provide the pk field because `auto_id` is set to False
        [str(i) for i in range(num_entities)],
        rng.random(num_entities).tolist(),  # field random, only supports list
        rng.random((num_entities, dim)),    # field embeddings, supports numpy.ndarray and list
    ]
    print ("entities\n", entities)
    insert_result = collection.insert(entities)

    collection.flush()
    print(f"Number of entities in Milvus: {collection.num_entities}")  # check the num_entites

    return entities, insert_result

def create_index(collection):
    # We are going to create an IVF_FLAT index for hello_milvus collection.
    # create_index() can only be applied to `FloatVector` and `BinaryVector` fields.
    print(fmt.format("Start Creating index IVF_FLAT"))
    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128},
    }

    collection.create_index("embeddings", index)

################################################################################
# 5. search, query, and hybrid search
# After data were inserted into Milvus and indexed, you can perform:
# - search based on vector similarity
# - query based on scalar filtering(boolean, int, etc.)
# - hybrid search based on vector similarity and scalar filtering.
#
def search(collection):
    # Before conducting a search or a query, you need to load the data in `hello_milvus` into memory.
    print(fmt.format("Start loading"))
    collection.load()

    # -----------------------------------------------------------------------------
    # search based on vector similarity
    print(fmt.format("Start searching based on vector similarity"))
    vectors_to_search = entities[-1][-2:]
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }

    start_time = time.time()
    result = collection.search(vectors_to_search, "embeddings", search_params, limit=3, output_fields=["random"])
    end_time = time.time()

    for hits in result:
        for hit in hits:
            print(f"hit: {hit}, random field: {hit.entity.get('random')}")
    print(search_latency_fmt.format(end_time - start_time))

    # -----------------------------------------------------------------------------
    # query based on scalar filtering(boolean, int, etc.)
    print(fmt.format("Start querying with `random > 0.5`"))

    start_time = time.time()
    result = collection.query(expr="random > 0.5", output_fields=["random", "embeddings"])
    end_time = time.time()

    print(f"query result:\n-{result[0]}")
    print(search_latency_fmt.format(end_time - start_time))

    # -----------------------------------------------------------------------------
    # pagination
    r1 = collection.query(expr="random > 0.5", limit=4, output_fields=["random"])
    r2 = collection.query(expr="random > 0.5", offset=1, limit=3, output_fields=["random"])
    print(f"query pagination(limit=4):\n\t{r1}")
    print(f"query pagination(offset=1, limit=3):\n\t{r2}")


    # -----------------------------------------------------------------------------
    # hybrid search
    print(fmt.format("Start hybrid searching with `random > 0.5`"))

    start_time = time.time()
    result = collection.search(vectors_to_search, "embeddings", search_params, limit=3, expr="random > 0.5", output_fields=["random"])
    end_time = time.time()

    for hits in result:
        for hit in hits:
            print(f"hit: {hit}, random field: {hit.entity.get('random')}")
    print(search_latency_fmt.format(end_time - start_time))

###############################################################################
# 6. delete entities by PK
def delete_entities_by_PK(collection):
    # You can delete entities by their PK values using boolean expressions.
    ids = insert_result.primary_keys

    expr = f'pk in ["{ids[0]}" , "{ids[1]}"]'
    print(fmt.format(f"Start deleting with expr `{expr}`"))

    result = collection.query(expr=expr, output_fields=["random", "embeddings"])
    print(f"query before delete by expr=`{expr}` -> result: \n-{result[0]}\n-{result[1]}\n")

    collection.delete(expr)

    result = collection.query(expr=expr, output_fields=["random", "embeddings"])
    print(f"query after delete by expr=`{expr}` -> result: {result}\n")


###############################################################################
# 7. drop collection
def drop_collection():
    # Finally, drop the hello_milvus collection
    print(fmt.format("Drop collection `hello_milvus`"))
    utility.drop_collection("hello_milvus")

collection_name = "hello_milvus"
connect_to_milvus()
if collection_exists(collection_name):
    drop_collection()
milvus_collection = create_collection(collection_name)
entities, insert_result = insert_data(milvus_collection)
create_index(milvus_collection)
search(milvus_collection)
# delete_entities_by_PK(milvus_collection)

