# db/queries.py

"""
Module de requêtes avancées pour la base de données Open Pandas-AI.
Fournit des fonctions d'accès aux données avec filtres et statistiques.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session

from db.models import User, UploadedFile, Question, CodeExecution, ConsultingMessage


# ============ USER QUERIES ============

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Récupère un utilisateur par son nom d'utilisateur."""
    return session.query(User).filter_by(username=username).first()


def get_user_by_session_id(session: Session, session_id: str) -> Optional[User]:
    """Récupère un utilisateur par son ID de session."""
    return session.query(User).filter_by(session_id=session_id).first()


def get_or_create_user(session: Session, session_id: str) -> User:
    """Récupère ou crée un utilisateur pour l'ID de session donné."""
    user = session.query(User).filter_by(session_id=session_id).first()
    if not user:
        user = User(session_id=session_id)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


# ============ FILE QUERIES ============

def get_uploaded_files_by_user(session: Session, user_id: int) -> List[UploadedFile]:
    """Récupère tous les fichiers uploadés par un utilisateur."""
    return session.query(UploadedFile).filter_by(user_id=user_id).all()


def get_recent_files(
    session: Session,
    user_id: int,
    limit: int = 10
) -> List[UploadedFile]:
    """
    Récupère les fichiers récents d'un utilisateur.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        limit: Nombre maximum de fichiers
        
    Returns:
        Liste des fichiers récents
    """
    return (
        session.query(UploadedFile)
        .filter_by(user_id=user_id)
        .order_by(desc(UploadedFile.uploaded_at))
        .limit(limit)
        .all()
    )


def get_file_by_name(
    session: Session,
    user_id: int,
    filename: str
) -> Optional[UploadedFile]:
    """Récupère un fichier par son nom pour un utilisateur."""
    return (
        session.query(UploadedFile)
        .filter_by(user_id=user_id, filename=filename)
        .first()
    )


# ============ QUESTION QUERIES ============

def get_questions_by_file(session: Session, file_id: int) -> List[Question]:
    """Récupère toutes les questions pour un fichier donné."""
    return session.query(Question).filter_by(file_id=file_id).all()


def get_questions_by_user(
    session: Session,
    user_id: int,
    limit: int = 100
) -> List[Question]:
    """
    Récupère les questions d'un utilisateur.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        limit: Nombre maximum de questions
        
    Returns:
        Liste des questions
    """
    return (
        session.query(Question)
        .filter_by(user_id=user_id)
        .order_by(desc(Question.created_at))
        .limit(limit)
        .all()
    )


def get_recent_questions(
    session: Session,
    user_id: int,
    limit: int = 10
) -> List[Question]:
    """
    Récupère les questions récentes d'un utilisateur.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        limit: Nombre maximum de questions
        
    Returns:
        Liste des questions récentes
    """
    return (
        session.query(Question)
        .filter_by(user_id=user_id)
        .order_by(desc(Question.created_at))
        .limit(limit)
        .all()
    )


def search_questions(
    session: Session,
    user_id: int,
    query: str,
    limit: int = 50
) -> List[Question]:
    """
    Recherche dans les questions d'un utilisateur.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        query: Texte à rechercher
        limit: Nombre maximum de résultats
        
    Returns:
        Liste des questions correspondantes
    """
    return (
        session.query(Question)
        .filter(
            and_(
                Question.user_id == user_id,
                Question.question.ilike(f"%{query}%")
            )
        )
        .order_by(desc(Question.created_at))
        .limit(limit)
        .all()
    )


def get_questions_by_period(
    session: Session,
    user_id: int,
    start_date: datetime,
    end_date: Optional[datetime] = None
) -> List[Question]:
    """
    Récupère les questions dans une période donnée.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        start_date: Date de début
        end_date: Date de fin (par défaut: maintenant)
        
    Returns:
        Liste des questions dans la période
    """
    if end_date is None:
        end_date = datetime.now()
    
    return (
        session.query(Question)
        .filter(
            and_(
                Question.user_id == user_id,
                Question.created_at >= start_date,
                Question.created_at <= end_date
            )
        )
        .order_by(desc(Question.created_at))
        .all()
    )


# ============ EXECUTION QUERIES ============

def get_execution_history(
    session: Session,
    question_id: int
) -> List[CodeExecution]:
    """
    Récupère l'historique d'exécution pour une question.
    
    Args:
        session: Session SQLAlchemy
        question_id: ID de la question
        
    Returns:
        Liste des exécutions
    """
    return (
        session.query(CodeExecution)
        .filter_by(question_id=question_id)
        .order_by(desc(CodeExecution.created_at))
        .all()
    )


def get_successful_executions(
    session: Session,
    user_id: int,
    limit: int = 50
) -> List[Tuple[Question, CodeExecution]]:
    """
    Récupère les exécutions réussies avec leurs questions.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        limit: Nombre maximum de résultats
        
    Returns:
        Liste de tuples (Question, CodeExecution)
    """
    return (
        session.query(Question, CodeExecution)
        .join(CodeExecution, Question.id == CodeExecution.question_id)
        .filter(
            and_(
                Question.user_id == user_id,
                CodeExecution.status == 'success'
            )
        )
        .order_by(desc(CodeExecution.created_at))
        .limit(limit)
        .all()
    )


def get_failed_executions(
    session: Session,
    user_id: int,
    limit: int = 50
) -> List[Tuple[Question, CodeExecution]]:
    """
    Récupère les exécutions échouées avec leurs questions.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        limit: Nombre maximum de résultats
        
    Returns:
        Liste de tuples (Question, CodeExecution)
    """
    return (
        session.query(Question, CodeExecution)
        .join(CodeExecution, Question.id == CodeExecution.question_id)
        .filter(
            and_(
                Question.user_id == user_id,
                CodeExecution.status == 'error'
            )
        )
        .order_by(desc(CodeExecution.created_at))
        .limit(limit)
        .all()
    )


# ============ CONSULTING QUERIES ============

def get_consulting_messages_by_question(
    session: Session,
    question_id: int
) -> List[ConsultingMessage]:
    """Récupère les messages de consulting pour une question."""
    return (
        session.query(ConsultingMessage)
        .filter_by(question_id=question_id)
        .order_by(ConsultingMessage.created_at)
        .all()
    )


# ============ STATISTICS QUERIES ============

def get_session_stats(session: Session, user_id: int) -> Dict[str, Any]:
    """
    Calcule les statistiques de session pour un utilisateur.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        
    Returns:
        Dict avec les statistiques
    """
    # Nombre total de questions
    total_questions = (
        session.query(func.count(Question.id))
        .filter_by(user_id=user_id)
        .scalar()
    ) or 0
    
    # Nombre de fichiers
    total_files = (
        session.query(func.count(UploadedFile.id))
        .filter_by(user_id=user_id)
        .scalar()
    ) or 0
    
    # Taux de succès
    total_executions = (
        session.query(func.count(CodeExecution.id))
        .join(Question, Question.id == CodeExecution.question_id)
        .filter(Question.user_id == user_id)
        .scalar()
    ) or 0
    
    success_executions = (
        session.query(func.count(CodeExecution.id))
        .join(Question, Question.id == CodeExecution.question_id)
        .filter(
            and_(
                Question.user_id == user_id,
                CodeExecution.status == 'success'
            )
        )
        .scalar()
    ) or 0
    
    success_rate = (success_executions / total_executions * 100) if total_executions > 0 else 0
    
    return {
        'total_questions': total_questions,
        'total_files': total_files,
        'total_executions': total_executions,
        'success_executions': success_executions,
        'success_rate': round(success_rate, 1),
        'error_count': total_executions - success_executions
    }


def get_daily_stats(
    session: Session,
    user_id: int,
    days: int = 7
) -> List[Dict[str, Any]]:
    """
    Calcule les statistiques quotidiennes.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        days: Nombre de jours
        
    Returns:
        Liste de stats par jour
    """
    start_date = datetime.now() - timedelta(days=days)
    
    results = (
        session.query(
            func.date(Question.created_at).label('date'),
            func.count(Question.id).label('count')
        )
        .filter(
            and_(
                Question.user_id == user_id,
                Question.created_at >= start_date
            )
        )
        .group_by(func.date(Question.created_at))
        .order_by(func.date(Question.created_at))
        .all()
    )
    
    return [
        {'date': str(r.date), 'count': r.count}
        for r in results
    ]


def get_popular_topics(
    session: Session,
    user_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Identifie les sujets les plus fréquents dans les questions.
    
    Args:
        session: Session SQLAlchemy
        user_id: ID de l'utilisateur
        limit: Nombre de sujets
        
    Returns:
        Liste des sujets populaires
    """
    questions = (
        session.query(Question.question)
        .filter_by(user_id=user_id)
        .all()
    )
    
    # Analyse basique des mots-clés
    keywords = {}
    stopwords = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou',
                 'qui', 'que', 'quoi', 'comment', 'combien', 'quel', 'quelle',
                 'est', 'sont', 'dans', 'pour', 'par', 'avec', 'sur', 'en'}
    
    for (question,) in questions:
        if question:
            words = question.lower().split()
            for word in words:
                if len(word) > 3 and word not in stopwords:
                    keywords[word] = keywords.get(word, 0) + 1
    
    # Trier par fréquence
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {'keyword': k, 'count': v}
        for k, v in sorted_keywords[:limit]
    ]
