import streamlit as st
import groq
from evaluation_utils import evaluate_reply, detailed_evaluation
from typing import Optional, Dict, List
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class GroqAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key is required")
        self.client = groq.Groq(api_key=self.api_key)
        self.default_model = "llama-3.1-8b-instant"
        
    def send_prompt(self, prompt: str, temperature: float = 0.7) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to get response from Groq API: {str(e)}")

def build_prompt(key_points: List[str], tone: str, context: str = "", email_type: str = "custom") -> str:
    # Base key points
    key_points_text = chr(10).join('- ' + point for point in key_points)
    
    # Email type specific templates
    if email_type == "thank_you":
        prompt = f"""Write a heartfelt thank you email with the following specifics:
{key_points_text}

Tone: {tone}
Additional Context: {context}

Please write a warm and appreciative email that expresses genuine gratitude. Include specific details about what you're thanking them for and how it impacted you or your work."""
    
    elif email_type == "new_article":
        prompt = f"""Write an engaging email announcing a new article or news with these details:
{key_points_text}

Tone: {tone}
Additional Context: {context}

Please write an informative and engaging email that introduces the new content. Include a compelling subject matter, key highlights, and encourage the reader to engage with the content."""
    
    elif email_type == "report_sharing":
        prompt = f"""Write a professional email for sharing a report with these key elements:
{key_points_text}

Tone: {tone}
Additional Context: {context}

Please write a clear and organized email that introduces the report, highlights key findings or important sections, and provides context for why this report is valuable to the recipient."""
    
    elif email_type == "meeting_followup":
        prompt = f"""Write a comprehensive meeting follow-up email covering:
{key_points_text}

Tone: {tone}
Additional Context: {context}

Please write a structured follow-up email that summarizes key decisions, action items, next steps, and deadlines. Make it clear and actionable for all participants."""
    
    elif email_type == "project_update":
        prompt = f"""Write a detailed project update email including:
{key_points_text}

Tone: {tone}
Additional Context: {context}

Please write an informative project update that covers current progress, achievements, challenges, next milestones, and any support needed. Keep stakeholders well-informed."""
    
    else:  # custom
        prompt = f"""Write a professional email with the following key points:
{key_points_text}

Tone: {tone}
Additional Context: {context}

Please write a complete, well-structured email incorporating these points."""
    
    return prompt

# Initialize Groq client
groq_client = GroqAPIClient()

# Set page config
st.set_page_config(
    page_title="AI Email Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
/* Global Styles */
div.stApp {
    background: linear-gradient(135deg, #6B46C1 0%, #2C5282 100%) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    min-height: 100vh !important;
    color: white !important;
}

/* Override text colors for better contrast */
.stApp * {
    color: white !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: white !important;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Main header styling */
.main-header {
    text-align: center;
    padding: 2rem 0;
    margin-bottom: 2rem;
}

.main-header h1 {
    font-size: 3.5rem;
    font-weight: 700;
    color: white !important;
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
}

.main-header p {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.8) !important;
    margin-bottom: 0;
    font-weight: 500;
}

/* Card styling */
.main-card {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 15px;
    padding: 2rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    margin-bottom: 2rem;
}

/* Input field styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 8px !important;
    color: white !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: rgba(255, 255, 255, 0.6) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2) !important;
}

/* Placeholder text */
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: rgba(255, 255, 255, 0.6) !important;
    font-style: italic;
}

/* Button styling */
.stButton > button {
    background: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: rgba(255, 255, 255, 0.3) !important;
    transform: translateY(-1px) !important;
}

/* Labels */
label {
    color: white !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* Info box styling */
.info-box {
    background: rgba(255, 255, 255, 0.1);
    border-left: 4px solid rgba(255, 255, 255, 0.5);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    backdrop-filter: blur(5px);
}

.info-box p {
    margin: 0;
    color: white !important;
}

/* Slider styling */
.stSlider > div > div > div > div {
    background: rgba(255, 255, 255, 0.3) !important;
}

/* Success/Error messages */
.stSuccess {
    background: rgba(72, 187, 120, 0.3) !important;
    color: white !important;
    border: 1px solid rgba(72, 187, 120, 0.5) !important;
}

.stError {
    background: rgba(245, 101, 101, 0.3) !important;
    color: white !important;
    border: 1px solid rgba(245, 101, 101, 0.5) !important;
}

.stWarning {
    background: rgba(236, 201, 75, 0.3) !important;
    color: white !important;
    border: 1px solid rgba(236, 201, 75, 0.5) !important;
}

/* Generated email styling */
.generated-email {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #2d3748 !important;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    font-family: 'Inter', sans-serif;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.generated-email * {
    color: #2d3748 !important;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Email Generator</h1>
    <p>Create professional emails with AI assistance</p>
</div>
""", unsafe_allow_html=True)

# Main content area
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("✨ Generate Professional Email")
        
        # Quick template buttons (outside form)
        st.markdown("**Quick Templates:**")
        col_t1, col_t2, col_t3 = st.columns(3)
        
        template_examples = {
            "thank_you": "Thank you for your excellent work on the project\nAppreciate your dedication and effort\nLooking forward to future collaboration",
            "new_article": "New research article published on AI trends\nShare link: www.example.com/article\nKey findings on market growth\nInvite team to review and discuss",
            "report_sharing": "Monthly sales report attached\nRevenue increased by 15% this quarter\nKey metrics and analysis included\nSchedule review meeting next week"
        }
        
        with col_t1:
            if st.button("Thank You 💝", key="template_thanks"):
                st.session_state.template_text = template_examples["thank_you"]
        with col_t2:
            if st.button("New Article 📄", key="template_article"):
                st.session_state.template_text = template_examples["new_article"]
        with col_t3:
            if st.button("Report 📊", key="template_report"):
                st.session_state.template_text = template_examples["report_sharing"]
        
        # Email form
        with st.form("email_form"):
            
            # Key points
            default_text = st.session_state.get('template_text', '')
            key_points_text = st.text_area(
                "📝 Key Points",
                value=default_text,
                placeholder="Enter the main points you want to include in your email (one per line)...",
                height=120,
                help="List the important topics or messages you want to convey"
            )
            
            # Convert text to list
            if key_points_text:
                key_points = [point.strip() for point in key_points_text.split('\n') if point.strip()]
            else:
                key_points = []
            
            # Email type selection
            email_type = st.selectbox(
                "📧 Email Type",
                options=["custom", "thank_you", "new_article", "report_sharing", "meeting_followup", "project_update"],
                format_func=lambda x: {
                    "custom": "Custom Email",
                    "thank_you": "Thank You Message",
                    "new_article": "New Article/News",
                    "report_sharing": "Report Sharing",
                    "meeting_followup": "Meeting Follow-up",
                    "project_update": "Project Update"
                }[x],
                help="Choose the type of email you want to generate"
            )
            
            # Tone selection
            tone = st.selectbox(
                "🎭 Tone",
                options=["professional", "friendly", "formal", "casual", "urgent"],
                help="Choose the tone that matches your communication style"
            )
            
            # Context
            context = st.text_area(
                "🔍 Context (Optional)",
                placeholder="Provide any background information or context...",
                height=80,
                help="Add any relevant background information"
            )
            
            # Temperature slider
            temperature = st.slider(
                "🌡️ Creativity Level",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Lower values = more focused, Higher values = more creative"
            )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Generate Email", use_container_width=True)
    
    with col2:
        st.subheader("💡 Tips")
        st.markdown("""
        <div class="info-box">
            <p><strong>✅ Best Practices:</strong></p>
            <p>• Be specific with key points</p>
            <p>• Choose appropriate tone</p>
            <p>• Add relevant context</p>
            <p>• Review generated content</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Template suggestions with dynamic content
        st.markdown("""
        <div class="info-box">
            <p><strong>📝 Available Templates:</strong></p>
            <p>• <strong>Thank You:</strong> Appreciation messages</p>
            <p>• <strong>New Article:</strong> Content announcements</p>
            <p>• <strong>Report Sharing:</strong> Data and analysis</p>
            <p>• <strong>Meeting Follow-up:</strong> Action items</p>
            <p>• <strong>Project Update:</strong> Progress reports</p>
            <p>• <strong>Custom:</strong> Any other purpose</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Usage statistics
        st.markdown("""
        <div class="info-box">
            <p><strong>🚀 Features:</strong></p>
            <p>• AI-powered email generation</p>
            <p>• Multiple email types</p>
            <p>• Quality evaluation</p>
            <p>• Professional templates</p>
            <p>• Instant preview & editing</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process form submission
if submitted:
    if not key_points:
        st.warning("⚠️ Please enter at least one key point.")
    else:
        with st.spinner("🤖 Generating your email..."):
            try:
                # Build the prompt
                prompt = build_prompt(key_points, tone, context, email_type)
                
                # Generate the reply
                response = groq_client.send_prompt(prompt, temperature)
                
                if response:
                    # Evaluate the reply
                    evaluation = evaluate_reply(response, key_points)
                    detailed_eval = detailed_evaluation(response, key_points)
                    
                    # Display results
                    st.markdown('<div class="main-card">', unsafe_allow_html=True)
                    st.subheader("📧 Generated Email")
                    
                    # Show the generated email
                    st.markdown(f"""
                    <div class="generated-email">
                        <div style="white-space: pre-wrap;">
                            {response}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Allow editing
                    edited_email = st.text_area(
                        "✏️ Edit Email (Optional)",
                        value=response,
                        height=200,
                        help="Make any adjustments to the generated email"
                    )
                    
                    # Show evaluation results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📊 Quality Check")
                        if evaluation['all_key_points_included']:
                            st.success("✅ All key points included")
                        else:
                            st.error("❌ Some key points missing")
                        
                        if evaluation['tone_is_polite']:
                            st.success("✅ Polite tone detected")
                        else:
                            st.warning("⚠️ Consider more polite language")
                    
                    with col2:
                        st.subheader("📈 Statistics")
                        st.metric("Word Count", detailed_eval['word_count'])
                        
                        if detailed_eval['missing_points']:
                            st.write("**Missing Points:**")
                            for point in detailed_eval['missing_points']:
                                st.write(f"• {point}")
                        
                        if detailed_eval['suggestions']:
                            st.write("**Suggestions:**")
                            for suggestion in detailed_eval['suggestions']:
                                st.write(f"• {suggestion}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                else:
                    st.error("❌ Failed to generate email. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("""
---
<div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 2rem;">
    <p>Powered by Groq's LLaMA AI Model • Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)