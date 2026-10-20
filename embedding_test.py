from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


model = SentenceTransformer("all-MiniLM-L6-v2")


question = "How does the UE tell the gNB that it needs uplink resources?"

texts = [
    "Scheduling Request. The UE uses Scheduling Request to request uplink UL-SCH resources from the gNB when it has new data to transmit.",
    "The UE performs cell selection.",
    "The UE reports positioning measurements.",
]


question_embedding = model.encode(question)

text_embeddings = model.encode(texts)


for text, embedding in zip(texts, text_embeddings):

    similarity = cos_sim(
        question_embedding,
        embedding
    )

    print()
    print("Text:", text)
    print("Similarity:", similarity.item())