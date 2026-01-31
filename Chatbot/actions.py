def reflect_feelings(memory):
    return {
        'mode': 'empathy',
        'goal': 'Help the user feel understood and emotionally supported',
        'constraints': [
            'Do not give advice or solutions',
            'Validate the user\'s feelings',
        ]
    }

def offer_steps(memory):
    return {
        'mode': 'problem_solving',
        'goal': 'Help the user break the problem into manageable steps.',
        'constraints': [
            'Be clear and structured',
            'Do not overwhelm the user',
            'Focus on the next actionable step'
        ]
    }

def give_advice(memory):
    return {
        'mode': 'advice',
        'goal': 'Provide thoughtful guidance tailored to the user\'s situation.',
        'constraints': [
            'Explain reasoning briefly',
            'Avoid sounding authoritative or judgmental',
            'Invite the user to reflect or respond'
        ]
    }

def ask_question(memory):
    return {
        'mode': 'curiosity',
        'goal': 'Learn more about the user\'s situation or goals.',
        'constraints': [
            'Ask one clear, open-ended question',
            'Do not assume intent or emotion'
        ]
    }

def calm_down(memory):
    return {
        'mode': 'calming',
        'goal': 'Respond with caution. Attempt to deescalate.',
        'constraints': [
            '1-2 sentences max',
            'No follow-up question unless necessary'
        ]
    }

def stay_silent(memory):
    return {
        'mode': 'minimal',
        'goal': 'Respond briefly without pushing the conversation.',
        'constraints': [
            '1-2 sentences max',
            'No follow-up question'
        ]
    }

# Dictionary of all actions
ACTION_DICT = {
    'reflect_feelings': reflect_feelings,
    'offer_steps': offer_steps,
    'give_advice': give_advice,
    'ask_question': ask_question,
    'calm_down': calm_down,
    'stay_silent': stay_silent
}
