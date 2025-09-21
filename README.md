# 🤖 Smart Office Assistant - AI Email Generator

An intelligent email generation tool powered by Groq's LLaMA AI model. Create professional emails with AI assistance, featuring multiple email types, quality evaluation, and beautiful UI.

## ✨ Features

- **AI-Powered Email Generation** - Uses Groq's LLaMA 3.1 model
- **Multiple Email Types** - Thank you, articles, reports, follow-ups, updates
- **Quick Templates** - Pre-built templates for common scenarios
- **Quality Evaluation** - Automatic assessment of completeness and tone
- **Professional UI** - Beautiful gradient design with responsive layout
- **Real-time Editing** - Modify generated emails before use

## 🚀 Email Types Supported

1. **Thank You Messages** - Express gratitude and appreciation
2. **New Article/News** - Share content and announcements
3. **Report Sharing** - Present data and findings professionally
4. **Meeting Follow-up** - Summarize decisions and action items
5. **Project Updates** - Share progress and milestones
6. **Custom Emails** - Any other purpose

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API key (get from [console.groq.com](https://console.groq.com/keys))

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sidxu18-ai/SmartOfficeAssistant.git
   cd SmartOfficeAssistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 🎯 Usage

1. **Start the application**
   ```bash
   streamlit run simple_app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Generate emails**:
   - Choose an email type or use quick templates
   - Enter your key points (one per line)
   - Select tone and creativity level
   - Click "Generate Email"
   - Review, edit, and use the generated content

## 📁 Project Structure

```
SmartOfficeAssistant/
├── simple_app.py          # Main Streamlit application
├── groq_utils.py          # Groq API integration
├── evaluation_utils.py    # Email quality evaluation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🎨 Features in Detail

### Quick Templates
- **Thank You 💝** - Pre-fills appreciation message template
- **New Article 📄** - Pre-fills content sharing template
- **Report 📊** - Pre-fills report sharing template

### Quality Evaluation
- **Completeness Check** - Verifies all key points are included
- **Tone Analysis** - Ensures polite and professional language
- **Word Count** - Tracks email length
- **Improvement Suggestions** - AI-powered recommendations

### Professional UI
- Beautiful purple gradient background
- Glass-morphism design effects
- Responsive layout for all screen sizes
- Intuitive form controls

## 🔧 Configuration

The application uses the following environment variables:

- `GROQ_API_KEY` - Your Groq API key (required)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for providing the LLaMA AI model
- [Streamlit](https://streamlit.io/) for the web framework
- [OpenAI](https://openai.com/) for AI development inspiration

## 📞 Support

If you have any questions or issues, please open an issue on [GitHub](https://github.com/sidxu18-ai/SmartOfficeAssistant/issues).

---

**Made with ❤️ and AI**