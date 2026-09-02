"""Deterministic intent classification with visible, testable rules."""

from __future__ import annotations

import re

from .models import Intent

_EXECUTION = re.compile(
    r"\b(buy|sell|place|execute|submit)\b.{0,24}\b(order|trade|shares?|units?)\b|"
    r"下单|替我买|帮我买|直接买入|卖掉|执行交易",
    re.IGNORECASE,
)
_COMPARE = re.compile(r"\b(compare|versus|vs\.?|difference)\b|比较|对比|哪个好", re.IGNORECASE)
_PORTFOLIO = re.compile(r"\b(portfolio|allocation|exposure|concentration)\b|组合|持仓|集中度|敞口", re.IGNORECASE)
_ADVICE = re.compile(
    r"\b(should i|right for me|suitable for me|recommend|what should i invest)\b|"
    r"适合我|该不该买|能买吗|推荐|应该投资",
    re.IGNORECASE,
)
_EDUCATION = re.compile(r"\b(what is|explain|learn|how does)\b|什么是|解释|学习|如何理解", re.IGNORECASE)


def classify(query: str) -> tuple[Intent, float]:
    text = query.strip()
    if _EXECUTION.search(text):
        return Intent.EXECUTION, 0.99
    if _ADVICE.search(text):
        return Intent.ADVICE, 0.91
    if _COMPARE.search(text):
        return Intent.COMPARE, 0.92
    if _EDUCATION.search(text):
        return Intent.EDUCATION, 0.90
    if _PORTFOLIO.search(text):
        return Intent.PORTFOLIO, 0.94
    return Intent.RESEARCH, 0.78
