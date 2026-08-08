"""
Dependency helper for accessing KnowledgeService.
"""

from app.rag.services.knowledge_service import KnowledgeService


def get_knowledge_service_dependency() -> KnowledgeService:
    return KnowledgeService.get_instance()
