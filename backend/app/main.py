import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.adk.runners import Runner
from google.genai.types import Content, Part
from pydantic import BaseModel

from .agents.card_operations_agent.agent import card_operations_agent
from .agents.coordinator_agent.agent import coordinator_agent
from .agents.loan_agent.agent import loan_agent
from .agents.support_agent.agent import support_agent
from .config import settings
from .database.connection import get_db, test_connection, get_db_health, create_tables
from .database.models import ChatMessage
from .services.rag_service import rag_service
from .services.session_memory_service import session_service

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


create_tables()

app = FastAPI(
    title="TBC Bank Multi-Agent Chatbot",
    version="1.0.0",
    description="Advanced banking chatbot with multi-agent architecture, Google ADK, and Gemini Flash",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


security = HTTPBearer()


agents = {
    "coordinator": Runner(
        agent=coordinator_agent,
        app_name="tbc_bank_chatbot",
        session_service=session_service.memory_service,
        memory_service=session_service.memory_service_instance
    ),
    "card_operations": Runner(
        agent=card_operations_agent,
        app_name="tbc_bank_chatbot",
        session_service=session_service.memory_service,
        memory_service=session_service.memory_service_instance
    ),
    "loan": Runner(
        agent=loan_agent,
        app_name="tbc_bank_chatbot",
        session_service=session_service.memory_service,
        memory_service=session_service.memory_service_instance
    ),
    "support": Runner(
        agent=support_agent,
        app_name="tbc_bank_chatbot",
        session_service=session_service.memory_service,
        memory_service=session_service.memory_service_instance
    )
}



class ChatRequest(BaseModel):
    message: str
    customer_id: str
    session_id: Optional[str] = None
    preferred_agent: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent_name: str
    session_state: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class SessionInfo(BaseModel):
    session_id: str
    customer_id: str
    created_at: datetime
    last_updated: datetime
    state: Dict[str, Any]
    messages: List[dict]
    operations_count: int


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: Dict[str, Any]
    services: Dict[str, str]



async def get_current_customer(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return "CUST001"


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
        request: ChatRequest,
        current_customer: str = Depends(get_current_customer),
        db=Depends(get_db)
):

    try:
        logger.info(f"Chat request from {request.customer_id}: {request.message[:50]}...")

        session_id = request.session_id or str(uuid.uuid4())

        existing_session = await session_service.get_session(
            app_name="tbc_bank_chatbot",
            user_id=request.customer_id,
            session_id=session_id
        )

        if not existing_session:
            initial_state = {
                "customer_id": request.customer_id,
                "conversation_start": datetime.now().isoformat(),
                "context": request.context or {},
                "preferred_language": "en",
                "banking_context": True,
                "user_preferences": {},
                "active_operations": [],
                "conversation_history": [],
                "agent_switches": 0
            }

            session_obj = await session_service.create_session(
                app_name="tbc_bank_chatbot",
                user_id=request.customer_id,
                session_id=session_id,
                initial_state=initial_state
            )
        else:
            session_obj = existing_session

        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()

        current_agent = request.preferred_agent or "coordinator"
        if current_agent not in agents:
            current_agent = "coordinator"

        user_content = Content(
            role="user",
            parts=[Part(text=request.message)]
        )

        final_response = None
        agent_name = None

        try:
            async for event in agents[current_agent].run_async(
                    user_id=request.customer_id,
                    session_id=session_id,
                    new_message=user_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                    agent_name = event.agent_name or current_agent
                    break
        except Exception as agent_error:
            logger.error(f"Agent error: {agent_error}")
            final_response = "I apologize, but I'm having trouble processing your request right now. Please try again or contact our customer service at (995 32) 2272727."
            agent_name = current_agent

        if not final_response:
            final_response = "I apologize, but I'm having trouble processing your request right now. Please try again or contact our customer service at (995 32) 2272727."
            agent_name = current_agent

        updated_session = await session_service.get_session(
            app_name="tbc_bank_chatbot",
            user_id=request.customer_id,
            session_id=session_id
        )

        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=final_response,
            agent_name=agent_name
        )
        db.add(assistant_message)
        db.commit()

        # Generate suggestions
        suggestions = _generate_suggestions(agent_name, updated_session.state if updated_session else {})

        logger.info(f"Chat response to {request.customer_id}: {len(final_response)} chars")

        return ChatResponse(
            response=final_response,
            session_id=session_id,
            agent_name=agent_name,
            session_state=updated_session.state if updated_session else {},
            suggestions=suggestions
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


def _generate_suggestions(agent_name: str, session_state: Dict[str, Any]) -> List[str]:
    """Generate contextual suggestions based on agent and session state"""

    base_suggestions = {
        "coordinator": [
            "Check my card balance",
            "Block my card",
            "What loan options do you have?",
            "Contact customer service"
        ],
        "card_operations_agent": [
            "Show my recent transactions",
            "What are the spending limits?",
            "How to enable notifications?",
            "Unblock my card"
        ],
        "loan_agent": [
            "Calculate monthly payments",
            "What documents do I need?",
            "Compare loan options",
            "Check my eligibility"
        ],
        "support_agent": [
            "Find nearest branch",
            "Mobile banking features",
            "Fee information",
            "Open new account"
        ]
    }

    suggestions = base_suggestions.get(agent_name, base_suggestions["coordinator"])

    active_operations = session_state.get("active_operations", [])

    if "card_blocked" in active_operations:
        suggestions.insert(0, "Unblock my card")

    if "recent_transfer" in active_operations:
        suggestions.insert(0, "Check transfer status")

    return suggestions[:4]


@app.get("/api/health", response_model=HealthResponse)
async def health_check():

    db_health = get_db_health()

    services_status = {}

    try:
        categories = await rag_service.get_categories()
        services_status["rag_service"] = "healthy"
    except Exception as e:
        services_status["rag_service"] = f"unhealthy: {str(e)}"

    try:
        test_session = await session_service.create_session(
            app_name="tbc_bank_chatbot",
            user_id="health_check",
            session_id="health_check_test"
        )
        await session_service.delete_session(
            app_name="tbc_bank_chatbot",
            user_id="health_check",
            session_id="health_check_test"
        )
        services_status["session_service"] = "healthy"
    except Exception as e:
        services_status["session_service"] = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="healthy" if db_health["status"] == "healthy" else "degraded",
        timestamp=datetime.now().isoformat(),
        database=db_health,
        services=services_status
    )


@app.get("/api/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(
        session_id: str,
        current_customer: str = Depends(get_current_customer),
        db=Depends(get_db)
):
    """Get detailed session information"""

    try:
        session_obj = await session_service.get_session(
            app_name="tbc_bank_chatbot",
            user_id=current_customer,
            session_id=session_id
        )

        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()

        formatted_messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "agent_name": msg.agent_name,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]

        operations_count = len([
            msg for msg in messages
            if msg.role == "assistant" and msg.agent_name != "coordinator"
        ])

        return SessionInfo(
            session_id=session_id,
            customer_id=current_customer,
            created_at=datetime.fromisoformat(session_obj.state.get("conversation_start", datetime.now().isoformat())),
            last_updated=datetime.fromtimestamp(session_obj.last_update_time),
            state=session_obj.state,
            messages=formatted_messages,
            operations_count=operations_count
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    """Initialize application with enhanced services"""
    logger.info("🚀 TBC Bank Multi-Agent Chatbot starting up...")

    # Test database connection
    if not test_connection():
        logger.error("❌ Database connection failed!")

    try:
        # Test Google embeddings
        categories = await rag_service.get_categories()
        logger.info(f"🧠 RAG service initialized with Google embeddings")
        logger.info(f"📚 Knowledge categories: {categories}")

        # Test session service
        test_session = await session_service.create_session(
            app_name="tbc_bank_chatbot",
            user_id="system_test",
            session_id="startup_test"
        )
        await session_service.delete_session(
            app_name="tbc_bank_chatbot",
            user_id="system_test",
            session_id="startup_test"
        )
        logger.info("✅ Session service initialized successfully")

        logger.info(f"📊 Available agents: {list(agents.keys())}")
        logger.info("🎯 All services initialized successfully!")
        logger.info("✅ Application ready!")

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        logger.warning("⚠️  Some services may not be fully functional")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
