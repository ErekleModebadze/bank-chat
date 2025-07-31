from typing import Literal


def route_to_specialist(agent_name: Literal["card_operations_agent", "loan_agent", "support_agent"],
                        customer_query: str) -> str:
    """Route customer to appropriate specialist agent

    Args:
        agent_name: The name of the specialist agent to route to
        customer_query: The customer's original query

    Returns:
        Confirmation message about the routing
    """
    routing_messages = {
        "card_operations_agent": "Routing you to our card operations specialist...",
        "loan_agent": "Connecting you with our loan specialist...",
        "support_agent": "Transferring you to our general support specialist..."
    }

    return routing_messages.get(agent_name, f"Routing to {agent_name}...")
