from actions import ACTION_DICT
from scipy.spatial.distance import cosine
import numpy as np
from embedding_utils import embed_text
from memory import get_relevant_memory, adjust_action_scores, add_interaction


def decide_action(user_input, memory):
    """
    Choose the action based on user intent.
    Prioritize task-solving if the input looks like a problem or request for a solution.
    """
    text = user_input.lower()

    task_keywords = [
        'solve', 'calculate', 'compute', 'evaluate', 'program', 'code', 
        'write', 'generate', 'explain', 'find', 'what is', 'how to'
    ]

    emotion_keywords = ['sad', 'upset', 'frustrated', 'angry', 'happy']

    question_keywords = ['how', 'what', 'why', 'who', 'where']

    # --- Task-oriented requests take top priority
    if any(word in text for word in task_keywords):
        return 'offer_steps'  # break it down or solve it

    # --- Emotional reflection if emotion keywords appear
    if any(word in text for word in emotion_keywords):
        return 'reflect_feelings'

    # --- Curiosity / follow-up questions
    if any(word in text for word in question_keywords):
        return 'ask_question'

    # --- Default to giving advice
    return 'give_advice'

def decide_action_with_learning(user_input, memory, ACTION_DICT):
    # --- 1. Compute base action scores ---
    base_scores = {name: 0 for name in ACTION_DICT.keys()}

    # --- 2. Use semantic memory to adjust scores ---
    input_vec = embed_text(user_input)
    base_scores = adjust_action_scores(memory, base_scores, input_vec)

    # --- 3. Pick the action with the highest score ---
    chosen_action = max(base_scores, key=base_scores.get)
    
    # --- 4. Record interaction in memory for future learning ---
    add_interaction(memory, user_input, chosen_action, input_vec)

    return chosen_action

