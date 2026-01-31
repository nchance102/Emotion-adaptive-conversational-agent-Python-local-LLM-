import requests

def ask_llm(prompt: str) -> str:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 220,
                "repeat_penalty": 1.15,
                "temperature": 0.7,
                "stop": ["\nUser:", "\nYou:"]
            }
        },
        timeout=60
    )
    r.raise_for_status()
    return r.json()["response"].strip()
