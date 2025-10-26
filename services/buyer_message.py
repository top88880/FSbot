"""Service for sanitizing buyer-facing messages.

This module provides utilities to clean buyer messages from
child agent bots, ensuring that main bot environment-based
contact information does not leak into child agent communications.
"""

import re
import logging


def sanitize_buyer_tip(text: str) -> str:
    """Remove main-bot contact lines from buyer-facing text.
    
    Strips lines that contain contact markers like:
    - ☎️ 客服：
    - 📣 频道：
    - 📢 官方频道：
    - Support:
    - Channel:
    - Official Channel:
    
    Also handles common emoji and Chinese/English variants.
    After removing contact lines, collapses multiple blank lines.
    
    Args:
        text: The original message text that may contain contact info
        
    Returns:
        Sanitized text with contact lines removed and cleaned up
    """
    if not text:
        return text
    
    # Define patterns for contact lines to remove
    # This covers various formats and languages
    patterns = [
        # Chinese variants with emojis
        r'^[☎️📞]\s*客服[：:].+$',
        r'^[📣📢]\s*频道[：:].+$',
        r'^[📣📢]\s*官方频道[：:].+$',
        r'^[🔔💬]\s*补货通知群[：:].+$',
        r'^[📖📚]\s*教程[：:].+$',
        
        # English variants with emojis
        r'^[☎️📞]\s*Support[：:].+$',
        r'^[📣📢]\s*Channel[：:].+$',
        r'^[📣📢]\s*Official\s+Channel[：:].+$',
        r'^[🔔💬]\s*Restock\s+Group[：:].+$',
        r'^[📖📚]\s*Tutorial[：:].+$',
        
        # Generic bold patterns (common in templates)
        r'^<b>\s*[☎️📞]\s*客服[：:].+</b>$',
        r'^<b>\s*[📣📢]\s*频道[：:].+</b>$',
        r'^<b>\s*[📣📢]\s*官方频道[：:].+</b>$',
        r'^<b>\s*[🔔💬]\s*补货通知群[：:].+</b>$',
        r'^<b>\s*[☎️📞]\s*Support[：:].+</b>$',
        r'^<b>\s*[📣📢]\s*Channel[：:].+</b>$',
        r'^<b>\s*[📣📢]\s*Official\s+Channel[：:].+</b>$',
        
        # Without emojis (fallback patterns)
        r'^客服[：:].+$',
        r'^频道[：:].+$',
        r'^官方频道[：:].+$',
        r'^补货通知群[：:].+$',
        r'^Support[：:].+$',
        r'^Channel[：:].+$',
        r'^Official\s+Channel[：:].+$',
        r'^Restock\s+Group[：:].+$',
        
        # Separator lines that often accompany contact blocks
        r'^[➖\-─]{8,}$',
    ]
    
    # Combine all patterns into one regex with MULTILINE and IGNORECASE flags
    combined_pattern = '|'.join(f'({p})' for p in patterns)
    compiled_regex = re.compile(combined_pattern, re.MULTILINE | re.IGNORECASE)
    
    # Remove matching lines
    sanitized = compiled_regex.sub('', text)
    
    # Collapse multiple consecutive blank lines into at most 2
    # This preserves intentional spacing while cleaning up gaps left by removed lines
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
    
    # Trim leading/trailing whitespace
    sanitized = sanitized.strip()
    
    logging.debug(f"Sanitized buyer message: removed contact lines")
    
    return sanitized


def build_agent_contacts_block(agent_settings: dict, lang: str = 'zh') -> str:
    """Build a contacts block from agent settings for template substitution.
    
    This is used in buyer reminder templates as {contacts_block_agent}.
    
    Args:
        agent_settings: Agent settings dict with contact fields
        lang: Language code ('zh' or 'en')
        
    Returns:
        Formatted HTML string with agent contact information
    """
    msg_parts = []
    
    customer_service = agent_settings.get('customer_service')
    if customer_service:
        msg_parts.append(
            f"<b>{'客服' if lang == 'zh' else 'Support'}：</b>{customer_service}"
        )
    
    official_channel = agent_settings.get('official_channel')
    if official_channel:
        msg_parts.append(
            f"<b>{'官方频道' if lang == 'zh' else 'Official Channel'}：</b>{official_channel}"
        )
    
    restock_group = agent_settings.get('restock_group')
    if restock_group:
        msg_parts.append(
            f"<b>{'补货通知群' if lang == 'zh' else 'Restock Group'}：</b>{restock_group}"
        )
    
    tutorial_link = agent_settings.get('tutorial_link')
    if tutorial_link:
        msg_parts.append(
            f"<b>{'教程' if lang == 'zh' else 'Tutorial'}：</b>{tutorial_link}"
        )
    
    if not msg_parts:
        return ''
    
    return '\n'.join(msg_parts)
