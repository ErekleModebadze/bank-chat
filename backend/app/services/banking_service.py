import random
from typing import List, Dict, Optional

from faker import Faker
from sqlalchemy.orm import Session

from ..database.models import Customer, Transaction

fake = Faker()


class BankingService:
    def __init__(self):
        self.fake = fake

    async def get_customer_by_id(self, customer_id: str, db: Session) -> Optional[Customer]:
        """Get customer by ID"""
        return db.query(Customer).filter(Customer.customer_id == customer_id).first()

    async def get_customer_cards(self, customer_id: str, db: Session) -> List[Dict]:
        """Get all cards for a customer"""
        customer = await self.get_customer_by_id(customer_id, db)
        if not customer:
            return []

        cards = []
        for card in customer.cards:
            cards.append({
                "id": card.id,
                "card_number": f"****-****-****-{card.card_number[-4:]}",
                "card_type": card.card_type,
                "balance": card.balance,
                "credit_limit": card.credit_limit,
                "is_blocked": card.is_blocked,
                "is_active": card.is_active
            })
        return cards

    async def block_card(self, customer_id: str, card_number: str, db: Session) -> Dict:
        """Block a customer's card"""
        customer = await self.get_customer_by_id(customer_id, db)
        if not customer:
            return {"success": False, "message": "Customer not found"}

        # Find the card (match last 4 digits)
        card = None
        for c in customer.cards:
            if c.card_number.endswith(card_number[-4:]):
                card = c
                break

        if not card:
            return {"success": False, "message": "Card not found"}

        if card.is_blocked:
            return {"success": False, "message": "Card is already blocked"}

        card.is_blocked = True
        db.commit()

        return {
            "success": True,
            "message": f"Card ending in {card_number[-4:]} has been blocked successfully",
            "card_number": f"****-****-****-{card.card_number[-4:]}",
        }

    async def unblock_card(self, customer_id: str, card_number: str, db: Session) -> Dict:
        """Unblock a customer's card"""
        customer = await self.get_customer_by_id(customer_id, db)
        if not customer:
            return {"success": False, "message": "Customer not found"}

        card = None
        for c in customer.cards:
            if c.card_number.endswith(card_number[-4:]):
                card = c
                break

        if not card:
            return {"success": False, "message": "Card not found"}

        if not card.is_blocked:
            return {"success": False, "message": "Card is not blocked"}

        card.is_blocked = False
        db.commit()

        return {
            "success": True,
            "message": f"Card ending in {card_number[-4:]} has been unblocked successfully",
            "card_number": f"****-****-****-{card.card_number[-4:]}",
        }

    async def get_card_transactions(self, customer_id: str, card_number: str, limit: int = 10, db: Session = None) -> \
    List[Dict]:
        """Get recent transactions for a card"""
        customer = await self.get_customer_by_id(customer_id, db)
        if not customer:
            return []

        card = None
        for c in customer.cards:
            if c.card_number.endswith(card_number[-4:]):
                card = c
                break

        if not card:
            return []

        transactions = db.query(Transaction).filter(
            Transaction.card_id == card.id
        ).order_by(Transaction.created_at.desc()).limit(limit).all()

        return [
            {
                "id": t.transaction_id,
                "amount": t.amount,
                "type": t.transaction_type,
                "description": t.description,
                "status": t.status,
                "date": t.created_at.isoformat()
            }
            for t in transactions
        ]

    async def get_loan_limits(self, customer_id: str, db: Session) -> Dict:
        """Calculate loan limits for a customer"""
        customer = await self.get_customer_by_id(customer_id, db)
        if not customer:
            return {"success": False, "message": "Customer not found"}

        # Calculate total income (mock calculation)
        total_balance = sum(card.balance for card in customer.cards)
        existing_loans = sum(loan.outstanding_balance for loan in customer.loans if loan.status == "active")

        # Mock loan limit calculation
        personal_loan_limit = max(0, (total_balance * 10) - existing_loans)
        mortgage_limit = max(0, (total_balance * 20) - existing_loans)
        car_loan_limit = max(0, (total_balance * 5) - existing_loans)

        return {
            "success": True,
            "customer_id": customer_id,
            "loan_limits": {
                "personal_loan": {
                    "limit": round(personal_loan_limit, 2),
                    "interest_rate": 12.5,
                    "max_term_months": 60
                },
                "mortgage": {
                    "limit": round(mortgage_limit, 2),
                    "interest_rate": 8.5,
                    "max_term_months": 360
                },
                "car_loan": {
                    "limit": round(car_loan_limit, 2),
                    "interest_rate": 10.0,
                    "max_term_months": 84
                }
            },
            "existing_loans_total": round(existing_loans, 2)
        }

    async def transfer_funds(self, customer_id: str, from_card: str, to_account: str, amount: float,
                             db: Session) -> Dict:
        """Transfer funds between accounts"""
        customer = await self.get_customer_by_id(customer_id, db)
        if not customer:
            return {"success": False, "message": "Customer not found"}

        # Find source card
        source_card = None
        for c in customer.cards:
            if c.card_number.endswith(from_card[-4:]):
                source_card = c
                break

        if not source_card:
            return {"success": False, "message": "Source card not found"}

        if source_card.is_blocked:
            return {"success": False, "message": "Source card is blocked"}

        if source_card.balance < amount:
            return {"success": False, "message": "Insufficient funds"}

        # Simulate transfer (deduct from source)
        source_card.balance -= amount

        # Create transaction record
        transaction = Transaction(
            transaction_id=f"TXN{random.randint(100000, 999999)}",
            amount=-amount,
            transaction_type="transfer_out",
            description=f"Transfer to {to_account}",
            status="completed",
            card_id=source_card.id,
            customer_id=customer.id
        )

        db.add(transaction)
        db.commit()

        return {
            "success": True,
            "message": f"Successfully transferred ₾{amount} to {to_account}",
            "transaction_id": transaction.transaction_id,
            "remaining_balance": round(source_card.balance, 2)
        }


banking_service = BankingService()
