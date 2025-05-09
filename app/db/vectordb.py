from langchain_openai import OpenAIEmbeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import uuid
from app.core.config import settings, ModelType
from app.schemas.cheese_products import CheeseProducts
from typing import List

class VectorDBService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.dims = 1536
        self.spec = ServerlessSpec(cloud="aws", region="us-east-1")
        self.index = self._initialize_index()
        self.embed_model = OpenAIEmbeddings(
            model=ModelType.embedding,
            openai_api_key=settings.OPENAI_API_KEY
        )

    def _initialize_index(self):
        existing_indexes = self.pc.list_indexes()
        
        if settings.PINECONE_INDEX_NAME not in [item["name"] for item in existing_indexes]:
            self.pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=self.dims,
                metric='cosine',
                spec=self.spec
            )
        return self.pc.Index(settings.PINECONE_INDEX_NAME)

    def _generate_vector_text(self, cheese: CheeseProducts) -> str:
        fields = [
            (cheese.product_name, "Product Name"),
            (cheese.product_description, "Product Description"),
            (cheese.product_category, "Product Category"),
            (cheese.product_subcategory, "Product Subcategory"),
            (cheese.product_brand, "Product Brand"),
            (cheese.product_type, "Product Type"),
            (cheese.product_origin, "Product Origin"),
            (cheese.product_price, "Product Price"),
            (cheese.product_quantity, "Product Quantity"),
            (cheese.product_unit, "Product Unit")
        ]
        return "\n".join([f"{label}: {value}" for value, label in fields if value])

    def upsert_cheese(self, cheese: CheeseProducts):
        embedding_id = str(uuid.uuid4())
        metadata = cheese.model_dump()
        metadata['start_date'] = metadata['start_date'].strftime('%Y-%m-%d')
        metadata['expiry_date'] = metadata['expiry_date'].strftime('%Y-%m-%d')
        vector = [{
            'id': embedding_id,
            'values': self.embed_model.embed_documents(self._generate_vector_text(cheese))[0],
            'metadata': metadata,
        }]
        self.index.upsert(vectors=vector)
        return embedding_id

    def query(self, query_text: str, top_k: int = 5) -> List[CheeseProducts]:
        vector = self.embed_model.embed_documents([query_text])[0]
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace="cheese-products"
        )
        return [CheeseProducts(**match['metadata']) for match in results['matches']]

vector_db = VectorDBService()