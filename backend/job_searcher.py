from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import sqlite3
import os
from pathlib import Path


class JobSearcher:
    def __init__(self, vec_size):
        db_path = Path(__file__).parent / "job_search.db"
        if db_path.exists():
            os.remove(db_path)

        connections.connect(host="milvus-standalone", port="19530")

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="tfidf_vector", dtype=DataType.FLOAT_VECTOR, dim=vec_size)
        ]
        schema = CollectionSchema(fields, description="Job embeddings with TF-IDF")
        self.collection = Collection("jobs", schema)

        self.collection.create_index(
            field_name="tfidf_vector",
            index_params={
                "index_type": "HNSW",
                "metric_type": "L2",
                "params": {"M": 16, "efConstruction": 200}
            }
        )

        self.conn = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.cursor = self.conn.cursor()

        self.cursor.execute("DROP TABLE IF EXISTS job_data")
        self.cursor.execute('''
            CREATE TABLE job_data (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                description TEXT NOT NULL,
                published_date TEXT,
                is_hourly TEXT,
                hourly_low REAL,
                hourly_high REAL,
                budget REAL,
                country TEXT
            )
        ''')
        self.conn.commit()

    def index_jobs(self, dense_vectors, metadata):
        ids = list(range(dense_vectors.shape[0]))

        batch_size = 1000

        for i in range(0, len(ids), batch_size):
            batch_data = [
                ids[i:i + batch_size],
                dense_vectors[i:i + batch_size].tolist()
            ]
            self.cursor.executemany("INSERT INTO job_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    metadata[i:i + batch_size])
            self.collection.insert(batch_data)
            print(f"Добавлено уже {i + len(batch_data[0])} записей")

        self.collection.load()

    def search(self, query_vector, top_k=5):
        search_params = {
            "metric_type": "L2",
            "params": {"ef": 50}
        }

        results = self.collection.search(
            data=[query_vector],
            anns_field="tfidf_vector",
            param=search_params,
            limit=top_k
        )

        ids = []
        for hits in results:
            for hit in hits:
                ids.append(hit.id)
        return ids

    def get_db_connection(self):
        db_path = Path(__file__).parent / "job_search.db"
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return conn

    def fetch_metadata(self, ids):
        try:
            with self.get_db_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                placeholders = ','.join(['?'] * len(ids))
                query = f"SELECT * FROM job_data WHERE id IN ({placeholders})"
                cursor = conn.cursor()
                cursor.execute(query, ids)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
