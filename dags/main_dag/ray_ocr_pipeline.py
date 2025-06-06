from airflow.decorators import dag, task
from datetime import datetime
import ray

@dag(start_date=datetime(2023, 1, 1), schedule=None, catchup=False)
def ray_pipeline():
    
    image_path = "/usr/local/airflow/include/example.png"

    @task
    def run_ray_pipeline():
        ray.init(ignore_reinit_error=True)

        @ray.remote
        def ocr(image_path):
            import pytesseract
            from PIL import Image
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text

        @ray.remote
        def chunk(text):
            return [text[i:i+500] for i in range(0, len(text), 500)]

        @ray.remote
        def embed(chunks):
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(chunks)
            return embeddings

        @ray.remote
        def store(embeddings):
            import faiss
            import numpy as np
            dim = embeddings.shape[1]
            index = faiss.IndexFlatL2(dim)
            index.add(embeddings.astype(np.float32))
            faiss.write_index(index, "/tmp/index.faiss")
            return "Embeddings stored in FAISS index."

        # Execute all steps
        text_future = ocr.remote(image_path)
        chunk_future = chunk.remote(text_future)
        embed_future = embed.remote(chunk_future)
        store_future = store.remote(embed_future)

        # Print final output
        result = ray.get(store_future)
        print(result)

    run_ray_pipeline()

dag = ray_pipeline()
