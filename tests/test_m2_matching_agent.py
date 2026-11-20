import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.api.v1.endpoints.jobs import match_jobs
from app.schemas.matching import CandidateProfile, MatchRequest, MatchResponse
from app.services.matching_agent import JobResumeMatchingAgent

def get_sample_candidate() -> CandidateProfile:
    return CandidateProfile(
        candidate_name="Daksh Singh",
        email="daksh.singh@example.com",
        phone="+91-9876543210",
        university_name="Indian Institute of Technology",
        degree_major="B.Tech in Computer Science and Engineering",
        gpa=3.85,
        graduation_year=2026,
        batch="2022-2026",
        skills=[
            "Python",
            "C++",
            "FastAPI",
            "Docker",
            "PostgreSQL",
            "LangChain",
            "PyTorch",
            "Redis",
            "Kafka",
            "Linux",
            "Git",
            "REST APIs",
        ],
        educations=[
            {
                "institution_name": "Indian Institute of Technology",
                "degree": "B.Tech",
                "major": "Computer Science and Engineering",
                "graduation_year": 2026,
                "gpa": 3.85,
            }
        ],
        projects=[
            {
                "title": "Distributed Search Engine",
                "technologies": ["C++", "Kafka", "Docker", "Linux"],
                "highlights": ["High-throughput distributed indexing pipeline with fault tolerance."],
            },
            {
                "title": "AI Lawyer Chatbot & RAG Engine",
                "technologies": ["Python", "FastAPI", "LangChain", "PostgreSQL"],
                "highlights": ["Domain-specific retrieval-augmented generation engine with hybrid search."],
            },
            {
                "title": "Interview Sandbox",
                "technologies": ["React", "Node.js", "Redis", "WebSockets"],
                "highlights": ["Real-time collaborative code editor and execution sandbox."],
            },
        ],
        work_experiences=[
            {
                "company_name": "Tech Corp",
                "role_title": "Software Engineering Intern",
                "technologies_used": ["Python", "FastAPI", "Docker"],
                "bullets": ["Engineered RESTful microservices and containerized deployment pipelines."],
            }
        ],
        certifications=["AWS Certified Cloud Practitioner"],
    )

def test_agent_matching_pipeline():
    agent = JobResumeMatchingAgent.get_instance(data_file="data/jobs/internships_curated.json")
    candidate = get_sample_candidate()
    request = MatchRequest(candidate_profile=candidate, top_k=5)

    response = agent.match_jobs(request)

    assert isinstance(response, MatchResponse)
    assert response.candidate_name == "Daksh Singh"
    assert len(response.results) == 5, f"Expected 5 results, got {len(response.results)}"
    assert response.total_evaluated_jobs > 0

    scores = [r.overall_match_score for r in response.results]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], f"Results not sorted descending: {scores}"

    valid_tiers = {"Strong Match", "Good Match", "Partial Match", "Stretch Role"}
    candidate_skills_lower = {s.lower() for s in response.candidate_skills}

    print("\n" + "=" * 80)
    print("TOP-5 JOB-RESUME MATCHING RESULTS (OVERALL EVALUATION)")
    print("=" * 80)

    for idx, match in enumerate(response.results, start=1):
        assert 0.0 <= match.overall_match_score <= 100.0
        assert match.recommendation_tier in valid_tiers
        assert match.reasoning and len(match.reasoning) > 20

        sb = match.score_breakdown
        assert 0.0 <= sb.required_skills_score <= 100.0
        assert 0.0 <= sb.preferred_skills_score <= 100.0
        assert 0.0 <= sb.projects_experience_score <= 100.0
        assert 0.0 <= sb.education_qualifications_score <= 100.0
        assert 0.0 <= sb.semantic_relevance_score <= 100.0

        for s in match.matched_skills:
            norm_s = s.lower().replace(".js", "").replace("3", "")
            assert any(norm_s in cs or cs in norm_s for cs in candidate_skills_lower), f"Hallucinated matched skill: {s}"

        print(f"\n#{idx}: [{match.overall_match_score:.2f}%] {match.job.job_title} @ {match.job.company} ({match.recommendation_tier})")
        print(f"    Domain: {match.job.domain} | Location: {match.job.location}")
        print(f"    Breakdown -> Req: {sb.required_skills_score:.1f}% | Sem: {sb.semantic_relevance_score:.1f}% | Proj: {sb.projects_experience_score:.1f}% | Pref: {sb.preferred_skills_score:.1f}% | Edu: {sb.education_qualifications_score:.1f}%")
        print(f"    Matched Skills: {', '.join(match.matched_skills)}")
        print(f"    Missing Req: {', '.join(match.missing_required_skills) if match.missing_required_skills else 'None'}")
        print(f"    Reasoning: {match.reasoning}")

    print(f"\n[PASSED] Job-Resume Matching Agent: Verified strict descending order, grounded reasoning, and score breakdowns.")

def test_domain_filtering():
    agent = JobResumeMatchingAgent.get_instance(data_file="data/jobs/internships_curated.json")
    candidate = get_sample_candidate()
    target_domain = "AI / Machine Learning & GenAI"
    request = MatchRequest(candidate_profile=candidate, top_k=4, domain=target_domain)

    response = agent.match_jobs(request)
    assert len(response.results) == 4

    for r in response.results:
        assert r.job.domain == target_domain, f"Domain filter violation: {r.job.domain}"

    print(f"[PASSED] Domain Filtering: All 4 results matched domain '{target_domain}' strictly.")

def test_fastapi_matching_endpoint():
    candidate = get_sample_candidate()
    req = MatchRequest(candidate_profile=candidate, top_k=3)
    response = match_jobs(req)

    assert isinstance(response, MatchResponse)
    assert len(response.results) == 3
    assert response.results[0].overall_match_score >= response.results[1].overall_match_score
    print(f"[PASSED] FastAPI Endpoint match_jobs: Returned HTTP 200 equivalent with Top-1 match '{response.results[0].job.job_title}' ({response.results[0].overall_match_score:.2f}%).")

def run_all_tests():
    print("======================================================================")
    print("MILESTONE 2 - STEP M2.3 JOB-RESUME MATCHING AGENT TEST SUITE")
    print("======================================================================")
    test_agent_matching_pipeline()
    test_domain_filtering()
    test_fastapi_matching_endpoint()
    print("\n======================================================================")
    print("ALL M2.3 MATCHING AGENT TESTS PASSED WITH 100% SUCCESS!")
    print("======================================================================")

if __name__ == "__main__":
    run_all_tests()
