from datetime import datetime
from typing import Dict, List, Optional

from google.adk.events import Event, EventActions
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.sessions.session import Session

from ..config import settings
from ..database.connection import get_db
from ..database.models import ChatSession


class TBCSessionService:

    def __init__(self):
        self.memory_service = InMemorySessionService()

        if settings.DATABASE_URL:
            self.db_service = DatabaseSessionService(db_url=settings.DATABASE_URL)
        else:
            self.db_service = None

        self.memory_service_instance = InMemoryMemoryService()

    async def create_session(self, app_name: str, user_id: str, session_id: str = None,
                             initial_state: Dict = None) -> Session:

        if initial_state is None:
            initial_state = {
                "customer_id": user_id,
                "conversation_start": datetime.now().isoformat(),
                "context": {
                    "preferred_language": "en",
                    "banking_context": True,
                    "session_type": "customer_service"
                },
                "user_preferences": {},
                "active_operations": []
            }

        session = await self.memory_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state
        )

        db = next(get_db())
        try:
            chat_session = ChatSession(
                session_id=session.id,
                customer_id=user_id
            )
            db.add(chat_session)
            db.commit()

            print(f"✅ Created session {session.id} for user {user_id}")

        except Exception as e:
            print(f"❌ Error saving session to database: {e}")
            db.rollback()
        finally:
            db.close()

        return session

    async def get_session(self, app_name: str, user_id: str, session_id: str) -> Optional[Session]:
        try:
            return await self.memory_service.get_session(app_name, user_id, session_id)
        except Exception as e:
            print(f"❌ Error getting session {session_id}: {e}")
            return None

    async def update_session_state(self, session: Session, state_updates: Dict):
        """Update session state with new information[141]"""
        try:
            # Create event with state delta[141]
            actions_with_update = EventActions(state_delta=state_updates)

            system_event = Event(
                invocation_id=f"state_update_{datetime.now().timestamp()}",
                author="system",
                actions=actions_with_update,
                timestamp=datetime.now().timestamp()
            )

            # Append the event to update state
            await self.memory_service.append_event(session, system_event)

            print(f"✅ Updated session state: {list(state_updates.keys())}")

        except Exception as e:
            print(f"❌ Error updating session state: {e}")

    async def list_sessions(self, app_name: str, user_id: str) -> List[str]:
        try:
            response = await self.memory_service.list_sessions(app_name, user_id)
            return response.session_ids
        except Exception as e:
            print(f"❌ Error listing sessions: {e}")
            return []

    async def delete_session(self, app_name: str, user_id: str, session_id: str):
        try:
            await self.memory_service.delete_session(app_name, user_id, session_id)

            # Also delete from database
            db = next(get_db())
            try:
                chat_session = db.query(ChatSession).filter(
                    ChatSession.session_id == session_id
                ).first()
                if chat_session:
                    db.delete(chat_session)
                    db.commit()
            finally:
                db.close()

        except Exception as e:
            print(f"❌ Error deleting session: {e}")

    async def add_session_to_memory(self, session: Session):
        """Add completed session to long-term memory[82]"""
        try:
            await self.memory_service_instance.add_session_to_memory(session)
            print(f"✅ Added session {session.id} to long-term memory")
        except Exception as e:
            print(f"❌ Error adding session to memory: {e}")

    async def search_memory(self, app_name: str, user_id: str, query: str, limit: int = 5):
        """Search long-term memory for relevant information[82]"""
        try:
            return await self.memory_service_instance.search_memory(
                app_name=app_name,
                user_id=user_id,
                query=query,
                limit=limit
            )
        except Exception as e:
            print(f"❌ Error searching memory: {e}")
            return None


# Global session service instance
session_service = TBCSessionService()
