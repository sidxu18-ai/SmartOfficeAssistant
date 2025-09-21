def build_prompt(key_points: list, tone: str, context: str = None) -> str:
    '''
    Build a prompt for the AI to generate a professional email.
    
    Args:
        key_points (list): List of main points to include in the email
        tone (str): Desired tone of the email (e.g., "professional", "friendly")
        context (str, optional): Additional context for the email
        
    Returns:
        str: Formatted prompt for the AI
    '''
    # Format key points as bullet points
    formatted_points = "\n".join(f"• {point}" for point in key_points)
    
    # Build the base prompt
    prompt = f"""
    Please draft a professional email with the following key points:
    
    {formatted_points}
    
    Tone: {tone}
    """
    
    # Add context if provided
    if context:
        prompt += f"""
        
    Additional Context:
    {context}
    """
    
    # Add instructions for email format
    prompt += """
    
    Please ensure the email:
    • Has a clear structure with introduction, body, and conclusion
    • Maintains a professional and courteous tone
    • Includes all key points naturally in the flow
    • Uses clear and concise language
    """
    
    return prompt.strip()