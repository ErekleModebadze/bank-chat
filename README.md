# TBC Bank Multi-Agent Chatbot (In-Memory Version)

A simple multi-agent chatbot for TBC Bank built with Google Agent Development Kit (ADK), using in-memory storage for sessions and chat history, and integrated with Google Gemini embeddings for knowledge search.

## Features

- Multi-agent system with Coordinator, Card Operations, Loan, and Support agents
- Fully in-memory session and conversation management (no database required)
- Retrieval-Augmented Generation (RAG) using Google Gemini embeddings and ChromaDB
- REST API backend with FastAPI
- React frontend with Material-UI chat interface
- Simple simulated banking tools (card blocking, loan info, etc.)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google API Key with access to Gemini embeddings