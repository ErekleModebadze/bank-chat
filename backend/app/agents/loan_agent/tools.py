import asyncio

from ...database.connection import get_db
from ...services.banking_service import banking_service


def get_loan_limits_tool(customer_id: str) -> str:
    """Calculate loan limits for a customer

    Args:
        customer_id: The customer's ID

    Returns:
        Formatted loan limits information
    """

    async def _get_loan_limits():
        db = next(get_db())
        try:
            result = await banking_service.get_loan_limits(customer_id, db)
            return result
        finally:
            db.close()

    result = asyncio.run(_get_loan_limits())

    if not result["success"]:
        return f"❌ Unable to calculate loan limits: {result['message']}"

    limits = result["loan_limits"]
    existing_loans = result["existing_loans_total"]

    info = "💰 Your TBC Bank Loan Limits:\n\n"

    info += f"📊 Personal Loan:\n"
    info += f"  • Limit: ₾{limits['personal_loan']['limit']:,.2f}\n"
    info += f"  • Interest Rate: {limits['personal_loan']['interest_rate']}% per year\n"
    info += f"  • Max Term: {limits['personal_loan']['max_term_months']} months\n\n"

    info += f"🏠 Mortgage Loan:\n"
    info += f"  • Limit: ₾{limits['mortgage']['limit']:,.2f}\n"
    info += f"  • Interest Rate: {limits['mortgage']['interest_rate']}% per year\n"
    info += f"  • Max Term: {limits['mortgage']['max_term_months']} months\n\n"

    info += f"🚗 Car Loan:\n"
    info += f"  • Limit: ₾{limits['car_loan']['limit']:,.2f}\n"
    info += f"  • Interest Rate: {limits['car_loan']['interest_rate']}% per year\n"
    info += f"  • Max Term: {limits['car_loan']['max_term_months']} months\n\n"

    if existing_loans > 0:
        info += f"⚠️ Existing Loans Total: ₾{existing_loans:,.2f}\n"
        info += "Note: Loan limits are calculated considering your existing loan obligations.\n\n"

    info += "💡 To apply for a loan, visit any TBC branch or use TBC mobile banking."

    return info


def get_loan_info_tool(loan_type: str) -> str:
    """Get detailed information about a specific loan type

    Args:
        loan_type: Type of loan (personal, mortgage, car)

    Returns:
        Detailed loan product information
    """
    loan_products = {
        "personal": {
            "name": "Personal Loan",
            "min_amount": 1000,
            "max_amount": 50000,
            "min_term": 6,
            "max_term": 60,
            "interest_rate": "12.5-18%",
            "requirements": [
                "Georgian citizenship or residence permit",
                "Age 21-65 years",
                "Regular income for at least 6 months",
                "No negative credit history"
            ],
            "features": [
                "No collateral required",
                "Fast approval process",
                "Flexible repayment terms",
                "Early repayment without penalty"
            ]
        },
        "mortgage": {
            "name": "Mortgage Loan",
            "min_amount": 10000,
            "max_amount": 500000,
            "min_term": 60,
            "max_term": 360,
            "interest_rate": "8.5-12%",
            "requirements": [
                "Georgian citizenship or residence permit",
                "Age 21-65 years",
                "Stable income confirmation",
                "Property evaluation",
                "Insurance requirement"
            ],
            "features": [
                "Up to 90% property value financing",
                "Competitive interest rates",
                "Flexible payment schedule",
                "Property insurance included"
            ]
        },
        "car": {
            "name": "Car Loan",
            "min_amount": 5000,
            "max_amount": 100000,
            "min_term": 12,
            "max_term": 84,
            "interest_rate": "10-15%",
            "requirements": [
                "Georgian citizenship or residence permit",
                "Age 21-65 years",
                "Driver's license",
                "Vehicle insurance",
                "Regular income proof"
            ],
            "features": [
                "New and used car financing",
                "Up to 85% vehicle value",
                "Comprehensive insurance options",
                "Quick approval process"
            ]
        }
    }

    loan_type = loan_type.lower()
    if loan_type not in loan_products:
        return f"❌ Unknown loan type: {loan_type}. Available types: personal, mortgage, car"

    loan = loan_products[loan_type]

    info = f"💰 {loan['name']} Details:\n\n"
    info += f"💵 Amount: ₾{loan['min_amount']:,} - ₾{loan['max_amount']:,}\n"
    info += f"⏰ Term: {loan['min_term']} - {loan['max_term']} months\n"
    info += f"📈 Interest Rate: {loan['interest_rate']} per year\n\n"

    info += "📋 Requirements:\n"
    for req in loan['requirements']:
        info += f"  • {req}\n"

    info += "\n✨ Key Features:\n"
    for feature in loan['features']:
        info += f"  • {feature}\n"

    info += "\n📞 To apply, call (995 32) 2272727 or visit any TBC branch."

    return info
