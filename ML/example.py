from interview_agent import InterviewAgent

if __name__ == "__main__":
    try:
        agent = InterviewAgent()
    except ValueError as e:
        print(f"Ошибка: {e}")
        print("\n Установите переменную окружения:")
        print("export SCIBOX_API_KEY='your-api-key-here'")
        print("export SCIBOX_BASE_URL='https://llm.t1v.scibox.tech/v1'")
        exit(1)
    
    job_title = "Python Developer"
    required_skills = ["Python", "FastAPI", "SQL", "Docker"]
    amount_of_tasks = 3
    
    print("Начало интервью...")
    print(f"Будет задано примерно {amount_of_tasks} вопросов.\n")
    first_question = agent.start_interview(
        job_title=job_title,
        required_skills=required_skills,
        amount_of_tasks=amount_of_tasks,
    )
    print(f"Интервьюер: {first_question}\n")
    
    interview_ended = False
    while not interview_ended:
        user_answer = input("Кандидат: ")
        if user_answer.lower() in ["завершить", "конец", "finish", "exit"]:
            print("\nИнтервью завершено по запросу кандидата.\n")
            break
        
        response = agent.process_answer(user_answer)
        print(f"Интервьюер: {response}\n")
        
        if agent.should_end_interview(response):
            print("\nИнтервью завершено. Переходим к обратной связи...\n")
            interview_ended = True
            break
    
    print("Генерация обратной связи...")
    feedback = agent.generate_feedback()
    print('')
    print("ИТОГОВАЯ ОБРАТНАЯ СВЯЗЬ")
    print("")
    print(feedback)
    print('')

