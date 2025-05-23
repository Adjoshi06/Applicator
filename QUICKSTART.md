# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Ollama installed and running (`ollama serve`)
- [ ] Llama 3.1 8B model pulled (`ollama pull llama3.1:8b`)
- [ ] Google Cloud project created
- [ ] Gmail API, Google Drive API, and Google Docs API enabled
- [ ] OAuth credentials downloaded as `credentials.json`
- [ ] Resume uploaded to Google Docs
- [ ] Google Doc ID obtained from URL

## Setup Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   # Copy env.example to .env
   cp env.example .env
   
   # Edit .env and add:
   # - GOOGLE_DRIVE_RESUME_ID (from your Google Doc URL)
   # - USER_PREFERENCES (comma-separated)
   # - USER_LOCATION
   ```

3. **First run - authenticate:**
   ```bash
   # This will open browser for OAuth
   python main.py check
   ```

4. **Parse your resume:**
   ```bash
   python main.py refresh-resume
   ```

## Typical Workflow

```bash
# 1. Check for new job emails
python main.py check

# 2. Score the jobs
python main.py score

# 3. Review high-scoring jobs
python main.py review --min-score 80

# 4. Research companies
python main.py research-high

# 5. Generate cover letters
python main.py generate
```

## Troubleshooting

### Ollama not running
```bash
# Start Ollama
ollama serve

# In another terminal, verify model
ollama list
```

### Authentication issues
```bash
# Delete tokens and re-authenticate
rm gmail_token.json drive_token.json
python main.py check
```

### Resume parsing fails
- Verify `GOOGLE_DRIVE_RESUME_ID` is correct
- Check Google Doc is accessible
- Try `python main.py refresh-resume`

## File Structure

```
.
├── main.py                 # CLI entry point
├── config.py              # Configuration
├── storage.py             # Storage (ChromaDB + JSON)
├── ollama_client.py       # Ollama LLM client
├── gmail_client.py        # Gmail API
├── drive_client.py        # Google Drive API
├── resume_parser.py       # Resume parsing
├── email_parser.py        # Email parsing
├── job_scorer.py          # Job scoring
├── company_researcher.py  # Company research
├── material_generator.py  # Cover letters/highlights
├── jobs/                  # Stored jobs (JSON)
├── chroma_db/             # Vector storage
├── cover_letters/         # Generated cover letters
└── resume_highlights/     # Generated highlights
```

## Next Steps

1. Run `python main.py check` to parse job emails
2. Run `python main.py score` to score jobs
3. Review jobs with `python main.py review`
4. Generate materials for high-scoring jobs

For detailed documentation, see [README.md](README.md).

