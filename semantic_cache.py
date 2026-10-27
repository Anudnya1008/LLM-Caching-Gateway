import json
import numpy as np
from sentence_transformers import SentenceTransformer

from cache import redis_client

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.90
SEMANTIC_TTL = 3600

model = SentenceTransformer(MODEL_NAME)
from sentence_transformers import CrossEncoder
verifier = CrossEncoder("cross-encoder/quora-distilroberta-base")
VERIFY_THRESHOLD = 0.6

def generate_embedding(question: str):
    return model.encode(
        question,
        normalize_embeddings=True
    ).tolist()


def find_semantic_match(question: str):
    query_embedding = np.array(
        generate_embedding(question)
    )

    best_score = -1
    best_response = None
    best_question = None
    print("Searching semantic cache...", flush=True)
    # MVP: scan stored semantic cache entries.
    for key in redis_client.scan_iter(match="semantic:*"):
        cached = redis_client.get(key)

        if cached is None:
            continue

        data = json.loads(cached)
        stored_embedding = np.array(data["embedding"])
        similarity = np.dot(
                    query_embedding,
                    stored_embedding
                )
        print(
        f"Cached question: {data['question']}\n"
        f"Similarity score: {similarity:.4f}",
        flush=True
             )
        

        if similarity > best_score:
            best_score = similarity
            best_response = data["response"]
            best_question = data["question"]

    # if best_score >= SIMILARITY_THRESHOLD:
    #     return best_response
    if best_score >= SIMILARITY_THRESHOLD:
         verify_score = verifier.predict([(question, best_question)])[0]
         print(f"Verifier score: {verify_score:.4f}", flush=True)
         if verify_score >= VERIFY_THRESHOLD:
             return best_response

    return None


def store_semantic_response(question: str, response: str):
    from cache import generated_cache_key

    key = f"semantic:{generated_cache_key(question)}"

    data = {
        "question": question,
        "embedding": generate_embedding(question),
        "response": response
    }

    redis_client.setex(
        key,
        SEMANTIC_TTL,
        json.dumps(data)
    )