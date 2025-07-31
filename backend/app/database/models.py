from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cards = relationship("Card", back_populates="customer")
    loans = relationship("Loan", back_populates="customer")
    transactions = relationship("Transaction", back_populates="customer")


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String, unique=True, index=True)
    card_type = Column(String)  # TBC Card, TBC Concept, TBC Concept 360
    balance = Column(Float, default=0.0)
    credit_limit = Column(Float, default=0.0)
    is_blocked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="cards")
    transactions = relationship("Transaction", back_populates="card")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(String, unique=True, index=True)
    loan_type = Column(String)
    amount = Column(Float)
    outstanding_balance = Column(Float)
    interest_rate = Column(Float)
    monthly_payment = Column(Float)
    status = Column(String, default="active")  # active, paid, defaulted
    customer_id = Column(Integer, ForeignKey("customers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="loans")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    transaction_type = Column(String)  # debit, credit, transfer
    description = Column(String)
    status = Column(String, default="completed")
    card_id = Column(Integer, ForeignKey("cards.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    card = relationship("Card", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"))
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    agent_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
