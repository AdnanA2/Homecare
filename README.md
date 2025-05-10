# HomeCare AI

HomeCare AI is a practical tool designed to make life easier for caregivers. It transforms voice notes into professional care documentation with just a few clicks. Whether you're a home health aide, nurse, or family caregiver, this app helps you maintain clear, organized records of your care visits.

Here's how it works: You record a voice memo during or after your visit, upload it to the app, and HomeCare AI takes care of the rest. It uses OpenAI's Whisper to transcribe your voice notes and Google's Gemini AI to create a structured, professional summary. The result is a clean care log that you can save as a PDF or text file, email to family members or healthcare providers, and keep in your records. Everything is stored securely in a local database, making it easy to track and reference past visits.

## ✨ Features

- 🔐 Secure login system for caregivers
- 🎙️ Upload voice memos (.wav or .mp3)
- 📝 Automatic transcription using Whisper
- 🧠 Smart summarization with Gemini AI
- 📄 Download care logs as PDF or TXT
- ✉️ Email summaries to family or providers
- 💾 Local SQLite database for recordkeeping
- 🎨 Clean, intuitive interface built with Streamlit

## 🚀 Running the App Locally

Want to try it out? Here's how to get started:

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/homecare_ai.git
   cd homecare_ai
   ```

2. **Set up a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install the requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your secrets**
   Create a file at `.streamlit/secrets.toml` with your API keys and email settings:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   EMAIL_USERNAME = "youremail@gmail.com"
   EMAIL_PASSWORD = "your-gmail-app-password"
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```
   Then open http://localhost:8501 in your browser.

## 📁 Project Structure

Here's what each main file does:

- `app.py` - The main interface you interact with
- `transcribe.py` - Handles converting voice memos to text
- `summarize.py` - Creates professional summaries using Gemini AI
- `export_pdf.py` - Generates PDF versions of the summaries
- `email_utils.py` - Manages sending summaries via email
- `database.py` - Keeps track of all your care logs

## 📝 Important Notes

- 🔒 Keep your API keys and email credentials secure! They should only be in your `.streamlit/secrets.toml` file, which is automatically ignored by git.
- 🏥 This app is designed for internal use or pilot programs. It's not intended as a public production tool.
- 💻 Everything runs on your local machine, and all data is stored locally in a SQLite database.
- 🆘 Need help? Check the issues section or create a new one if you find a bug.

## 🤝 Contributing

We welcome contributions! Whether you're a developer who wants to add features or a caregiver with ideas for improvements, feel free to:
- Open an issue to report bugs or suggest features
- Submit a pull request with your improvements
- Share your experience using the app

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Made with ❤️ for caregivers everywhere. Your work matters, and we hope this tool makes it a little easier. 