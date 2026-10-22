from __future__ import annotations

import re

import astrbot.api.message_components as Comp
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

PLUGIN_ID = "astrbot_plugin_md_strip"

_FENCE = re.compile(r"```[a-zA-Z0-9_+-]*\n?")
_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_UNDER_BOLD = re.compile(r"__(.+?)__", re.S)
_INLINE_CODE = re.compile(r"`([^`\n]+)`")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+", re.M)
_BULLET = re.compile(r"^\s{0,3}[-*+]\s+", re.M)
_QUOTE = re.compile(r"^\s{0,3}>\s?", re.M)


def strip_markdown(text: str) -> str:
    """Remove Markdown markers that QQ renders as literal characters.

    Args:
        text: Raw plain text produced by the model.

    Returns:
        Text with bold/heading/quote/code markers removed; bullets become "·".
    """
    if not text:
        return text
    text = _FENCE.sub("", text)
    text = _BOLD.sub(r"\1", text)
    text = _UNDER_BOLD.sub(r"\1", text)
    text = _INLINE_CODE.sub(r"\1", text)
    text = _HEADING.sub("", text)
    text = _BULLET.sub("· ", text)
    text = _QUOTE.sub("", text)
    return text


@register(PLUGIN_ID, "Coe", "发送前去掉 QQ 不渲染的 Markdown 符号", "1.0.0")
class MarkdownStripPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_decorating_result(priority=-100)
    async def strip_plain_text(self, event: AstrMessageEvent) -> None:
        """Rewrite every Plain component of the outgoing chain."""
        result = event.get_result()
        if result is None or not getattr(result, "chain", None):
            return
        for component in result.chain:
            if isinstance(component, Comp.Plain):
                stripped = strip_markdown(component.text)
                if stripped != component.text:
                    component.text = stripped
