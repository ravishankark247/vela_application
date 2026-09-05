"""Vela AI Tutor helpers with an offline student-friendly fallback."""

import os
from typing import Any


def _offline_answer(task: str, subject: str, material: str, difficulty: str, count: int) -> str:
    topic = subject.strip() or "your topic"
    source = material.strip() or f"the key ideas in {topic}"
    if task == "Make a quiz":
        questions = []
        for number in range(1, count + 1):
            questions.append(
                f"{number}. What is one important idea from {topic}?\n"
                f"A. A definition or core principle\nB. An unrelated detail\nC. A random example\nD. None of these\n"
                f"Answer: A\nExplanation: Review the core principle in {source}."
            )
        return f"{difficulty} quiz on {topic}\n\n" + "\n\n".join(questions)
    if task == "Explain an answer":
        return f"Answer explanation for {topic}\n\nStart with the main idea: {source}. Break it into a definition, one example, and one reason it matters. Then explain it back in your own words and check which step feels unclear."
    if task == "Make flashcards":
        return "\n\n".join(f"Card {number}\nFront: Key idea from {topic}\nBack: Define it, give an example, and connect it to {source}." for number in range(1, count + 1))
    if task == "Summarize notes":
        return f"Study summary: {topic}\n\n- Main idea: {source}\n- Important terms: identify the 3 to 5 words that repeat most often.\n- Remember: connect each term to one example.\n- Self-check: explain the topic without looking at your notes."
    if task == "Make a study plan":
        return f"Study plan for {topic}\n\n1. 10 min: skim and list what you already know.\n2. 20 min: learn the core concepts from {source}.\n3. 15 min: create flashcards and answer them without notes.\n4. 10 min: take a short quiz.\n5. 5 min: write one question to revisit tomorrow."
    return f"Vela Tutor on {topic}\n\nI can help you learn this step by step. Start with this prompt: {source}\n\nTry: define the idea, work through one example, explain why the answer works, and then create a similar problem for yourself."


def _openai_answer(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are Vela Tutor, a patient study coach. Be accurate, concise, age-appropriate, and show reasoning without doing dishonest academic work for the student."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return None


def tutor_answer(task: str, subject: str, material: str, difficulty: str = "Medium", count: int = 5) -> dict[str, Any]:
    prompt = (
        f"Task: {task}\nSubject: {subject}\nDifficulty: {difficulty}\n"
        f"Number of items: {count}\nStudent material or question:\n{material}\n\n"
        "Give a useful student-facing result. For quizzes include answers and short explanations. "
        "For explanations use steps and a small example. Do not invent citations."
    )
    online = _openai_answer(prompt)
    if online:
        return {"text": online, "provider": "OpenAI-compatible provider"}
    return {"text": _offline_answer(task, subject, material, difficulty, count), "provider": "Offline Vela Tutor"}
