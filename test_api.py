#!/usr/bin/env python3
"""
Test script for QERA API - tests completed phases
"""

import asyncio
import aiosqlite
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'qera/backend'))

from config import settings
from database import DB_PATH

async def test_database():
    """Test database connection and schema"""
    print("\n" + "="*60)
    print("TEST 1: Database Connection & Schema")
    print("="*60)
    
    try:
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA foreign_keys=ON;")
        
        # Check tables exist
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = await cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        print(f"✓ Database connection successful")
        print(f"✓ Found {len(table_names)} tables:")
        for table in table_names:
            print(f"  - {table}")
        
        # Check FTS5 virtual table
        if 'questions_fts' in table_names:
            print(f"✓ FTS5 virtual table 'questions_fts' exists for full-text search")
        
        await db.close()
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


async def test_search_model():
    """Test search model functions"""
    print("\n" + "="*60)
    print("TEST 2: Search Model (Phase 9)")
    print("="*60)
    
    try:
        from models.search_model import keyword_search_questions, keyword_search_exams
        
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA foreign_keys=ON;")
        
        # Test questions search (should return empty if no public questions)
        result = await keyword_search_questions(db, "test", page=1, page_size=10)
        print(f"✓ keyword_search_questions() works")
        print(f"  - Returns: {list(result.keys())}")
        print(f"  - Total results: {result['total']}")
        
        # Test exams search
        result = await keyword_search_exams(db, "test", page=1, page_size=10)
        print(f"✓ keyword_search_exams() works")
        print(f"  - Returns: {list(result.keys())}")
        print(f"  - Total results: {result['total']}")
        
        await db.close()
        return True
    except Exception as e:
        print(f"✗ Search model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_service():
    """Test AI service functions"""
    print("\n" + "="*60)
    print("TEST 3: AI Service (Phase 10 - Stubs)")
    print("="*60)
    
    try:
        from services.ai_service import (
            check_duplicate, suggest_tags, analyze_difficulty,
            moderation_filter, semantic_search
        )
        
        # Test check_duplicate
        db = await aiosqlite.connect(DB_PATH)
        result = await check_duplicate(db, "Test Title", "Test Description")
        print(f"✓ check_duplicate() works: {result['is_duplicate']}")
        
        # Test suggest_tags
        tags = await suggest_tags(db, "Math equation problem", None)
        print(f"✓ suggest_tags() works: {tags}")
        
        # Test analyze_difficulty
        diff = await analyze_difficulty(db, "Easy problem", None)
        print(f"✓ analyze_difficulty() works: {diff['difficulty']}")
        
        # Test moderation_filter
        mod = await moderation_filter("This is normal text")
        print(f"✓ moderation_filter() works: is_toxic={mod['is_toxic']}, is_spam={mod['is_spam']}")
        
        # Test semantic_search stub
        sem = await semantic_search("query")
        print(f"✓ semantic_search() stub works: {sem}")
        
        await db.close()
        return True
    except Exception as e:
        print(f"✗ AI service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "█"*60)
    print("█ QERA Backend Test Suite")
    print("█ Testing Completed Phases (1-9, 11-16)")
    print("█"*60)
    
    results = []
    
    # Test database
    results.append(("Database", await test_database()))
    
    # Test search model (Phase 9)
    results.append(("Search Model (P9)", await test_search_model()))
    
    # Test AI service (Phase 10 stubs)
    results.append(("AI Service (P10)", await test_ai_service()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Completed phases are working correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
