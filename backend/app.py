import strawberry
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()

@strawberry.type
class SentimentResult:
    label: str
    score: float

@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        """Check the health of the API."""
        return "healthy"

    @strawberry.field
    async def predict(self, text: str) -> SentimentResult:
        """Run sentiment prediction on a given text."""
        if not text.strip():
            raise ValueError("Text input cannot be empty.")
        
        res = await analyzer.predict(text)
        return SentimentResult(label=res["label"], score=res["score"])

schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema, graphql_ide="graphiql")

app = FastAPI(title="Sentiment Analysis API")
app.include_router(graphql_router, prefix="/graphql")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
