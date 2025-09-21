import re
from typing import List, Dict, Tuple

def evaluate_reply(reply: str, key_points: List[str]) -> Dict[str, bool]:
    """
    Evaluate an AI-generated reply by checking if key points are included
    and if the tone is polite.
    
    Args:
        reply (str): The AI-generated reply to evaluate
        key_points (List[str]): List of key points that should be in the reply
    
    Returns:
        Dict[str, bool]: Dictionary with evaluation results:
            - 'all_key_points_included': True if all key points are found
            - 'tone_is_polite': True if the tone appears polite
    """
    
    def check_key_points_included(text: str, points: List[str]) -> bool:
        """Check if all key points appear in the text (case-insensitive)"""
        text_lower = text.lower()
        
        for point in points:
            # Convert key point to lowercase and check for partial matches
            point_lower = point.lower()
            
            # Check for direct inclusion or key words from the point
            if point_lower in text_lower:
                continue
            
            # Extract key words from the point and check if they appear
            key_words = re.findall(r'\b\w+\b', point_lower)
            key_words = [word for word in key_words if len(word) > 2]  # Filter short words
            
            if key_words and any(word in text_lower for word in key_words):
                continue
            
            # If we reach here, this key point wasn't found
            return False
        
        return True
    
    def check_polite_tone(text: str) -> bool:
        """Check if the text has a polite tone based on common polite phrases"""
        text_lower = text.lower()
        
        # Polite indicators
        polite_phrases = [
            'please', 'thank you', 'thanks', 'appreciate', 'grateful',
            'kindly', 'would you', 'could you', 'may i', 'excuse me',
            'sorry', 'apologize', 'sincerely', 'regards', 'respectfully',
            'dear', 'hope', 'look forward', 'best wishes', 'warm regards',
            'thank you for', 'i appreciate', 'we appreciate', 'much appreciated'
        ]
        
        # Impolite indicators (red flags)
        impolite_phrases = [
            'must', 'need to', 'have to', 'should', 'demand', 'require',
            'immediately', 'asap', 'urgent', 'now', 'right away'
        ]
        
        # Count polite and impolite indicators
        polite_count = sum(1 for phrase in polite_phrases if phrase in text_lower)
        impolite_count = sum(1 for phrase in impolite_phrases if phrase in text_lower)
        
        # Additional checks for formal structure
        has_greeting = any(greeting in text_lower for greeting in ['dear', 'hello', 'hi', 'good'])
        has_closing = any(closing in text_lower for closing in ['regards', 'sincerely', 'best', 'thank you'])
        
        # Determine if tone is polite
        # At least 2 polite indicators OR formal structure, and not too many impolite phrases
        is_polite = (polite_count >= 2 or (has_greeting and has_closing)) and impolite_count <= polite_count
        
        return is_polite
    
    # Perform evaluations
    all_key_points_included = check_key_points_included(reply, key_points)
    tone_is_polite = check_polite_tone(reply)
    
    return {
        'all_key_points_included': all_key_points_included,
        'tone_is_polite': tone_is_polite
    }

def detailed_evaluation(reply: str, key_points: List[str]) -> Dict:
    """
    Provide a detailed evaluation with additional insights.
    
    Args:
        reply (str): The AI-generated reply to evaluate
        key_points (List[str]): List of key points that should be in the reply
    
    Returns:
        Dict: Detailed evaluation results with missing points and suggestions
    """
    basic_eval = evaluate_reply(reply, key_points)
    
    # Find missing key points
    missing_points = []
    reply_lower = reply.lower()
    
    for point in key_points:
        point_lower = point.lower()
        if point_lower not in reply_lower:
            # Check for key words
            key_words = re.findall(r'\b\w+\b', point_lower)
            key_words = [word for word in key_words if len(word) > 2]
            
            if not any(word in reply_lower for word in key_words):
                missing_points.append(point)
    
    # Generate suggestions
    suggestions = []
    if missing_points:
        suggestions.append(f"Missing key points: {', '.join(missing_points)}")
    
    if not basic_eval['tone_is_polite']:
        suggestions.append("Consider adding more polite language (please, thank you, etc.)")
    
    if len(reply.split()) < 50:
        suggestions.append("Reply might be too brief - consider adding more detail")
    
    return {
        **basic_eval,
        'missing_points': missing_points,
        'word_count': len(reply.split()),
        'suggestions': suggestions
    }