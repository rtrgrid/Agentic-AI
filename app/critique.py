def critique_response(model, query, answer):

    critique_prompt = f"""
    You are an expert research critic.

    Analyze the following answer carefully.

    Original Question:
    {query}

    Generated Answer:
    {answer}

    Your task:
    1. Identify missing information
    2. Detect weak reasoning
    3. Detect incomplete evidence
    4. Suggest follow-up research questions

    If answer is already strong, say:
    COMPLETE

    Otherwise output:

    FOLLOW_UP:
    question 1
    question 2
    """

    response = model.generate_content(
        critique_prompt
    )

    return response.text