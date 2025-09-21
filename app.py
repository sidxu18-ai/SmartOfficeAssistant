import streamlit as st
import os
import smtplib
import re
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from dotenv import load_dotenv
import groq
from typing import Optional, Dict, List

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

def build_prompt(key_points: List[str], tone: str, context: str) -> str:
    prompt = f"""Write a professional email with the following key points:
{chr(10).join('- ' + point for point in key_points)}

Tone: {tone}
Additional Context: {context}

Please write a complete, well-structured email incorporating these points."""
    return prompt

def evaluate_email(email_text: str, key_points: List[str]) -> Dict[str, any]:
    """Simple email evaluation"""
    evaluation = {
        "completeness": all(point.lower() in email_text.lower() for point in key_points),
        "length": len(email_text.split()),
        "suggestions": []
    }
    
    if evaluation["length"] < 50:
        evaluation["suggestions"].append("Consider adding more detail")
    elif evaluation["length"] > 500:
        evaluation["suggestions"].append("Consider making the email more concise")
        
    return evaluation

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = GroqAPIClient()

# Set page config
st.set_page_config(
    page_title="Smart Office Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Add Google Fonts
st.markdown('''
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    ''', unsafe_allow_html=True)

# Initialize session state for attachments
if 'attachments' not in st.session_state:
    st.session_state.attachments = []

def handle_uploaded_file(uploaded_file):
    """Process an uploaded file and add it to session state"""
    if uploaded_file is not None:
        # Check file size (10MB limit)
        if uploaded_file.size > 10 * 1024 * 1024:
            return False, "File size exceeds 10MB limit"
        
        # Save file info to session state
        file_info = {
            'name': uploaded_file.name,
            'type': uploaded_file.type,
            'size': uploaded_file.size,
            'data': uploaded_file.getvalue()
        }
        
        # Add to session state if not already present
        if not any(f['name'] == file_info['name'] for f in st.session_state.attachments):
            st.session_state.attachments.append(file_info)
            return True, f"Added {uploaded_file.name}"
        
        return False, "File already attached"
    
    return False, "No file provided"

def is_valid_email(email):
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_email_template(template_name="default"):
    """Get predefined email templates"""
    templates = {
        "newsletter": {
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #2196F3; color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }
                    .content { background: #fff; padding: 30px; border: 1px solid #e0e0e0; }
                    .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
                    .button { display: inline-block; padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{header}</h1>
                    </div>
                    <div class="content">
                        {content}
                    </div>
                    <div class="footer">
                        {footer}
                    </div>
                </div>
            </body>
            </html>
            """,
            "plain": "{header}\n\n{content}\n\n{footer}"
        },
        "meeting": {
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: 'Calibri', sans-serif; line-height: 1.5; color: #2c3e50; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .calendar-box { background: #ecf0f1; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0; }
                    .details { background: #fff; padding: 20px; border: 1px solid #bdc3c7; margin-top: 20px; }
                    .button { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>{header}</h2>
                    <div class="calendar-box">
                        {content}
                    </div>
                    <div class="details">
                        {footer}
                    </div>
                </div>
            </body>
            </html>
            """,
            "plain": "{header}\n\n{content}\n\n{footer}"
        },
        "thank_you": {
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: 'Georgia', serif; line-height: 1.8; color: #2c3e50; }
                    .container { max-width: 600px; margin: 0 auto; padding: 30px; }
                    .message { text-align: center; padding: 40px 20px; }
                    .signature { margin-top: 40px; font-style: italic; }
                    h1 { color: #e74c3c; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="message">
                        <h1>{header}</h1>
                        <div class="content">
                            {content}
                        </div>
                        <div class="signature">
                            {footer}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            "plain": "{header}\n\n{content}\n\n{footer}"
        },
        "default": {
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .email-container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .email-header { margin-bottom: 20px; }
                    .email-content { background: #fff; padding: 20px; border-radius: 5px; }
                    .email-footer { margin-top: 20px; font-size: 12px; color: #666; }
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        {header}
                    </div>
                    <div class="email-content">
                        {content}
                    </div>
                    <div class="email-footer">
                        {footer}
                    </div>
                </div>
            </body>
            </html>
            """,
            "plain": "{header}\n\n{content}\n\n{footer}"
        },
        "formal": {
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: 'Times New Roman', serif; line-height: 1.8; color: #1a1a1a; }
                    .email-container { max-width: 600px; margin: 0 auto; padding: 30px; }
                    .email-header { border-bottom: 2px solid #1a1a1a; padding-bottom: 20px; margin-bottom: 30px; }
                    .email-content { text-align: justify; }
                    .signature { margin-top: 40px; }
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        {header}
                    </div>
                    <div class="email-content">
                        {content}
                    </div>
                    <div class="signature">
                        {footer}
                    </div>
                </div>
            </body>
            </html>
            """,
            "plain": "{header}\n\n{content}\n\n{footer}"
        }
    }
    return templates.get(template_name, templates["default"])

def convert_to_html(text):
    """Convert plain text to HTML with basic formatting"""
    # Replace newlines with HTML breaks
    text = text.replace('\n', '<br>')
    
    # Convert URLs to links
    url_pattern = r'(https?://\S+)'
    text = re.sub(url_pattern, r'<a href="\1">\1</a>', text)
    
    # Add basic paragraph formatting
    paragraphs = text.split('<br><br>')
    text = ''.join([f'<p>{p}</p>' for p in paragraphs])
    
    return text

def send_email(sender_email, receiver_email, subject, body, smtp_password, provider="gmail", template="default", attachments=None):
    """Send email using SMTP with HTML support and templates"""
    try:
        # Create message
        message = MIMEMultipart('alternative')
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        
        # Get template
        template = get_email_template(template)
        
        # Create plain text version
        text_content = template["plain"].format(
            header=f"Subject: {subject}",
            content=body,
            footer=f"Sent by {sender_email}"
        )
        
        # Create HTML version
        html_content = template["html"].format(
            header=f"<h2>{subject}</h2>",
            content=convert_to_html(body),
            footer=f"<em>Sent by {sender_email}</em>"
        )
        
        # Attach both plain and HTML versions
        message.attach(MIMEText(text_content, 'plain'))
        message.attach(MIMEText(html_content, 'html'))
        
        # Attach files
        if attachments:
            for attachment in attachments:
                mime_type, _ = mimetypes.guess_type(attachment['name'])
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                maintype, subtype = mime_type.split('/', 1)
                
                if maintype == 'text':
                    att = MIMEText(attachment['data'].decode('utf-8'), _subtype=subtype)
                elif maintype == 'application':
                    att = MIMEApplication(attachment['data'], _subtype=subtype)
                else:
                    att = MIMEBase(maintype, subtype)
                    att.set_payload(attachment['data'])
                    encoders.encode_base64(att)
                
                att.add_header('Content-Disposition', 'attachment', filename=attachment['name'])
                message.attach(att)
        
        # Provider settings
        providers = {
            "gmail": ("smtp.gmail.com", 587),
            "outlook": ("smtp-mail.outlook.com", 587),
            "yahoo": ("smtp.mail.yahoo.com", 587),
            "custom": (st.secrets.get("SMTP_HOST", ""), st.secrets.get("SMTP_PORT", 587))
        }
        
        smtp_host, smtp_port = providers.get(provider, providers["gmail"])
        
        # Create SMTP session
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender_email, smtp_password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
            
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = GroqAPIClient()

# Set page config for better appearance
st.set_page_config(
    page_title="Smart Office Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern lovable design with proper text colors
st.markdown("""
<style>
    /* Engaging button styling */
    .stButton > button {
        background: #4CAF50 !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        background: #43A047 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(76, 175, 80, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2) !important;
    } Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = GroqAPIClient()

# Set page config for better appearance
st.set_page_config(
    page_title="Smart Office Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the custom CSS file
load_css('style.css')

# Add Google Fonts
st.markdown('''
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    ''', unsafe_allow_html=True)
    
    /* Global Styles */
    div.stApp {
        background: #E3F2FD !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        min-height: 100vh !important;
    }
    
    /* Ensure background covers entire page */
    .main .block-container {
        background: transparent !important;
    }
    
    /* Override any default Streamlit backgrounds */
    .stApp > div {
        background: transparent !important;
    }
    
    /* Simple text colors - black on white background */
    .stApp * {
        color: #333333 !important;
    }
    
    /* Clear headings */
    h1, h2, h3, h4, h5, h6 {
        color: #dc3545 !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Regular text */
    p, div, span {
        color: #333333 !important;
    }
    
    /* Simple labels */
    label {
        color: #dc3545 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
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
        background: linear-gradient(45deg, #1565C0, #4CAF50) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .main-header p {
        font-size: 1.2rem;
        color: #666666 !important;
        margin-bottom: 0;
        font-weight: 500;
    }
    
    /* Simple card styling */
    .main-card {
        background: #ffffff !important;
        border-radius: 10px;
        padding: 2rem;
        border: 2px solid #dc3545;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .main-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(220, 53, 69, 0.2);
    }
    
    /* User-friendly input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: #f8f9fa !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 8px !important;
        color: #2E7D32 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #2E7D32 !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2) !important;
        background: #ffffff !important;
    }
    
    /* Placeholder text style */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #81C784 !important;
        font-style: italic;
    }
    
    /* Simple red button styling */
    .stButton > button {
        background: #dc3545 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: #c82333 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Quick actions grid */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .quick-action {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid #dc3545;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .quick-action:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.2);
        background: #fff5f5;
    }
    
    .quick-action h4 {
        color: #dc3545 !important;
        margin: 0.5rem 0;
        font-weight: 600;
    }
    
    .quick-action p {
        color: #666666 !important;
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* Success/Error message styling */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    .stSuccess {
        background: rgba(72, 187, 120, 0.2) !important;
        color: #68d391 !important;
    }
    
    .stError {
        background: rgba(245, 101, 101, 0.2) !important;
        color: #f56565 !important;
    }
    
    /* Friendly, encouraging labels */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stSlider label {
        color: #1565C0 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 8px !important;
        padding-left: 4px !important;
        position: relative !important;
    }
    
    /* Add a friendly icon hint */
    .stTextInput label::before,
    .stTextArea label::before,
    .stSelectbox label::before {
        content: '💡 ';
        margin-right: 4px;
    }
    
    /* Simple info box styling */
    .info-box {
        background: #fff5f5;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #f8d7da;
    }
    
    .info-box p {
        margin: 0;
        color: #333333 !important;
    }
    
    /* Simple sidebar styling */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 2px solid #dc3545 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #dc3545 !important;
    }
    
    /* Additional background fixes */
    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Attachment styling */
    .attachment-section {
        margin-top: 1rem;
        border-top: 1px solid #e2e8f0;
        padding-top: 1rem;
    }
    
    .attachment-label {
        color: #1565C0 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 8px !important;
    }
    
    .attachment-list {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #4CAF50 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        background: rgba(76, 175, 80, 0.05) !important;
    }
    
    .stFileUploader > div:hover {
        border-color: #2E7D32 !important;
        background: rgba(76, 175, 80, 0.1) !important;
    }
    
    /* Clean white background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: #ffffff;
        z-index: -1;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 Smart Office Assistant</h1>
    <p>Your AI-powered email and communication companion</p>
</div>
""", unsafe_allow_html=True)

# Quick actions
st.markdown("""
<div class="quick-actions">
    <div class="quick-action">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📧</div>
        <h4>Email Generation</h4>
        <p>Create professional emails instantly</p>
    </div>
    <div class="quick-action">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💬</div>
        <h4>Smart Replies</h4>
        <p>Generate contextual responses</p>
    </div>
    <div class="quick-action">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✨</div>
        <h4>AI Assistant</h4>
        <p>Get help with any task</p>
    </div>
    <div class="quick-action">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
        <h4>Analytics</h4>
        <p>Track your productivity</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content area
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("✨ Generate Professional Email")
        
        # Email form
        with st.form("email_form"):
            # Email addresses
            col_from, col_to = st.columns(2)
            with col_from:
                sender_email = st.text_input(
                    "📤 From",
                    placeholder="your@email.com",
                    help="Enter your email address"
                )
            with col_to:
                receiver_email = st.text_input(
                    "📥 To",
                    placeholder="recipient@email.com",
                    help="Enter recipient's email address"
                )
            
            # Subject
            subject = st.text_input(
                "📫 Subject",
                placeholder="Enter email subject...",
                help="Enter a clear and concise subject line"
            )
            
            # Key points
            key_points = st.text_area(
                "📝 Key Points",
                placeholder="Enter the main points you want to include in your email...",
                height=100,
                help="List the important topics or messages you want to convey"
            )
            
            # Tone selection
            tone = st.selectbox(
                "🎭 Tone",
                options=["professional", "friendly", "formal", "casual", "urgent"],
                help="Choose the tone that matches your communication style"
            )
            
            # Context
            context = st.text_area(
                "🔍 Context",
                placeholder="Provide any background information or context...",
                height=80,
                help="Add any relevant background information"
            )
            
            # File attachments
            st.markdown("""
            <div class="attachment-section">
                <p class="attachment-label">📎 Attachments (Optional)</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_files = st.file_uploader(
                "",
                type=["txt", "pdf", "doc", "docx", "xls", "xlsx", "jpg", "png"],
                accept_multiple_files=True,
                help="Drag and drop files here (max 10MB each)"
            )
            
            if uploaded_files:
                st.markdown('<div class="attachment-list">', unsafe_allow_html=True)
                total_size = 0
                for file in uploaded_files:
                    size_mb = file.size / (1024 * 1024)
                    total_size += size_mb
                    if size_mb > 10:
                        st.error(f"❌ {file.name} exceeds 10MB limit")
                    else:
                        st.success(f"✅ {file.name} ({size_mb:.1f}MB)")
                
                if total_size > 25:
                    st.warning("⚠️ Total attachments exceed 25MB limit")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Temperature slider
            temperature = st.slider(
                "🌡️ Creativity Level",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Lower values = more focused, Higher values = more creative"
            )
            
            # File attachments
            uploaded_file = st.file_uploader(
                "📎 Attachments",
                type=["txt", "pdf", "doc", "docx", "xls", "xlsx", "jpg", "png", "zip"],
                help="Upload files (max 10MB each)"
            )
            
            if uploaded_file is not None:
                success, message = handle_uploaded_file(uploaded_file)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            
            # Show current attachments
            if st.session_state.attachments:
                st.write("📁 Current Attachments:")
                for idx, attachment in enumerate(st.session_state.attachments):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"{attachment['name']} ({attachment['size'] / 1024:.1f} KB)")
                    with col2:
                        if st.button("❌", key=f"remove_{idx}"):
                            st.session_state.attachments.pop(idx)
                            st.experimental_rerun()
            
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
            <p>• Review before sending</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats or additional info could go here
        st.markdown("""
        <div class="info-box">
            <p><strong>🎯 Quick Stats:</strong></p>
            <p>• Average generation time: 2-3s</p>
            <p>• Success rate: 98%</p>
            <p>• Languages supported: 50+</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process form submission
if submitted:
    # Retrieve sidebar selections for email_provider and email_template
    email_provider = st.session_state.get("email_provider") if "email_provider" in st.session_state else "gmail"
    email_template = st.session_state.get("email_template") if "email_template" in st.session_state else "default"

    if not sender_email or not receiver_email or not subject or not key_points:
        st.warning("⚠️ Please fill in all required fields (From, To, Subject, and Key Points).")
    else:
        with st.spinner("🤖 Generating your email..."):
            try:
                # Build the prompt with additional context
                email_context = f"""
                From: {sender_email}
                To: {receiver_email}
                Subject: {subject}
                
                Additional Context: {context}
                """
                
                # Build the prompt
                prompt = build_prompt(key_points, tone, email_context)
                
                # Generate the reply
                response = groq_client.send_prompt(prompt)
                
                if response:
                    # Evaluate the reply
                    evaluation = evaluate_email(response, key_points)
                    
                    # Display results
                    st.markdown('<div class="main-card">', unsafe_allow_html=True)
                    st.subheader("📧 Generated Email")
                    
                    # Show the generated email in email format
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.95); color: #2d3748; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; font-family: 'Inter', sans-serif;">
                        <div style="border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem; padding-bottom: 1rem;">
                            <strong style="color: #4a5568">From:</strong> {sender_email}<br>
                            <strong style="color: #4a5568">To:</strong> {receiver_email}<br>
                            <strong style="color: #4a5568">Subject:</strong> {subject}
                        </div>
                        <div style="white-space: pre-wrap;">
                            {response}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add send button
                    col_edit, col_send = st.columns([3, 1])
                    with col_edit:
                        edited_email = st.text_area(
                            "✏️ Edit Email",
                            value=response,
                            height=300
                        )
                    with col_send:
                        if st.button("📧 Send Email"):
                            smtp_password = os.getenv('SMTP_PASSWORD')
                            if not smtp_password:
                                st.error("❌ SMTP Password not configured. Please add SMTP_PASSWORD to your .env file.")
                            else:
                                # Validate email addresses
                                if not is_valid_email(sender_email):
                                    st.error("❌ Invalid sender email address format.")
                                elif not is_valid_email(receiver_email):
                                    st.error("❌ Invalid recipient email address format.")
                                else:
                                    # Custom SMTP validation
                                    if email_provider == "custom" and not (st.secrets.get("SMTP_HOST") and st.secrets.get("SMTP_PORT")):
                                        st.error("❌ Custom SMTP settings are not configured.")
                                    else:
                                        # Show sending indicator
                                        with st.spinner("📤 Sending email..."):
                                            # Check total attachment size
                                            total_size = sum(att['size'] for att in st.session_state.attachments)
                                            if total_size > 25 * 1024 * 1024:  # 25MB total limit
                                                st.error("❌ Total attachment size exceeds 25MB limit")
                                            else:
                                                success, message = send_email(
                                                    sender_email,
                                                    receiver_email,
                                                    subject,
                                                    edited_email,
                                                    smtp_password,
                                                    provider=email_provider,
                                                    template=email_template,
                                                    attachments=st.session_state.attachments
                                                )
                                            
                                            if success:
                                                st.success(message)
                                                # Save successful template for future use
                                                st.session_state['last_template'] = email_template
                                            else:
                                                st.error(message)
                    
                    # Show evaluation results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if evaluation['all_points_covered']:
                            st.success(f"✅ All key points covered! ({evaluation['coverage_percentage']:.1f}%)")
                        else:
                            st.warning(f"⚠️ Coverage: {evaluation['coverage_percentage']:.1f}%")
                            st.info(f"Missing points: {', '.join(evaluation['missing_points'])}")
                    
                    with col2:
                        st.info(f"📊 Points found: {len(evaluation['found_points'])}/{len(evaluation['all_points'])}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Please check your API key and try again.")

elif submitted and not key_points:
    st.warning("⚠️ Please enter some key points to generate an email.")

# Sidebar with additional features
with st.sidebar:
    st.markdown("### 🛠️ Settings")
    
    # API Status
    api_key = os.getenv('GROQ_API_KEY')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if api_key:
        st.success("✅ API Key Configured")
    else:
        st.error("❌ API Key Missing")
        st.info("Add your GROQ_API_KEY to the .env file")
    
    # Email Settings
    st.markdown("#### 📧 Email Settings")
    
    # Email Provider Selection
    email_provider = st.selectbox(
        "📫 Email Provider",
        options=["gmail", "outlook", "yahoo", "custom"],
        help="Select your email service provider"
    )
    
    if email_provider == "custom":
        smtp_host = st.text_input("SMTP Host", placeholder="smtp.example.com")
        smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        if smtp_host and smtp_port:
            st.secrets["SMTP_HOST"] = smtp_host
            st.secrets["SMTP_PORT"] = smtp_port
    
    # Email Template Selection
    email_template = st.selectbox(
        "📝 Email Template",
        options=["default", "formal", "newsletter", "meeting", "thank_you"],
        help="Choose an email template style"
    )
    
    # Template description
    template_descriptions = {
        "default": "Clean, modern design suitable for general communication",
        "formal": "Professional style ideal for business correspondence",
        "newsletter": "Eye-catching layout perfect for newsletters and updates",
        "meeting": "Structured format for meeting invitations and agendas",
        "thank_you": "Elegant design for expressing gratitude and appreciation"
    }
    st.caption(template_descriptions[email_template])
    
    # SMTP Password Status
    if smtp_password:
        st.success("✅ SMTP Password Configured")
    else:
        st.error("❌ SMTP Password Missing")
        st.info(f"""
        To use {email_provider.title()} SMTP:
        1. Enable 2-Step Verification
        2. Generate App Password
        3. Add it as SMTP_PASSWORD in .env
        """)
        
    # Show template preview
    with st.expander("📋 Template Preview"):
        template = get_email_template(email_template)
        st.markdown(f"""
        **HTML Preview:**
        ```html
        {template['html'][:200]}...
        ```
        """)
        st.info("Template will be automatically formatted with your content")
    
    st.markdown("---")
    
    # Model selection
    model = st.selectbox(
        "🤖 AI Model",
        options=["llama-3.1-8b-instant", "llama-3.1-70b-versatile"],
        help="Choose the AI model for generation"
    )
    
    # Max tokens
    max_tokens = st.slider(
        "📏 Max Response Length",
        min_value=100,
        max_value=2000,
        value=1000,
        step=100
    )
    
    st.markdown("---")
    
    # About section
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Smart Office Assistant** helps you generate professional emails and responses using AI.
    
    **Features:**
    - ✨ AI-powered email generation
    - 🎭 Multiple tone options
    - 📊 Content evaluation
    - 🚀 Fast and reliable
    """)
    
    # Version info
    st.markdown("---")
    st.markdown("**Version:** 1.0.0")
    st.markdown("**Powered by:** Groq AI")