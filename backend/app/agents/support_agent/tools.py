import asyncio
from typing import Dict, Any, List
from ...services.rag_service import rag_service


def search_knowledge_tool(query: str, category: str = None, session_context: Dict[str, Any] = None) -> str:
    """Search TBC Bank knowledge base with category filtering and session awareness

    Args:
        query: Customer's question or search query
        category: Optional category filter (cards, loans, support, etc.)
        session_context: Current session context

    Returns:
        Relevant information from knowledge base
    """

    async def _search():
        # Search with category filter if provided
        results = await rag_service.search_knowledge(query, limit=3, category_filter=category)

        # Update session state with search activity
        if session_context:
            from ...services.session_memory_service import session_service

            state_updates = {
                "last_knowledge_search": {
                    "query": query,
                    "category": category,
                    "results_count": len(results),
                    "timestamp": asyncio.get_event_loop().time()
                }
            }

            session_obj = await session_service.get_session(
                app_name=session_context.get("app_name", "tbc_bank_chatbot"),
                user_id=session_context.get("customer_id"),
                session_id=session_context.get("session_id")
            )

            if session_obj:
                await session_service.update_session_state(session_obj, state_updates)

        return results

    results = asyncio.run(_search())

    if not results:
        return "❌ No relevant information found in knowledge base. Let me help you contact our customer service team."

    response = f"📚 Found {len(results)} relevant information sources:\n\n"

    for i, result in enumerate(results, 1):
        confidence = result['similarity_score']
        confidence_emoji = "🎯" if confidence > 0.8 else "✅" if confidence > 0.6 else "ℹ️"

        response += f"{confidence_emoji} **Result {i}** (Confidence: {confidence:.1%})\n"
        response += f"**Category:** {result['category'].title()}\n"
        response += f"{result['content']}\n\n"

    response += "💡 Need more specific information? Feel free to ask follow-up questions!"

    return response


def get_categories_tool() -> str:
    """Get all available knowledge categories"""

    async def _get_categories():
        return await rag_service.get_categories()

    categories = asyncio.run(_get_categories())

    if not categories:
        return "❌ No categories available."

    response = "📂 Available Information Categories:\n\n"

    category_descriptions = {
        "cards": "🏧 Credit/Debit Cards, Benefits, Features",
        "loans": "💰 Personal, Mortgage, Car, and Business Loans",
        "support": "📞 Customer Service, Contact Information",
        "card_security": "🔒 Security Services, Fraud Protection",
        "digital_services": "📱 Mobile Banking, Online Services",
        "network": "🏢 Branches, ATMs, Locations"
    }

    for category in sorted(categories):
        description = category_descriptions.get(category, f"Information about {category}")
        response += f"• **{category.title()}**: {description}\n"

    response += "\n💡 You can ask questions like:\n"
    response += "• 'Search for card benefits in cards category'\n"
    response += "• 'Tell me about loans'\n"
    response += "• 'Find security information'\n"

    return response


def general_inquiry_tool(inquiry_type: str, details: str = "", session_context: Dict[str, Any] = None) -> str:
    """Handle general banking inquiries with enhanced responses"""

    inquiries = {
        "hours": {
            "title": "🕒 TBC Bank Service Hours",
            "content": """
**Branch Hours:**
• Monday-Friday: 10:00-18:00
• Saturday: 10:00-15:00
• Sunday: Closed

**24/7 Services:**
• ATMs: Available round the clock
• Mobile Banking: Always accessible
• Customer Service: (995 32) 2272727
• Emergency Card Blocking: Call anytime

**Holiday Schedule:**
• Reduced hours on public holidays
• Check our mobile app for specific branch hours
            """
        },

        "contact": {
            "title": "📞 TBC Bank Contact Information",
            "content": """
**Customer Service Hotline:**
• Phone: (995 32) 2272727 (24/7)
• International: +995 32 2272727

**Digital Channels:**
• Mobile App: TBC Bank (iOS/Android)
• Website: www.tbcbank.ge
• Email: info@tbcbank.ge
• Live Chat: Available in mobile app 24/7

**Emergency Services:**
• Card Blocking: Available 24/7
• Fraud Reporting: Immediate response
• Lost Card Replacement: 24-48 hours
            """
        },

        "branches": {
            "title": "🏢 TBC Bank Branch Network",
            "content": """
**Total Network:** 150+ branches across Georgia

**Major Cities:**
• Tbilisi: 40+ locations
• Batumi: 8 locations  
• Kutaisi: 6 locations
• Rustavi: 4 locations
• Zugdidi: 3 locations

**Services Available:**
• Account opening and management
• Loan applications and consultations
• Foreign currency exchange
• Safe deposit boxes
• Investment services

**Branch Locator:**
Use our mobile app or visit tbcbank.ge/branches
            """
        },

        "atm": {
            "title": "🏧 TBC Bank ATM Network",
            "content": """
**Network Size:** 800+ ATMs across Georgia

**ATM Features:**
• Cash withdrawal (₾10,000 daily limit)
• Balance inquiries
• Mini statements
• Bill payments
• Mobile top-ups
• Deposit services (select ATMs)

**Languages:** Georgian, English, Russian

**Free Withdrawals:**
• TBC Card: Up to ₾10,000/month
• TBC Concept: Up to ₾15,000/month  
• TBC Concept 360: Up to ₾20,000/month

**International Access:**
• Visa/Mastercard network worldwide
• Competitive exchange rates
            """
        },

        "mobile_banking": {
            "title": "📱 TBC Mobile Banking Features",
            "content": """
**Account Management:**
• Real-time balance and transaction history
• Account statements and certificates
• Multiple account monitoring

**Payment Services:**
• Instant transfers between TBC accounts
• Interbank transfers (RTGS/ACH)
• Bill payments and utilities
• Mobile/internet top-ups
• Tax payments

**Card Services:**
• Card blocking/unblocking
• PIN change
• Transaction limits
• Spending analytics

**Additional Features:**
• Loan applications and management
• Investment portfolio tracking
• Currency exchange
• Branch/ATM locator
• 24/7 customer chat support

**Security:**
• Biometric authentication
• Two-factor authentication
• Transaction notifications
• Session timeout protection
            """
        },

        "fees": {
            "title": "💳 TBC Bank Fee Structure",
            "content": """
**Card Annual Fees:**
• TBC Card: ₾10/year
• TBC Concept: ₾25/year
• TBC Concept 360: ₾50/year

**Transaction Fees:**
• TBC to TBC transfers: Free
• Interbank transfers: ₾1.50
• International transfers: 0.5% (min ₾15)
• ATM withdrawals: Free within limits

**Additional Services:**
• SMS notifications: ₾2/month
• Card delivery: ₾5
• Statement copies: ₾2/page
• Account closure: Free after 6 months

**Fee Waivers:**
• Salary account holders: Reduced fees
• Premium customers: Many fees waived
• Students: Special discounts available
            """
        }
    }

    inquiry_type = inquiry_type.lower()

    if inquiry_type in inquiries:
        inquiry_data = inquiries[inquiry_type]

        # Update session context if provided
        if session_context:
            asyncio.run(_update_inquiry_context(session_context, inquiry_type))

        response = f"{inquiry_data['title']}\n"
        response += inquiry_data['content']

        if details:
            response += f"\n\n**Additional Notes:** {details}"

        response += f"\n\n💡 Need more help? Contact us at (995 32) 2272727 or use our mobile app chat!"

        return response
    else:
        # Handle unknown inquiry types
        response = f"ℹ️ **General Information Request: {inquiry_type.title()}**\n\n"

        if details:
            response += f"You asked about: {details}\n\n"

        response += "I don't have specific information about this topic in my knowledge base. "
        response += "Here's how you can get detailed assistance:\n\n"
        response += "📞 **Call Customer Service:** (995 32) 2272727 (24/7)\n"
        response += "💬 **Use Mobile App Chat:** Available 24/7\n"
        response += "🌐 **Visit Website:** www.tbcbank.ge\n"
        response += "🏢 **Visit Any Branch:** 150+ locations nationwide\n\n"
        response += "Our customer service team will be happy to provide detailed information about your inquiry."

        return response


async def _update_inquiry_context(session_context: Dict[str, Any], inquiry_type: str):
    """Update session context with inquiry information"""
    try:
        from ...services.session_memory_service import session_service

        state_updates = {
            "last_general_inquiry": {
                "type": inquiry_type,
                "timestamp": asyncio.get_event_loop().time()
            },
            "inquiry_history": session_context.get("inquiry_history", []) + [inquiry_type]
        }

        session_obj = await session_service.get_session(
            app_name=session_context.get("app_name", "tbc_bank_chatbot"),
            user_id=session_context.get("customer_id"),
            session_id=session_context.get("session_id")
        )

        if session_obj:
            await session_service.update_session_state(session_obj, state_updates)

    except Exception as e:
        print(f"❌ Error updating inquiry context: {e}")
