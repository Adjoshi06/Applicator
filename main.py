"""Main CLI interface for the job application assistant."""
import argparse
import sys
import json
from pathlib import Path
from gmail_client import GmailClient
from email_parser import EmailParser
from resume_parser import ResumeParser
from job_scorer import JobScorer
from company_researcher import CompanyResearcher
from material_generator import MaterialGenerator
from storage import Storage
from config import Config


def check_emails():
    """Check Gmail for new job alerts and parse them."""
    print("🔍 Checking Gmail for job alerts...")
    
    gmail = GmailClient()
    parser = EmailParser()
    storage = Storage()
    
    emails = gmail.get_unread_job_emails(max_results=50)
    print(f"Found {len(emails)} unread job emails")
    
    parsed_count = 0
    for email in emails:
        try:
            job_data = parser.parse_email(
                email["subject"],
                email["body"],
                email["from"]
            )
            
            # Check if job already exists
            existing_jobs = storage.get_all_jobs()
            job_id = storage._generate_job_id(job_data)
            
            if any(job.get("id") == job_id for job in existing_jobs):
                print(f"⏭️  Skipping duplicate: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
                gmail.mark_as_read(email["id"])
                continue
            
            # Save job (without score yet)
            job_data["id"] = job_id
            job_file = Config.DATA_DIR / f"{job_id}.json"
            with open(job_file, "w") as f:
                json.dump(job_data, f, indent=2)
            
            print(f"✅ Parsed: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
            parsed_count += 1
            
            # Mark email as read
            gmail.mark_as_read(email["id"])
        except Exception as e:
            print(f"❌ Error parsing email: {e}")
            continue
    
    print(f"\n✨ Parsed {parsed_count} new jobs")
    return parsed_count


def score_jobs():
    """Score all unscored jobs based on resume."""
    print("📊 Scoring jobs...")
    
    # Load resume
    resume_parser = ResumeParser()
    try:
        resume_data = resume_parser.parse_resume()
        print("✅ Loaded resume data")
    except Exception as e:
        print(f"❌ Error loading resume: {e}")
        return
    
    # Load jobs
    storage = Storage()
    jobs = storage.get_all_jobs()
    unscored_jobs = [job for job in jobs if "score" not in job or job.get("score") == 0]
    
    if not unscored_jobs:
        print("✅ All jobs are already scored")
        return
    
    print(f"Found {len(unscored_jobs)} jobs to score")
    
    scorer = JobScorer(resume_data)
    scored_count = 0
    
    for job in unscored_jobs:
        try:
            scoring_result = scorer.score_job(job)
            job["score"] = scoring_result["score"]
            job["scoring"] = scoring_result
            
            # Save updated job
            job_file = Config.DATA_DIR / f"{job['id']}.json"
            import json
            with open(job_file, "w") as f:
                json.dump(job, f, indent=2)
            
            print(f"✅ Scored: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} - Score: {scoring_result['score']}/100")
            scored_count += 1
        except Exception as e:
            print(f"❌ Error scoring job: {e}")
            continue
    
    print(f"\n✨ Scored {scored_count} jobs")


def review_jobs(min_score: int = None):
    """Review jobs, optionally filtered by minimum score."""
    storage = Storage()
    jobs = storage.get_all_jobs()
    
    if min_score is not None:
        jobs = [job for job in jobs if job.get("score", 0) >= min_score]
        jobs.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    if not jobs:
        print("No jobs found")
        return
    
    print(f"\n{'='*80}")
    print(f"📋 JOB LISTING ({len(jobs)} jobs)")
    print(f"{'='*80}\n")
    
    for job in jobs:
        score = job.get("score", "Not scored")
        print(f"Title: {job.get('title', 'Unknown')}")
        print(f"Company: {job.get('company', 'Unknown')}")
        print(f"Location: {job.get('location', 'Unknown')}")
        print(f"Score: {score}/100")
        if "scoring" in job:
            scoring = job["scoring"]
            print(f"Reasoning: {scoring.get('reasoning', 'N/A')[:100]}...")
        print(f"URL: {job.get('url', 'N/A')}")
        print(f"Source: {job.get('source', 'Unknown')}")
        print(f"ID: {job.get('id', 'Unknown')}")
        print(f"{'-'*80}\n")


def research_company(company_name: str):
    """Research a company."""
    print(f"🔍 Researching {company_name}...")
    
    researcher = CompanyResearcher()
    research = researcher.research_company(company_name)
    
    print(f"\n{'='*80}")
    print(f"📊 COMPANY RESEARCH: {research.get('company', company_name)}")
    print(f"{'='*80}\n")
    print(f"Summary: {research.get('summary', 'N/A')}")
    print(f"\nTech Stack: {', '.join(research.get('tech_stack', []))}")
    print(f"Values: {', '.join(research.get('values', []))}")
    print(f"Size: {research.get('size', 'N/A')}")
    print(f"Industry: {research.get('industry', 'N/A')}")
    print(f"Funding Stage: {research.get('funding_stage', 'N/A')}")
    print(f"\nCulture: {research.get('culture', 'N/A')}")
    print(f"\nRecent News:")
    for news in research.get('recent_news', []):
        print(f"  - {news}")
    print(f"\nSources: {', '.join(research.get('sources', []))}")


def research_high_scoring():
    """Research companies for high-scoring jobs."""
    storage = Storage()
    jobs = storage.get_high_scoring_jobs(Config.MIN_SCORE_FOR_RESEARCH)
    
    if not jobs:
        print("No high-scoring jobs to research")
        return
    
    print(f"🔍 Researching {len(jobs)} high-scoring companies...")
    
    researcher = CompanyResearcher()
    researched_companies = set()
    
    for job in jobs:
        company = job.get("company", "")
        if not company or company in researched_companies:
            continue
        
        researched_companies.add(company)
        try:
            research = researcher.research_company(company)
            job["company_research"] = research
            
            # Save updated job
            job_file = Config.DATA_DIR / f"{job['id']}.json"
            import json
            with open(job_file, "w") as f:
                json.dump(job, f, indent=2)
            
            print(f"✅ Researched: {company}")
        except Exception as e:
            print(f"❌ Error researching {company}: {e}")
            continue
    
    print(f"\n✨ Researched {len(researched_companies)} companies")


def generate_materials(job_id: str = None):
    """Generate cover letters and resume highlights for jobs."""
    storage = Storage()
    
    if job_id:
        job = storage.get_job(job_id)
        if not job:
            print(f"Job {job_id} not found")
            return
        jobs = [job]
    else:
        # Generate for high-scoring jobs
        jobs = storage.get_high_scoring_jobs(Config.MIN_SCORE_FOR_NOTIFICATION)
    
    if not jobs:
        print("No jobs found for material generation")
        return
    
    # Load resume
    resume_parser = ResumeParser()
    try:
        resume_data = resume_parser.parse_resume()
    except Exception as e:
        print(f"❌ Error loading resume: {e}")
        return
    
    generator = MaterialGenerator(resume_data)
    
    print(f"📝 Generating materials for {len(jobs)} jobs...")
    
    for job in jobs:
        try:
            company_research = job.get("company_research")
            
            # Generate cover letter
            cover_letter = generator.generate_cover_letter(job, company_research)
            cover_letter_path = generator.save_cover_letter(job["id"], cover_letter)
            
            # Generate resume highlights
            highlights = generator.generate_resume_highlights(job)
            highlights_path = generator.save_resume_highlights(job["id"], highlights)
            
            print(f"✅ Generated materials for: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"   Cover letter: {cover_letter_path}")
            print(f"   Highlights: {highlights_path}")
        except Exception as e:
            print(f"❌ Error generating materials for job {job.get('id', 'Unknown')}: {e}")
            continue
    
    print(f"\n✨ Generated materials for {len(jobs)} jobs")


def refresh_resume():
    """Refresh resume data from Google Docs."""
    print("🔄 Refreshing resume data...")
    
    resume_parser = ResumeParser()
    try:
        resume_data = resume_parser.parse_resume(force_refresh=True)
        print("✅ Resume data refreshed")
        print(f"   Skills: {len(resume_data.get('skills', []))} skills")
        print(f"   Experience: {resume_data.get('experience_years', 0)} years")
        print(f"   Level: {resume_data.get('experience_level', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error refreshing resume: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Job Application Assistant")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check emails
    subparsers.add_parser("check", help="Check Gmail for new job alerts")
    
    # Score jobs
    subparsers.add_parser("score", help="Score all unscored jobs")
    
    # Review jobs
    review_parser = subparsers.add_parser("review", help="Review jobs")
    review_parser.add_argument("--min-score", type=int, help="Minimum score filter")
    
    # Research company
    research_parser = subparsers.add_parser("research", help="Research a company")
    research_parser.add_argument("company", help="Company name to research")
    
    # Research high-scoring
    subparsers.add_parser("research-high", help="Research companies for high-scoring jobs")
    
    # Generate materials
    gen_parser = subparsers.add_parser("generate", help="Generate cover letters and resume highlights")
    gen_parser.add_argument("--job-id", help="Specific job ID to generate materials for")
    
    # Refresh resume
    subparsers.add_parser("refresh-resume", help="Refresh resume data from Google Docs")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Execute command
    try:
        if args.command == "check":
            check_emails()
        elif args.command == "score":
            score_jobs()
        elif args.command == "review":
            review_jobs(args.min_score)
        elif args.command == "research":
            research_company(args.company)
        elif args.command == "research-high":
            research_high_scoring()
        elif args.command == "generate":
            generate_materials(args.job_id)
        elif args.command == "refresh-resume":
            refresh_resume()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

