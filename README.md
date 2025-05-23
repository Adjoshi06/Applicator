# Job Application Assistant

A minimalistic Python application that monitors Gmail for job alerts, parses them using local Llama 3.1 8B (via Ollama), scores jobs based on your resume, and generates customized cover letters and resume highlights.

## Features

- 📧 **Gmail Monitoring**: Automatically checks for job alert emails from LinkedIn, Indeed, Glassdoor, etc.
- 📄 **Resume Integration**: Fetches and parses your resume from Google Docs
- 🤖 **Local LLM Processing**: Uses Ollama with Llama 3.1 8B for all LLM operations (privacy-first)
- 📊 **Job Scoring**: Scores jobs 0-100 based on skills match, preferences, and location
- 🔍 **Company Research**: Researches high-scoring companies using web search
- ✍️ **Material Generation**: Generates customized cover letters and resume highlights
- 💾 **Local Storage**: All data stored locally (ChromaDB for vectors, JSON for jobs)

## Prerequisites

1. **Python 3.8+**
2. **Ollama** with Llama 3.1 8B model installed
3. **Google Cloud Project** with Gmail API and Google Drive API enabled
4. **Google OAuth Credentials** (credentials.json)

## Setup

### 1. Install Ollama and Llama 3.1 8B

```bash
# Install Ollama (visit https://ollama.ai for installation)
# Then pull the model:
ollama pull llama3.1:8b

# Verify it's working:
ollama run llama3.1:8b "Hello, world!"
```

### 2. Set Up Google APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Drive API
   - Google Docs API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials and save as `credentials.json` in the project root

### 3. Get Your Google Doc Resume ID

1. Open your resume in Google Docs
2. The Document ID is in the URL: `https://docs.google.com/document/d/{DOCUMENT_ID}/edit`
3. Copy the `DOCUMENT_ID` part

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

Create a `.env` file in the project root:

```env
# Google APIs
GMAIL_CREDENTIALS_PATH=credentials.json
GOOGLE_DRIVE_RESUME_ID=your_document_id_here

# User preferences (not in resume)
USER_PREFERENCES=Remote or hybrid,AI/ML focus,Startup or Mid-size companies
USER_LOCATION=San Francisco, CA
MIN_SCORE_FOR_RESEARCH=70
MIN_SCORE_FOR_NOTIFICATION=80
```

### 6. First Run - OAuth Authentication

On first run, the application will open a browser window for OAuth authentication:
- You'll need to authenticate for both Gmail and Google Drive
- Tokens will be saved as `gmail_token.json` and `drive_token.json`

## Usage

### Check for New Job Emails

```bash
python main.py check
```

This will:
- Check Gmail for unread job alert emails
- Parse them using Llama 3.1 8B
- Extract job data (title, company, location, description, URL)
- Save jobs to local storage
- Mark emails as read

### Score Jobs

```bash
python main.py score
```

This will:
- Load your resume from Google Docs (or use cache)
- Score all unscored jobs based on:
  - Skills match (40 points)
  - Experience level match (20 points)
  - Preferences match (20 points)
  - Location match (10 points)
  - Overall fit (10 points)

### Review Jobs

```bash
# Review all jobs
python main.py review

# Review only high-scoring jobs
python main.py review --min-score 80
```

### Research a Company

```bash
python main.py research "Company Name"
```

### Research High-Scoring Companies

```bash
python main.py research-high
```

This will research companies for all jobs scoring above `MIN_SCORE_FOR_RESEARCH`.

### Generate Cover Letters and Resume Highlights

```bash
# Generate for all high-scoring jobs
python main.py generate

# Generate for a specific job
python main.py generate --job-id <job_id>
```

Generated materials are saved in:
- `cover_letters/<job_id>_cover_letter.txt`
- `resume_highlights/<job_id>_highlights.txt`

### Refresh Resume Data

```bash
python main.py refresh-resume
```

Forces a refresh of resume data from Google Docs (bypasses cache).

## Workflow

Typical workflow:

```bash
# 1. Check for new job emails
python main.py check

# 2. Score the new jobs
python main.py score

# 3. Review high-scoring jobs
python main.py review --min-score 80

# 4. Research companies for jobs you're interested in
python main.py research-high

# 5. Generate cover letters and resume highlights
python main.py generate
```

## Project Structure

```
.
├── main.py                 # CLI entry point
├── config.py              # Configuration management
├── storage.py             # Storage layer (ChromaDB + JSON)
├── ollama_client.py       # Ollama LLM client
├── gmail_client.py        # Gmail API client
├── drive_client.py        # Google Drive API client
├── resume_parser.py       # Resume parsing with Llama
├── email_parser.py        # Email parsing with Llama
├── job_scorer.py          # Job scoring logic
├── company_researcher.py  # Company research with web search
├── material_generator.py  # Cover letter and highlights generation
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── jobs/                 # Stored job data (JSON files)
├── chroma_db/            # ChromaDB vector storage
├── cover_letters/        # Generated cover letters
└── resume_highlights/    # Generated resume highlights
```

## Configuration

### Environment Variables

- `GMAIL_CREDENTIALS_PATH`: Path to Google OAuth credentials JSON file
- `GOOGLE_DRIVE_RESUME_ID`: Google Doc ID of your resume
- `USER_PREFERENCES`: Comma-separated preferences (e.g., "Remote,AI/ML focus,Startup")
- `USER_LOCATION`: Preferred location
- `MIN_SCORE_FOR_RESEARCH`: Minimum score to trigger company research (default: 70)
- `MIN_SCORE_FOR_NOTIFICATION`: Minimum score to generate materials (default: 80)
- `OLLAMA_BASE_URL`: Ollama API URL (default: http://localhost:11434)

## Notes

- **Privacy**: All data stays local. No external APIs are used for LLM operations.
- **Ollama Performance**: Llama 3.1 8B may be slower than cloud APIs but provides privacy and no API costs.
- **Parsing Accuracy**: The LLM may occasionally misparse emails or resumes. Review generated data.
- **Resume Cache**: Resume data is cached locally. Use `refresh-resume` to update.
- **Job Deduplication**: Jobs are deduplicated based on title, company, and URL.

## Troubleshooting

### Ollama Connection Error

Ensure Ollama is running:
```bash
ollama serve
```

Verify the model is available:
```bash
ollama list
```

### Google API Authentication Errors

Delete `gmail_token.json` and `drive_token.json` and re-authenticate.

### Resume Parsing Issues

- Ensure `GOOGLE_DRIVE_RESUME_ID` is correct
- Check that the Google Doc is accessible
- Try `refresh-resume` to clear cache

### Job Parsing Issues

- Some emails may not be parsed correctly
- Check the `jobs/` directory for parsed job data
- Review and manually edit if needed

## License

MIT License

## Contributing

This is a minimalistic prototype. Feel free to extend and customize for your needs.

