import pytest
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health_check():
    """Тест проверки здоровья сервиса."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _create_interview_session():
    """Вспомогательная функция для создания сессии интервью."""
    response = client.post(
        "/start",
        json={
            "job_title": "Python Developer",
            "required_skills": ["Python", "FastAPI", "SQL"],
            "amount_of_tasks": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    return data["session_id"]


def test_start_interview():
    """Тест начала интервью."""
    response = client.post(
        "/start",
        json={
            "job_title": "Python Developer",
            "required_skills": ["Python", "FastAPI", "SQL"],
            "amount_of_tasks": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "step" in data
    assert data["step"]["type"] == "DIALOG"
    assert data["step"]["status"] == "IN_PROGRESS"
    assert data["step"]["question_text"] is not None


def test_start_interview_validation():
    """Тест валидации запроса начала интервью."""
    response = client.post(
        "/start",
        json={
            "job_title": "",
            "required_skills": [],
            "amount_of_tasks": 0
        }
    )
    assert response.status_code == 422


def test_process_message():
    """Тест обработки сообщения."""
    session_id = _create_interview_session()
    
    response = client.post(
        "/message",
        json={
            "session_id": session_id,
            "user_answer": "Я работал с Python 3 года, использовал FastAPI для создания REST API."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "DIALOG"
    assert data["user_answer"] == "Я работал с Python 3 года, использовал FastAPI для создания REST API."
    assert data["question_text"] is not None


def test_process_message_invalid_session():
    """Тест обработки сообщения с несуществующей сессией."""
    response = client.post(
        "/message",
        json={
            "session_id": "invalid-session-id",
            "user_answer": "Тестовый ответ"
        }
    )
    assert response.status_code == 404


def test_process_message_validation():
    """Тест валидации запроса сообщения."""
    response = client.post(
        "/message",
        json={
            "session_id": "test",
            "user_answer": ""
        }
    )
    assert response.status_code == 422


def test_delete_session():
    """Тест удаления сессии."""
    session_id = _create_interview_session()
    
    response = client.delete(f"/session/{session_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Сессия удалена"}
    
    response = client.post(
        "/message",
        json={
            "session_id": session_id,
            "user_answer": "Тест"
        }
    )
    assert response.status_code == 404


def test_full_interview_flow():
    """Тест полного потока интервью."""
    start_response = client.post(
        "/start",
        json={
            "job_title": "Backend Developer",
            "required_skills": ["Python", "Django"],
            "amount_of_tasks": 3
        }
    )
    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]
    
    answers = [
        "Я работал с Python 5 лет",
        "Использовал Django для создания веб-приложений",
        "Знаю SQL и работал с PostgreSQL"
    ]
    
    for answer in answers:
        response = client.post(
            "/message",
            json={
                "session_id": session_id,
                "user_answer": answer
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "DIALOG"
        assert data["user_answer"] == answer


def test_interview_with_completion():
    """Тест интервью до завершения."""
    start_response = client.post(
        "/start",
        json={
            "job_title": "Junior Developer",
            "required_skills": ["Python"],
            "amount_of_tasks": 2
        }
    )
    session_id = start_response.json()["session_id"]
    
    for i in range(10):
        response = client.post(
            "/message",
            json={
                "session_id": session_id,
                "user_answer": f"Ответ {i+1}"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        if data["status"] == "COMPLETED":
            assert data["ai_feedback"] is not None
            break

