#!/usr/bin/env python3
"""Простой интерактивный скрипт для тестирования диалога с интервью-агентом."""

import requests
import json

API_URL = "http://localhost:8080"


def start_interview():
    """Начало интервью."""
    print("=== Начало интервью ===\n")
    
    job_title = input("Название вакансии: ").strip() or "Python Developer"
    skills_input = input("Навыки (через запятую): ").strip() or "Python, FastAPI, SQL"
    required_skills = [s.strip() for s in skills_input.split(",")]
    amount_of_tasks = input("Количество вопросов (по умолчанию 5): ").strip() or "5"
    
    try:
        amount_of_tasks = int(amount_of_tasks)
    except ValueError:
        amount_of_tasks = 5
    
    print(f"\nНачинаем интервью на позицию: {job_title}")
    print(f"Навыки: {', '.join(required_skills)}")
    print(f"Количество вопросов: {amount_of_tasks}\n")
    print("-" * 60)
    
    response = requests.post(
        f"{API_URL}/start/stream",
        json={
            "job_title": job_title,
            "required_skills": required_skills,
            "amount_of_tasks": amount_of_tasks
        }
    )
    
    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    session_id = data["session_id"]
    step = data["step"]
    
    print(f"\n[Интервьюер]: {step['question_text']}\n")
    
    return session_id


def continue_dialog(session_id):
    """Продолжение диалога."""
    print("-" * 60)
    
    while True:
        user_answer = input("\n[Вы]: ").strip()
        
        if not user_answer:
            print("Введите ответ или 'exit' для выхода")
            continue
        
        if user_answer.lower() in ['exit', 'quit', 'выход']:
            print("\nЗавершение интервью...")
            break
        
        response = requests.post(
            f"{API_URL}/message/stream",
            json={
                "session_id": session_id,
                "user_answer": user_answer
            }
        )
        
        if response.status_code != 200:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            break
        
        step = response.json()
        
        print(f"\n[Интервьюер]: {step['question_text']}")
        
        if step.get('score') is not None:
            print(f"[Оценка]: {step['score']}/100")
        
        if step.get('feedback'):
            print(f"[Обратная связь]: {step['feedback']}")
        
        if step['status'] == 'COMPLETED':
            print("\n" + "=" * 60)
            print("Интервью завершено!")
            if step.get('ai_feedback'):
                print(f"\n[Итоговая обратная связь]:\n{step['ai_feedback']}")
            break


def main():
    """Главная функция."""
    print("=" * 60)
    print("Тестирование Interview Agent API")
    print("=" * 60)
    
    try:
        health = requests.get(f"{API_URL}/health")
        if health.status_code != 200:
            print(f"Сервис недоступен. Убедитесь, что сервер запущен на {API_URL}")
            return
    except requests.exceptions.ConnectionError:
        print(f"Не удалось подключиться к {API_URL}")
        print("Убедитесь, что сервер запущен: python run_api.py")
        return
    
    session_id = start_interview()
    
    if session_id:
        continue_dialog(session_id)
    
    print("\n" + "=" * 60)
    print("Тестирование завершено")


if __name__ == "__main__":
    main()

