import chromadb
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction

from typing import List, Dict

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding_function = GoogleGenerativeAiEmbeddingFunction(
            model_name="gemini-embedding-001",
            task_type="RETRIEVAL_DOCUMENT"
        )
        self.collection = self.client.get_or_create_collection(
            name="tbc_bank_knowledge",
            embedding_function=self.embedding_function
        )
        if self.collection.count() == 0:
            self._initialize_knowledge()

    def _initialize_knowledge(self):
        knowledge_data =  [
            {
                "id": "tbc_card_benefits",
                "content": "TBC Card offers 0.6% cashback on any payment in Georgia, doubled cashback (1.2%) in selected categories like grocery, fuel, and pharmacy. Free cash withdrawal up to 10,000₾ monthly from any ATM in Georgia.",
                "category": "cards"
            },
            {
                "id": "tbc_concept_360",
                "content": "TBC Concept Card 360 provides 0.7% cashback on every payment, triple cashback (2.1%) in selected categories, personal banker service, and free cash withdrawal up to 20,000₾ monthly.",
                "category": "cards"
            },
            {
                "id": "card_blocking",
                "content": "You can block your TBC card instantly through mobile banking, by calling customer service, or through our chatbot. Blocking is immediate and helps protect against unauthorized transactions.",
                "category": "card_security"
            },
            {
                "id": "loan_types",
                "content": "TBC Bank offers personal loans, mortgage loans, car loans, and business loans. Interest rates vary based on loan type, amount, and customer profile. Loan limits are calculated based on income and existing obligations.",
                "category": "loans"
            },
            {
                "id": "customer_support",
                "content": "TBC Bank customer support is available 24/7 through phone at (995 32) 2272727, mobile app chat, or online banking. You can also visit any TBC branch during business hours.",
                "category": "support"
            },
            {
                "id": "card_security_service",
                "content": "Card Security Service protects against illegal/fraudulent transactions. TBC Card includes 5₾ annual fee, TBC Concept Card includes 10₾ fee, and TBC Concept 360 includes it free. Coverage includes up to 3000₾ for unauthorized transactions.",
                "category": "card_security"
            }
        ]
        self.collection.add(
            ids=[item['id'] for item in knowledge_data],
            documents=[item['content'] for item in knowledge_data],
            metadatas=[{"category": item["category"]} for item in knowledge_data]
        )

    async def search_knowledge(self, query: str, limit: int = 3) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
        )
        return [
            {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "category": results["metadatas"][0][i]
            }
            for i in range(len(results['documents'][0]))
        ]

rag_service = RAGService()
