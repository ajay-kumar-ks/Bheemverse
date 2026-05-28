"""
Search model for FTS5 full-text search on questions and exams.
Provides keyword search with filters and semantic fallback capability.
"""

try:
    from backend.models.question_model import _row_to_question
except ImportError:
    from models.question_model import _row_to_question


async def keyword_search_questions(
    db,
    query: str,
    tags: list[str] | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
    page: int = 1,
    page_size: int = 10,
):
    """
    Search questions using FTS5 full-text search with optional filters.
    
    Args:
        db: Database connection
        query: Search query string
        tags: Optional list of tag names to filter by
        difficulty: Optional difficulty level (easy, medium, hard)
        question_type: Optional question type (mcq, true_false, short_answer, descriptive)
        page: Page number (1-indexed)
        page_size: Results per page
    
    Returns:
        {
            "results": [question_objects],
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total_count / page_size)
        }
    """
    offset = (page - 1) * page_size
    
    # FTS5 search query
    fts_query = query.replace('"', '""')  # Escape quotes for FTS5
    
    # Build the base search query
    where_clauses = ["questions_fts.rowid IN (SELECT rowid FROM questions_fts WHERE questions_fts MATCH ?)"]
    where_clauses.append("questions.is_public = 1")
    where_clauses.append("questions.is_flagged = 0")
    params = [fts_query]
    
    # Add filter clauses
    if difficulty:
        where_clauses.append("questions.difficulty = ?")
        params.append(difficulty)
    
    if question_type:
        where_clauses.append("questions.type = ?")
        params.append(question_type)
    
    where_sql = " AND ".join(where_clauses)
    
    # Build tag filter if provided
    tag_join = ""
    if tags and len(tags) > 0:
        placeholders = ",".join("?" * len(tags))
        tag_join = f"""
        INNER JOIN question_tags ON questions.id = question_tags.question_id
        INNER JOIN tags ON question_tags.tag_id = tags.id
        """
        where_sql += f" AND tags.name IN ({placeholders})"
        params.extend(tags)
    
    # Count total results
    count_sql = f"""
    SELECT COUNT(DISTINCT questions.id)
    FROM questions
    INNER JOIN questions_fts ON questions.id = questions_fts.rowid
    {tag_join}
    WHERE {where_sql}
    """
    cursor = await db.execute(count_sql, params)
    total_result = await cursor.fetchone()
    total = total_result[0] if total_result else 0
    
    # Fetch paginated results
    search_sql = f"""
    SELECT DISTINCT questions.id, questions.user_id, questions.title, questions.description,
           questions.type, questions.correct_answer, questions.difficulty, questions.explanation,
           questions.is_public, questions.is_flagged, questions.likes_count, questions.created_at, questions.updated_at
    FROM questions
    INNER JOIN questions_fts ON questions.id = questions_fts.rowid
    {tag_join}
    WHERE {where_sql}
    ORDER BY questions.created_at DESC
    LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])
    
    cursor = await db.execute(search_sql, params)
    rows = await cursor.fetchall()
    
    results = [_row_to_question(row) for row in rows]
    
    total_pages = (total + page_size - 1) // page_size  # Ceiling division
    
    return {
        "results": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


async def keyword_search_exams(
    db,
    query: str,
    page: int = 1,
    page_size: int = 10,
):
    """
    Search exams using FTS5 full-text search on title and description.
    
    Args:
        db: Database connection
        query: Search query string
        page: Page number (1-indexed)
        page_size: Results per page
    
    Returns:
        {
            "results": [exam_objects],
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total_count / page_size)
        }
    """
    offset = (page - 1) * page_size
    
    # Simple search on exams (no FTS5 yet)
    where_clauses = ["exams.is_public = 1"]
    params = [f"%{query}%", f"%{query}%"]
    
    search_text = f"(exams.title LIKE ? OR exams.description LIKE ?)"
    
    # Count total results
    count_sql = f"""
    SELECT COUNT(*)
    FROM exams
    WHERE {search_text} AND {' AND '.join(where_clauses)}
    """
    cursor = await db.execute(count_sql, params)
    total_result = await cursor.fetchone()
    total = total_result[0] if total_result else 0
    
    # Fetch paginated results
    search_sql = f"""
    SELECT id, user_id, title, description, duration_minutes, total_marks, is_public, randomize_order, created_at, updated_at
    FROM exams
    WHERE {search_text} AND {' AND '.join(where_clauses)}
    ORDER BY exams.created_at DESC
    LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])
    
    cursor = await db.execute(search_sql, params)
    rows = await cursor.fetchall()
    
    results = [
        {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "description": row[3],
            "duration_minutes": row[4],
            "total_marks": row[5],
            "is_public": row[6],
            "randomize_order": row[7],
            "created_at": row[8],
            "updated_at": row[9],
        }
        for row in rows
    ]
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "results": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
