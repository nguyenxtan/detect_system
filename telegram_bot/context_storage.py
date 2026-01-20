"""User context storage for Telegram bot"""
import json
import os
from typing import Optional, Dict

# File to store user contexts
CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "user_contexts.json")


def load_contexts() -> Dict[str, Dict]:
    """Load user contexts from file"""
    if not os.path.exists(CONTEXT_FILE):
        return {}

    try:
        with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading contexts: {e}")
        return {}


def save_contexts(contexts: Dict[str, Dict]):
    """Save user contexts to file"""
    try:
        with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(contexts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving contexts: {e}")


def get_user_context(user_id: str) -> Optional[Dict]:
    """
    Get context for a user

    Returns:
        dict with customer_id, product_id, customer_name, product_name
        or None if not set
    """
    contexts = load_contexts()
    return contexts.get(user_id)


def set_user_customer(user_id: str, customer_id: int, customer_name: str):
    """
    Set customer for a user (and clear product)

    Args:
        user_id: Telegram user ID
        customer_id: Customer ID from database
        customer_name: Customer name for display
    """
    contexts = load_contexts()

    if user_id not in contexts:
        contexts[user_id] = {}

    contexts[user_id]['customer_id'] = customer_id
    contexts[user_id]['customer_name'] = customer_name
    # Clear product when customer changes
    contexts[user_id]['product_id'] = None
    contexts[user_id]['product_name'] = None

    save_contexts(contexts)


def set_user_product(user_id: str, product_id: int, product_name: str, product_code: str):
    """
    Set product for a user

    Args:
        user_id: Telegram user ID
        product_id: Product ID from database
        product_name: Product name for display
        product_code: Product code for display
    """
    contexts = load_contexts()

    if user_id not in contexts:
        raise ValueError("Please set customer first using /set_customer")

    contexts[user_id]['product_id'] = product_id
    contexts[user_id]['product_name'] = product_name
    contexts[user_id]['product_code'] = product_code

    save_contexts(contexts)


def clear_user_context(user_id: str):
    """Clear context for a user"""
    contexts = load_contexts()
    if user_id in contexts:
        del contexts[user_id]
        save_contexts(contexts)


def get_context_summary(user_id: str) -> str:
    """Get formatted summary of user's context"""
    context = get_user_context(user_id)

    if not context:
        return "❌ Chưa thiết lập context. Vui lòng dùng /set_customer để bắt đầu."

    customer_info = f"✅ Khách hàng: {context.get('customer_name', 'N/A')}"
    product_info = f"✅ Sản phẩm: {context.get('product_code', 'N/A')} - {context.get('product_name', 'N/A')}" if context.get('product_id') else "❌ Sản phẩm: Chưa thiết lập"

    return f"""
📋 **Context hiện tại:**

{customer_info}
{product_info}

Gửi ảnh để phân tích hoặc dùng /set_customer để thay đổi.
    """.strip()
