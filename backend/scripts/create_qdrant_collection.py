# from qdrant_client import QdrantClient
# from qdrant_client.models import VectorParams, Distance

# QDRANT_URL = "https://2d545162-c8d9-46ea-b665-bad7333c085d.us-east4-0.gcp.cloud.qdrant.io"
# QDRANT_API_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.VRH5ukCLgaIU4wGzVzy8h0aCjiqfQG2-JC2cLlwAv6E'


# COLLECTION_NAME = "book_content"
# VECTOR_SIZE = 1024  # Cohere embeddings

# client = QdrantClient(
#     url=QDRANT_URL,
#     api_key=QDRANT_API_KEY,
# )

# if client.collection_exists(COLLECTION_NAME):
#     print("Collection already exists")
# else:
#     client.create_collection(
#         collection_name=COLLECTION_NAME,
#         vectors_config=VectorParams(
#             size=VECTOR_SIZE,
#             distance=Distance.COSINE,
#         ),
#     )
#     print("Collection created:", COLLECTION_NAME)
