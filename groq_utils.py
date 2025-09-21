import os
import groq

def generate_reply(prompt: str) -> str:
    """
    Generate a response using Groq's API with the llama3-8b-8192 model.
    
    Args:
        prompt (str): The input prompt to send to the model
        
    Returns:
        str: The generated response from the model
        
    Raises:
        Exception: If there's an error communicating with the Groq API
    """
    # Initialize the Groq client using API key from environment variable
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    try:
        # Call the Groq API with specified parameters
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Extract and return the response text
        return completion.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Error generating response from Groq: {str(e)}")