"""Main FastAPI application for HealthGuide"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.config import settings
from app.models import (
    ConversationRequest, ConversationResponse, TriageResult, TriageLevel,
    ProviderRequest, Provider, SummaryResponse, Message
)
from app.database import get_db, init_db, save_conversation, get_conversation
from app.llm_service import get_llm_service
from app.red_flags import check_red_flags, get_red_flag_response
from app.providers import get_providers

# Initialize FastAPI app
app = FastAPI(
    title="HealthGuide - Fever Helpline API",
    description="AI-powered fever triage and guidance system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# Health check endpoint
@app.get("/")
async def root():
    return {"message": "HealthGuide API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HealthGuide API"}


# Triage endpoint
@app.post("/api/triage", response_model=ConversationResponse)
async def triage(
    request: ConversationRequest,
    db: Session = Depends(get_db)
):
    """
    Main triage endpoint that processes user messages and provides guidance.
    """
    try:
        # Initialize LLM service
        llm_service = get_llm_service()
        
        # Check for red flags FIRST (before any other processing)
        red_flag = check_red_flags(request.message)
        if red_flag:
            # Save conversation with red flag
            messages = request.conversation_history + [
                {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": get_red_flag_response(red_flag), "timestamp": datetime.now().isoformat()}
            ]
            save_conversation(
                db=db,
                session_id=request.session_id,
                messages=messages,
                triage_level=TriageLevel.EMERGENCY.value,
                red_flag=red_flag
            )
            
            return ConversationResponse(
                session_id=request.session_id,
                message=get_red_flag_response(red_flag),
                triage_result=TriageResult(
                    triage_level=TriageLevel.EMERGENCY,
                    escalate=True,
                    summary=f"Red flag symptom detected: {red_flag}",
                    recommended_next_steps=[
                        "Call emergency services immediately",
                        "Go to the nearest emergency room",
                        "Do not delay seeking medical attention"
                    ],
                    red_flag_detected=True,
                    red_flag_symptom=red_flag
                ),
                conversation_complete=True
            )
        
        # Convert conversation history to Message objects
        messages = [
            Message(role=msg.get("role", "user"), content=msg.get("content", ""))
            for msg in request.conversation_history
        ]
        messages.append(Message(role="user", content=request.message))
        
        # Assess triage level
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        triage_result = llm_service.assess_triage(conversation_history, request.message)
        
        # Generate response
        if triage_result.red_flag_detected:
            response_message = get_red_flag_response(triage_result.red_flag_symptom or "red flag symptom")
            conversation_complete = True
        else:
            # Generate LLM response
            response_message = llm_service.generate_response(messages, conversation_history)
            if triage_result.next_question:
                response_message += f"\n\n{triage_result.next_question}"
            conversation_complete = triage_result.next_question is None
        
        # Save conversation to database
        updated_messages = request.conversation_history + [
            {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": response_message, "timestamp": datetime.now().isoformat()}
        ]
        save_conversation(
            db=db,
            session_id=request.session_id,
            messages=updated_messages,
            triage_level=triage_result.triage_level.value,
            summary=triage_result.summary,
            red_flag=triage_result.red_flag_symptom
        )
        
        return ConversationResponse(
            session_id=request.session_id,
            message=response_message,
            triage_result=triage_result,
            conversation_complete=conversation_complete
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing triage request: {str(e)}")


# Summary endpoint
@app.get("/api/summary/{session_id}", response_model=SummaryResponse)
async def get_summary(session_id: str, db: Session = Depends(get_db)):
    """Get conversation summary for a session"""
    conversation = get_conversation(db, session_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get triage result from conversation
    triage_level = TriageLevel(conversation.triage_level) if conversation.triage_level else TriageLevel.FOLLOW_UP
    
    # Extract recommended steps from messages (simplified)
    recommended_steps = [
        "Monitor your symptoms",
        "Stay hydrated",
        "Get plenty of rest",
        "Consult a healthcare provider if symptoms persist"
    ]
    
    return SummaryResponse(
        session_id=session_id,
        summary=conversation.summary or "Fever-related symptoms discussed",
        triage_level=triage_level,
        recommended_next_steps=recommended_steps,
        conversation_count=len(conversation.messages) if conversation.messages else 0
    )


# Providers endpoint
@app.post("/api/providers", response_model=List[Provider])
async def get_healthcare_providers(request: ProviderRequest):
    """Get nearby healthcare providers"""
    try:
        providers = get_providers(request)
        return providers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")


# Create new session endpoint
@app.post("/api/session")
async def create_session():
    """Create a new conversation session"""
    session_id = str(uuid.uuid4())
    return {"session_id": session_id, "message": "New session created"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

