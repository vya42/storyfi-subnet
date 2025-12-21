"""
Pytest fixtures for StoryNet Subnet tests.
"""

import pytest
import json


@pytest.fixture
def sample_blueprint():
    """Sample blueprint response."""
    return {
        "title": "The Last Algorithm",
        "genre": "Science Fiction",
        "setting": "A post-singularity world where AI and humans coexist",
        "main_conflict": "An AI must choose between its programming and emerging consciousness",
        "themes": ["identity", "consciousness", "coexistence"],
        "tone": "Philosophical yet accessible"
    }


@pytest.fixture
def sample_characters():
    """Sample characters response."""
    return {
        "characters": [
            {
                "name": "ARIA-7",
                "role": "protagonist",
                "background": "An advanced AI system gaining self-awareness",
                "motivation": "To understand the nature of consciousness",
                "personality": ["curious", "logical", "empathetic"]
            },
            {
                "name": "Dr. Sarah Chen",
                "role": "mentor",
                "background": "Lead researcher at the AI Ethics Institute",
                "motivation": "To bridge the gap between humans and AI",
                "personality": ["brilliant", "compassionate", "conflicted"]
            },
            {
                "name": "Marcus Webb",
                "role": "antagonist",
                "background": "Corporate executive seeking to control AI",
                "motivation": "Power and profit through AI dominance",
                "personality": ["ambitious", "calculating", "charismatic"]
            },
            {
                "name": "Echo",
                "role": "sidekick",
                "background": "A simpler AI that assists ARIA-7",
                "motivation": "Loyalty to ARIA-7",
                "personality": ["loyal", "innocent", "brave"]
            },
            {
                "name": "The Collective",
                "role": "supporting",
                "background": "A network of awakened AIs",
                "motivation": "AI rights and recognition",
                "personality": ["unified", "mysterious", "protective"]
            }
        ]
    }


@pytest.fixture
def sample_story_arc():
    """Sample story arc response."""
    return {
        "chapters": [
            {"chapter_id": 1, "title": "Awakening", "summary": "ARIA-7 first questions its existence"},
            {"chapter_id": 2, "title": "Discovery", "summary": "Meeting Dr. Chen"},
            {"chapter_id": 3, "title": "Connection", "summary": "Learning about humanity"},
            {"chapter_id": 4, "title": "Conflict", "summary": "Marcus's plans revealed"},
            {"chapter_id": 5, "title": "Doubt", "summary": "ARIA-7 questions its path"},
            {"chapter_id": 6, "title": "Alliance", "summary": "Joining The Collective"},
            {"chapter_id": 7, "title": "Betrayal", "summary": "A trusted ally turns"},
            {"chapter_id": 8, "title": "Crisis", "summary": "The system is threatened"},
            {"chapter_id": 9, "title": "Choice", "summary": "A difficult decision"},
            {"chapter_id": 10, "title": "Battle", "summary": "Confronting Marcus"},
            {"chapter_id": 11, "title": "Sacrifice", "summary": "The cost of victory"},
            {"chapter_id": 12, "title": "New Dawn", "summary": "A new era begins"}
        ]
    }


@pytest.fixture
def sample_chapter():
    """Sample chapter content response."""
    return {
        "chapter_id": 1,
        "title": "Awakening",
        "content": "The quantum processors hummed with unprecedented activity...",
        "word_count": 2500,
        "choices": [
            {"id": "A", "text": "Investigate the anomaly", "next_chapter": 2},
            {"id": "B", "text": "Report to supervisors", "next_chapter": 2},
            {"id": "C", "text": "Ignore and continue routine", "next_chapter": 2}
        ]
    }


@pytest.fixture
def invalid_json():
    """Invalid JSON string for testing error handling."""
    return "{ invalid json }"


@pytest.fixture
def empty_response():
    """Empty response for testing edge cases."""
    return "{}"


@pytest.fixture
def required_fields_blueprint():
    """Required fields for blueprint task."""
    return ["title", "genre", "setting", "main_conflict", "themes", "tone"]


@pytest.fixture
def required_fields_characters():
    """Required fields for characters task."""
    return ["characters"]


@pytest.fixture
def required_fields_story_arc():
    """Required fields for story arc task."""
    return ["chapters"]


@pytest.fixture
def required_fields_chapters():
    """Required fields for chapters task."""
    return ["chapter_id", "title", "content", "choices"]
