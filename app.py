from services.spec_discovery import (
    detect_rat,
    get_spec_series,
    check_3gpp_connection,
    get_spec_versions,
    decode_3gpp_version,
)
from services.search import (
    bm25_search_clauses,
    hybrid_search_clauses,
    rerank_clauses,
)
from services.terminology import extract_abbreviations
from services.terminology import find_abbreviation_clause
from services.spec_catalog import (
    get_series_specs,
)
from services.search import search_clauses
question = input("Ask Spexalation: ")

rat = detect_rat(question)
series = get_spec_series(rat)
connected = check_3gpp_connection()

print()
print("Detected RAT:", rat)
print("3GPP spec series:", series)
print("3GPP connection:", connected)
print()
print("Testing dynamic 3GPP version discovery...")

versions = get_spec_versions("38.321")

print("Number of versions found:", len(versions))

for version in versions[-10:]:
    print(version)
latest_file = versions[-1]

print()
print("Latest file:", latest_file)
print("Decoded version:", decode_3gpp_version(latest_file))
print()
print("Discovering 3GPP specifications...")

specs = get_series_specs("38")

print("Number of 38-series specifications:", len(specs))

for spec in specs[:20]:
    print(spec)
from services.version_manager import (
    check_spec_update,
    register_spec,
)


print()
print("Checking local Spexalation database...")

result = check_spec_update("38.321")

print("Database status:", result["status"])

if result["status"] == "missing":
    print("No local copy found.")
    print("3GPP version:", result["remote"]["version"])
    print("3GPP file:", result["remote"]["filename"])
from services.spec_downloader import build_spec_url


if result["status"] == "missing":

    remote = result["remote"]

    url = build_spec_url(
        remote["spec"],
        remote["filename"],
    )

    print()
    print("Download URL:")
    print(url)
from services.spec_downloader import download_spec


if result["status"] == "missing":

    remote = result["remote"]

    print()
    print("Local specification not found.")
    print("Downloading latest version from 3GPP...")

    destination = download_spec(
        remote["spec"],
        remote["version"],
        remote["filename"],
    )
    register_spec(
        remote["spec"],
        remote["version"],
        remote["filename"],
        destination,
    )

    print()
    print("Specification stored at:")
    print(destination)
from services.spec_loader import (
    load_docx,
    extract_clauses,
)


print()
print("Reading local 3GPP specification...")

paragraphs = load_docx(
    "data/specs/38.321/19.4.0/38321-j40.docx"
)
clauses = extract_clauses(paragraphs)
abbreviations = extract_abbreviations(
    clauses
)

print()
print(
    "Abbreviations extracted:",
    len(abbreviations)
)

for abbreviation in [
    "SR",
    "BSR",
    "BWP",
    "PUCCH",
    "PUSCH",
    "UL-SCH",
    "RNTI",
]:
    print(
        abbreviation,
        "->",
        abbreviations.get(
            abbreviation,
            "Not found"
        )
    )
abbreviation_clause = find_abbreviation_clause(
    clauses
)

print()
print("3GPP Abbreviation Clause...")

if abbreviation_clause:

    print(
        "Clause:",
        abbreviation_clause["number"]
    )

    print(
        "Title:",
        abbreviation_clause["title"]
    )

    print()

    for paragraph in abbreviation_clause["paragraphs"][:30]:
        print(paragraph)

else:
    print("Abbreviation clause not found.")

print("Clauses detected:", len(clauses))


print("Paragraphs loaded:", len(paragraphs))

print()
print("Searching 3GPP clauses...")

results = search_clauses(
    question,
    clauses
)

for result in results[:5]:

    print()
    print("Result")
    print("Clause:", result["number"])
    print("Title:", result["title"])
    print("Score:", result["score"])
from services.search import semantic_search_clauses
print()
print("Semantic Search Results...")

semantic_results = semantic_search_clauses(
    question,
    clauses
)

for result in semantic_results:

    print()
    print("Result")
    print("Clause:", result["number"])
    print("Title:", result["title"])
    print(
        "Similarity:",
        round(result["score"], 4)
    )
print()
print("BM25 Search Results...")

bm25_results = bm25_search_clauses(
    question,
    clauses
)

for result in bm25_results:

    print()
    print("Result")
    print("Clause:", result["number"])
    print("Title:", result["title"])
    print(
        "BM25 Score:",
        round(result["score"], 4)
    )
    print()
print("Hybrid Search Results...")

hybrid_results = hybrid_search_clauses(
    results,
    semantic_results,
    bm25_results,
    top_k=10,
)

for result in hybrid_results:

    print()
    print("Result")
    print("Clause:", result["number"])
    print("Title:", result["title"])
    print(
        "Hybrid Score:",
        round(result["score"], 6)
    )
print()
print("Reranked Search Results...")

reranked_results = rerank_clauses(
    question,
    hybrid_results,
    clauses,
)

for result in reranked_results:

    print()
    print("Result")
    print("Clause:", result["number"])
    print("Title:", result["title"])
    print(
        "Reranker Score:",
        round(result["score"], 4)
    )
