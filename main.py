import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import Optional, Dict, List

# Load environment variables from .env file
load_dotenv()

class GroqAPIClient:
    """
    A client class for interacting with the Groq API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Groq API client.
        
        Args:
            api_key (str, optional): Your Groq API key. If not provided, 
                                   it will be loaded from GROQ_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Groq API key is required. Set GROQ_API_KEY environment variable "
                "or pass it directly to the constructor."
            )
        
        # Initialize the Groq client
        self.client = Groq(api_key=self.api_key)
        
        # Default model and parameters
        self.default_model = "llama-3.1-8b-instant"
        self.default_max_tokens = 1024
        self.default_temperature = 0.7
    
    def send_prompt(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None
    ) -> str:
        """
        Send a prompt to the Groq API and return the response.
        
        Args:
            prompt (str): The user prompt to send to the AI
            model (str, optional): The model to use (defaults to mixtral-8x7b-32768)
            max_tokens (int, optional): Maximum number of tokens in response
            temperature (float, optional): Controls randomness (0.0 to 1.0)
            system_message (str, optional): System message to set AI behavior
            
        Returns:
            str: The AI's response text
            
        Raises:
            Exception: If the API request fails
        """
        try:
            # Use provided parameters or fall back to defaults
            model = model or self.default_model
            max_tokens = max_tokens or self.default_max_tokens
            temperature = temperature or self.default_temperature
            
            # Prepare messages
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make the API request
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract and return the response
            return completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to get response from Groq API: {str(e)}")
    
    def send_conversation(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Send a conversation (multiple messages) to the Groq API.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            model (str, optional): The model to use
            max_tokens (int, optional): Maximum number of tokens in response
            temperature (float, optional): Controls randomness (0.0 to 1.0)
            
        Returns:
            str: The AI's response text
            
        Raises:
            Exception: If the API request fails
        """
        try:
            # Use provided parameters or fall back to defaults
            model = model or self.default_model
            max_tokens = max_tokens or self.default_max_tokens
            temperature = temperature or self.default_temperature
            
            # Make the API request
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract and return the response
            return completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to get response from Groq API: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from Groq.
        
        Returns:
            List[str]: List of available model names
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            # Return commonly available models as fallback
            return [
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile", 
                "gemma2-9b-it",
                "deepseek-r1-distill-llama-70b"
            ]


def build_prompt(key_points: List[str], tone: str, context: Optional[str] = None) -> str:
    """
    Build a formatted prompt for AI assistant to draft a professional email reply.
    
    Args:
        key_points (List[str]): List of key points to include in the email
        tone (str): The desired tone for the email (e.g., "formal", "friendly", "apologetic")
        context (str, optional): Additional context about the situation or recipient
        
    Returns:
        str: A formatted prompt string for the AI assistant
        
    Example:
        >>> key_points = ["Meeting scheduled for Friday", "Please bring quarterly reports"]
        >>> tone = "professional"
        >>> context = "Follow-up to client meeting request"
        >>> prompt = build_prompt(key_points, tone, context)
    """
    # Format key points into a numbered list
    formatted_points = "\n".join([f"{i+1}. {point}" for i, point in enumerate(key_points)])
    
    # Build the base prompt
    prompt = f"""Please draft a professional email reply with the following specifications:

TONE: {tone.capitalize()}

KEY POINTS TO INCLUDE:
{formatted_points}"""
    
    # Add context if provided
    if context:
        prompt += f"""

CONTEXT:
{context}"""
    
    # Add formatting instructions
    prompt += """

REQUIREMENTS:
- Use a professional email format with appropriate greeting and closing
- Ensure all key points are naturally incorporated into the message
- Maintain the specified tone throughout
- Keep the email concise but comprehensive
- Use proper business email etiquette
- Do not include placeholder text like [Your Name] - provide a complete email body only

Please provide only the email content (subject line and body) without any additional commentary."""
    
    return prompt


def generate_reply(prompt: str) -> str:
    """
    Generate a reply using the Groq API with specific model and temperature settings.
    
    Args:
        prompt (str): The prompt string to send to the AI
        
    Returns:
        str: The AI's reply/response
        
    Raises:
        Exception: If the API request fails or configuration is invalid
        
    Example:
        >>> prompt = "Write a brief introduction about artificial intelligence"
        >>> reply = generate_reply(prompt)
        >>> print(reply)
    """
    try:
        # Initialize the Groq client
        client = GroqAPIClient()
        
        # Use the send_prompt method with specified parameters
        response = client.send_prompt(
            prompt=prompt,
            model="llama-3.1-8b-instant",
            temperature=0.7
        )
        
        return response
        
    except Exception as e:
        raise Exception(f"Failed to generate reply: {str(e)}")


def evaluate_reply(reply: str, key_points: List[str]) -> tuple[bool, bool]:
    """
    Evaluate if an AI reply contains all key points and has a polite tone.
    
    Args:
        reply (str): The AI's generated reply to evaluate
        key_points (List[str]): List of key points that should appear in the reply
        
    Returns:
        tuple[bool, bool]: (all_points_present, is_polite_tone)
            - all_points_present: True if all key points are found in the reply
            - is_polite_tone: True if the reply has polite/professional tone
            
    Example:
        >>> reply = "Thank you for your time. The meeting is confirmed for 3 PM."
        >>> key_points = ["thank", "meeting", "3 PM"]
        >>> points_check, tone_check = evaluate_reply(reply, key_points)
        >>> print(f"All points: {points_check}, Polite: {tone_check}")
    """
    # Convert reply to lowercase for case-insensitive checking
    reply_lower = reply.lower()
    
    # Check if all key points are present
    all_points_present = True
    missing_points = []
    
    for point in key_points:
        # Check if key point (or variations) appear in the reply
        point_lower = point.lower()
        
        # Check for exact match or common variations
        point_found = False
        
        # Direct substring check
        if point_lower in reply_lower:
            point_found = True
        else:
            # Check for common variations and related terms
            if "thank" in point_lower:
                if any(word in reply_lower for word in ["thank", "appreciate", "grateful"]):
                    point_found = True
            elif "meeting" in point_lower:
                if any(word in reply_lower for word in ["meeting", "appointment", "session", "conference"]):
                    point_found = True
            elif "confirm" in point_lower:
                if any(word in reply_lower for word in ["confirm", "acknowledge", "verified", "scheduled"]):
                    point_found = True
            elif "report" in point_lower:
                if any(word in reply_lower for word in ["report", "document", "file", "attachment"]):
                    point_found = True
            elif "attach" in point_lower:
                if any(word in reply_lower for word in ["attach", "include", "enclosed", "accompanying"]):
                    point_found = True
        
        if not point_found:
            all_points_present = False
            missing_points.append(point)
    
    # Check for polite tone indicators
    polite_indicators = [
        # Polite expressions
        "please", "thank you", "thanks", "appreciate", "grateful",
        "kindly", "would you", "could you", "may i", "if you don't mind",
        
        # Professional closings
        "best regards", "sincerely", "kind regards", "yours truly",
        "looking forward", "hope to hear", "please let me know",
        
        # Courteous phrases
        "i hope", "i trust", "i believe", "if possible", "at your convenience",
        "sorry for", "apologize", "excuse me", "pardon",
        
        # Professional language
        "dear", "respected", "esteemed", "honored", "pleased to",
        "happy to", "glad to", "delighted to"
    ]
    
    # Check for impolite indicators that would make it not polite
    impolite_indicators = [
        "must", "need to", "have to", "should", "demand", "require",
        "immediately", "asap", "urgent", "now", "right away",
        "obviously", "clearly", "of course", "duh", "stupid",
        "wrong", "error", "mistake", "fail", "bad", "terrible"
    ]
    
    # Count polite vs impolite indicators
    polite_count = sum(1 for indicator in polite_indicators if indicator in reply_lower)
    impolite_count = sum(1 for indicator in impolite_indicators if indicator in reply_lower)
    
    # Determine if tone is polite
    # Consider it polite if there are polite indicators and few/no impolite ones
    is_polite_tone = polite_count > 0 and impolite_count <= polite_count
    
    # Additional check: if it's very short and has no clear tone indicators,
    # check for basic professional structure
    if polite_count == 0 and impolite_count == 0:
        # Check for basic professional email structure
        has_greeting = any(word in reply_lower for word in ["dear", "hello", "hi", "greetings"])
        has_closing = any(word in reply_lower for word in ["regards", "sincerely", "thank", "best"])
        
        # If it has professional structure, consider it polite
        if has_greeting or has_closing:
            is_polite_tone = True
    
    return all_points_present, is_polite_tone


def main():
    """
    Example usage of the GroqAPIClient and utility functions
    """
    try:
        # Initialize the client
        groq_client = GroqAPIClient()
        
        print("🤖 Groq API Integration Ready!")
        print("Available models:", groq_client.get_available_models())
        print("-" * 50)
        
        # Example 1: Simple prompt
        print("Example 1: Simple prompt")
        response = groq_client.send_prompt(
            prompt="What is artificial intelligence?",
            temperature=0.5
        )
        print("Response:", response)
        print("-" * 50)
        
        # Example 2: Using build_prompt for email drafting
        print("Example 2: Professional email drafting with build_prompt")
        
        # Define email parameters
        key_points = [
            "Confirm meeting scheduled for next Tuesday at 2 PM",
            "Please bring the Q3 financial reports",
            "We'll discuss the new marketing strategy",
            "Conference room B has been reserved"
        ]
        
        tone = "professional"
        context = "Follow-up to client's meeting request from this morning"
        
        # Build the prompt
        email_prompt = build_prompt(key_points, tone, context)
        
        print("Generated prompt:")
        print(email_prompt)
        print("\n" + "="*50)
        
        # Send to AI for email generation using the client
        email_response = groq_client.send_prompt(
            prompt=email_prompt,
            temperature=0.3
        )
        
        print("AI-generated email:")
        print(email_response)
        print("-" * 50)
        
        # Example 3: Using generate_reply function
        print("Example 3: Using generate_reply function")
        
        test_prompt = "Explain the benefits of using AI in office automation in 3 bullet points."
        
        print(f"Prompt: {test_prompt}")
        print("\nGenerating reply...")
        
        reply = generate_reply(test_prompt)
        
        print("Reply from generate_reply function:")
        print(reply)
        print("-" * 50)
        
        # Example 4: Test case - build_prompt + generate_reply
        print("Example 4: Test case - build_prompt + generate_reply")
        
        # Test parameters as specified
        test_key_points = ['Thank the client', 'Confirm meeting at 3 PM', 'Attach report']
        test_tone = 'formal'
        
        print(f"Key points: {test_key_points}")
        print(f"Tone: {test_tone}")
        print()
        
        # Build the prompt using build_prompt function
        test_email_prompt = build_prompt(test_key_points, test_tone)
        
        print("Built prompt:")
        print(test_email_prompt)
        print("\n" + "="*50)
        
        # Call generate_reply with the built prompt
        print("Calling generate_reply...")
        test_result = generate_reply(test_email_prompt)
        
        print("Generated email result:")
        print(test_result)
        print("\n" + "="*50)
        
        # Evaluate the generated reply
        print("Evaluating the generated reply...")
        all_points_present, is_polite = evaluate_reply(test_result, test_key_points)
        
        print(f"✅ All key points present: {all_points_present}")
        print(f"✅ Polite tone detected: {is_polite}")
        
        if all_points_present and is_polite:
            print("🎉 Email evaluation: PASSED - High quality response!")
        else:
            print("⚠️  Email evaluation: NEEDS IMPROVEMENT")
            if not all_points_present:
                print("   - Some key points may be missing or unclear")
            if not is_polite:
                print("   - Tone could be more polite/professional")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 To fix this:")
        print("1. Get your API key from: https://console.groq.com/keys")
        print("2. Create a .env file in this directory with:")
        print("   GROQ_API_KEY=your_api_key_here")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()