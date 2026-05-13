from vertexai.generative_models import GenerativeModel

def critique_response(query, answer):
    """Verified stable critique using raw Vertex AI."""
    critique_prompt = f"""
    You are an expert research critic.
    Analyze the following research answer carefully.
    
    Question: {query}
    Answer: {answer}
    
    If the answer is comprehensive, output: COMPLETE
    Otherwise, suggest 2 follow-up questions starting with: FOLLOW_UP:
    """
    
    # Using the verified working model path
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(critique_prompt)
    return response.text
