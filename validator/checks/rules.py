"""Детерминированные проверки без LLM (source="rule").

ЗАГЛУШКА. Что добавить: пустые разделы и поля таблиц, «—» вместо значения,
«Да / Нет» без отметки, размытые слова (быстро, удобно, и т.п., при необходимости),
смешение единиц (тиын/тенге), незаполненные версия/дата/согласующие.
"""
from typing import List

from ..models import Document, Finding, Requirement


def check(doc: Document, reqs: List[Requirement]) -> List[Finding]:
    return []
