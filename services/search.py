from rank_bm25 import BM25Okapi
import re
from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder,
)
from sentence_transformers.util import semantic_search


embedding_model = None
reranker_model = None
STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "how",
    "what",
    "why",
    "when",
    "where",
    "does",
    "do",
    "work",
    "works",
    "in",
    "on",
    "of",
    "for",
    "to",
    "and",
    "or",
    "with",
    "5g",
    "4g",
    "6g",
}
def clean_query(query):
    """
    Remove common words that are not useful
    for technical document retrieval.
    """

    words = query.lower().split()

    cleaned_words = []

    for word in words:

        word = word.strip(".,?!:;()")

        if word not in STOP_WORDS:
            cleaned_words.append(word)

    return cleaned_words
def search_clauses(query, clauses):
    """
    Search 3GPP clauses and rank them based on
    words appearing in the clause title and content.
    """

    query_words = clean_query(query)

    results = []

    for clause in clauses:

        title = clause["title"].lower()

        content = " ".join(
            clause["paragraphs"]
        ).lower()

        score = 0

        for word in query_words:

            # Title matches are more important
            if word in title:
                score += 5

            # Content matches also matter
            if word in content:
                score += 1

        if score > 0:

            results.append({
                "number": clause["number"],
                "title": clause["title"],
                "score": score,
                "paragraphs": clause["paragraphs"],
            })

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )
    print("Search terms:", query_words)

    return results
def semantic_search_clauses(query, clauses, top_k=5):
    global embedding_model

    if embedding_model is None:
        print("Loading semantic search model...")

        embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    documents = []

    for clause in clauses:

        content = " ".join(clause["paragraphs"])

        document_text = (
            f"{clause['title']}. "
            f"{content}"
        )

        documents.append(document_text)

    document_embeddings = embedding_model.encode(
        documents,
        convert_to_tensor=True
    )

    query_embedding = embedding_model.encode(
        query,
        convert_to_tensor=True
    )

    hits = semantic_search(
        query_embedding,
        document_embeddings,
        top_k=top_k
    )[0]

    results = []

    for hit in hits:

        clause = clauses[hit["corpus_id"]]

        results.append({
            "number": clause["number"],
            "title": clause["title"],
            "score": hit["score"],
        })

    return results
def tokenize(text):
    """
    Convert text into searchable words.
    """

    words = re.findall(
        r"[a-zA-Z0-9\-]+",
        text.lower()
    )

    return [
        word
        for word in words
        if word not in STOP_WORDS
    ]
def bm25_search_clauses(query, clauses, top_k=5):
    """
    Search 3GPP clauses using BM25 ranking.
    """

    documents = []

    for clause in clauses:

        content = " ".join(
            clause["paragraphs"]
        )

        searchable_text = (
            f"{clause['title']} "
            f"{clause['title']} "
            f"{content}"
        )

        documents.append(
            tokenize(searchable_text)
        )

    bm25 = BM25Okapi(documents)

    query_tokens = tokenize(query)

    scores = bm25.get_scores(
        query_tokens
    )
    query_text = " ".join(query_tokens)

    for index, clause in enumerate(clauses):

        title_tokens = tokenize(
            clause["title"]
        )

        title_text = " ".join(title_tokens)

        # Strong boost for exact title match
        if query_text == title_text:
            scores[index] += 10

        # Smaller boost when all query words
        # appear in the clause title
        elif all(
            word in title_tokens
            for word in query_tokens
        ):
            scores[index] += 5

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )

    results = []

    for index in ranked_indexes[:top_k]:

        clause = clauses[index]

        results.append({
            "number": clause["number"],
            "title": clause["title"],
            "score": scores[index],
        })

    return results
def hybrid_search_clauses(
    keyword_results,
    semantic_results,
    bm25_results,
    top_k=5,
):
    """
    Combine keyword, semantic, and BM25 rankings
    using Reciprocal Rank Fusion (RRF).
    """

    combined = {}

    def add_results(results, source):

        for rank, result in enumerate(
            results,
            start=1,
        ):
            number = result["number"]

            if number not in combined:
                combined[number] = {
                    "number": number,
                    "title": result["title"],
                    "keyword": 0.0,
                    "semantic": 0.0,
                    "bm25": 0.0,
                }

            # Reciprocal Rank Fusion
            rrf_score = 1 / (60 + rank)

            combined[number][source] += rrf_score

    add_results(
        keyword_results,
        "keyword",
    )

    add_results(
        semantic_results,
        "semantic",
    )

    add_results(
        bm25_results,
        "bm25",
    )

    for result in combined.values():

        result["score"] = (
            result["keyword"]
            + result["semantic"]
            + result["bm25"]
        )

    ranked_results = sorted(
        combined.values(),
        key=lambda result: result["score"],
        reverse=True,
    )

    return ranked_results[:top_k]
def rerank_clauses(
    query,
    hybrid_results,
    clauses,
    top_k=5,
):
    """
    Rerank hybrid-search candidates using
    a CrossEncoder relevance model.
    """

    global reranker_model

    if reranker_model is None:
        print("Loading reranker model...")

        reranker_model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L6-v2"
        )

    clause_lookup = {
        clause["number"]: clause
        for clause in clauses
    }

    pairs = []
    candidates = []

    for result in hybrid_results:

        clause = clause_lookup.get(
            result["number"]
        )

        if clause is None:
            continue

        content = " ".join(
            clause["paragraphs"]
        )

        candidate_text = (
            f"{clause['title']}. "
            f"{content}"
        )

        pairs.append([
            query,
            candidate_text,
        ])

        candidates.append(clause)

    scores = reranker_model.predict(
        pairs
    )

    reranked_results = []

    for clause, score in zip(
        candidates,
        scores,
    ):

        reranked_results.append({
            "number": clause["number"],
            "title": clause["title"],
            "score": float(score),
        })

    reranked_results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return reranked_results[:top_k]