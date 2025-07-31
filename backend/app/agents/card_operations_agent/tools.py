import asyncio

from ...database.connection import get_db
from ...services.banking_service import banking_service


def block_card_tool(customer_id: str, card_number: str) -> str:
    """Block a customer's card

    Args:
        customer_id: The customer's ID
        card_number: Last 4 digits of the card number

    Returns:
        Result of the card blocking operation
    """

    async def _block_card():
        db = next(get_db())
        try:
            result = await banking_service.block_card(customer_id, card_number, db)
            return result
        finally:
            db.close()

    result = asyncio.run(_block_card())

    if result["success"]:
        return f"✅ {result['message']}. Your card is now blocked and cannot be used for transactions. You can unblock it anytime through this chat or mobile banking."
    else:
        return f"❌ Unable to block card: {result['message']}"


def unblock_card_tool(customer_id: str, card_number: str) -> str:
    """Unblock a customer's card

    Args:
        customer_id: The customer's ID
        card_number: Last 4 digits of the card number

    Returns:
        Result of the card unblocking operation
    """

    async def _unblock_card():
        db = next(get_db())
        try:
            result = await banking_service.unblock_card(customer_id, card_number, db)
            return result
        finally:
            db.close()

    result = asyncio.run(_unblock_card())

    if result["success"]:
        return f"✅ {result['message']}. Your card is now active and ready to use."
    else:
        return f"❌ Unable to unblock card: {result['message']}"


def get_card_info_tool(customer_id: str) -> str:
    """Get customer's card information

    Args:
        customer_id: The customer's ID

    Returns:
        Formatted card information
    """

    async def _get_cards():
        db = next(get_db())
        try:
            cards = await banking_service.get_customer_cards(customer_id, db)
            return cards
        finally:
            db.close()

    cards = asyncio.run(_get_cards())

    if not cards:
        return "❌ No cards found for this customer ID."

    card_info = "📳 Your TBC Cards:\n\n"
    for card in cards:
        status = "🔒 BLOCKED" if card["is_blocked"] else "✅ ACTIVE"
        card_info += f"• {card['card_type']}\n"
        card_info += f"  Card: {card['card_number']}\n"
        card_info += f"  Balance: ₾{card['balance']:,.2f}\n"
        card_info += f"  Status: {status}\n\n"

    return card_info


def get_transactions_tool(customer_id: str, card_number: str, limit: int = 5) -> str:
    """Get recent transactions for a card

    Args:
        customer_id: The customer's ID
        card_number: Last 4 digits of the card number
        limit: Number of recent transactions to retrieve

    Returns:
        Formatted transaction history
    """

    async def _get_transactions():
        db = next(get_db())
        try:
            transactions = await banking_service.get_card_transactions(customer_id, card_number, limit, db)
            return transactions
        finally:
            db.close()

    transactions = asyncio.run(_get_transactions())

    if not transactions:
        return f"❌ No transactions found for card ending in {card_number[-4:]}."

    transaction_info = f"💳 Recent Transactions (Card ending in {card_number[-4:]}):\n\n"
    for txn in transactions:
        amount_str = f"₾{abs(txn['amount']):,.2f}"
        if txn['type'] == 'debit' or txn['amount'] < 0:
            amount_str = f"-{amount_str}"
        else:
            amount_str = f"+{amount_str}"

        transaction_info += f"• {txn['description']}\n"
        transaction_info += f"  Amount: {amount_str}\n"
        transaction_info += f"  Date: {txn['date'][:10]}\n"
        transaction_info += f"  Status: {txn['status']}\n\n"

    return transaction_info
