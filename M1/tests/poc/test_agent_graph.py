
import os
import sys
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

class PoCAgentState(TypedDict):
    session_id: str
    candidate_id: str
    candidate_name: str
    candidate_skills: List[str]
    candidate_projects: List[Dict[str, Any]]
    candidate_education: Dict[str, Any]
    target_job: Dict[str, Any]
    match_report: Optional[Dict[str, Any]]
    skill_gap_report: Optional[Dict[str, Any]]
    current_node: str
    execution_steps: int

def matching_agent_node(state: PoCAgentState) -> Dict[str, Any]:
    candidate_skills = set(s.lower() for s in state["candidate_skills"])
    job_reqs = state["target_job"].get("required_skills", [])
    
    matched_skills = []
    missing_skills = []

    for req in job_reqs:
        if req.lower() in candidate_skills:
            matched_skills.append(req)
        else:
            missing_skills.append(req)

    skill_match_ratio = len(matched_skills) / max(len(job_reqs), 1)
    
    project_text = " ".join(p.get("summary", "") for p in state["candidate_projects"]).lower()
    has_project_overlap = any(s.lower() in project_text for s in matched_skills)
    project_score = 90.0 if has_project_overlap else 60.0

    overall_score = int((skill_match_ratio * 60.0) + (project_score * 0.40))
    overall_score = max(0, min(100, overall_score))

    match_verdict = "STRONG_MATCH" if overall_score >= 80 else ("COMPETITIVE_MATCH" if overall_score >= 65 else "GAP_HEAVY")

    match_report = {
        "overall_match_score": overall_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": round(skill_match_ratio * 100, 1),
        "project_fit_rating": "HIGH" if has_project_overlap else "MODERATE",
        "verdict": match_verdict,
        "summary": f"Candidate possesses {len(matched_skills)}/{len(job_reqs)} core requirements. Missing skills: {', '.join(missing_skills)}."
    }

    return {
        "match_report": match_report,
        "current_node": "MatchingAgent",
        "execution_steps": state.get("execution_steps", 0) + 1,
    }

def skill_gap_agent_node(state: PoCAgentState) -> Dict[str, Any]:
    match_report = state.get("match_report", {})
    missing_skills = match_report.get("missing_skills", [])

    RESOURCE_DB = {
        "Docker": {
            "resource": "Docker Official Getting Started Lab & Container Handbook",
            "url": "https://docs.docker.com/get-started/",
            "est_hours": 6,
            "project_suggestion": "Containerize existing FastAPI task queue with multi-stage Dockerfile."
        },
        "Kubernetes": {
            "resource": "Kubernetes.io Interactive Tutorials & Minikube Basics",
            "url": "https://kubernetes.io/docs/tutorials/",
            "est_hours": 12,
            "project_suggestion": "Deploy containerized services as a local Kubernetes Deployment with ClusterIP service."
        },
        "Celery": {
            "resource": "Celery Project Official First Steps Guide",
            "url": "https://docs.celeryq.dev/",
            "est_hours": 5,
            "project_suggestion": "Integrate Celery distributed task queue with Redis broker for asynchronous background tasks."
        },
        "CI/CD": {
            "resource": "GitHub Actions Official Workflow Documentation",
            "url": "https://docs.github.com/actions",
            "est_hours": 4,
            "project_suggestion": "Add automated GitHub Actions workflow running pytest and linter on push."
        }
    }

    action_items = []
    total_hours = 0

    for skill in missing_skills:
        info = RESOURCE_DB.get(skill, {
            "resource": f"Official {skill} Documentation and Core Tutorials",
            "url": f"https://www.google.com/search?q={skill}+tutorial",
            "est_hours": 8,
            "project_suggestion": f"Build a prototype microservice demonstrating {skill} fundamentals."
        })
        action_items.append({
            "skill": skill,
            "priority": "HIGH" if skill in ("Docker", "Kubernetes") else "MEDIUM",
            "estimated_hours": info["est_hours"],
            "resource_title": info["resource"],
            "resource_url": info["url"],
            "actionable_project": info["project_suggestion"]
        })
        total_hours += info["est_hours"]

    roadmap_phases = [
        {
            "phase": "Week 1: Foundations",
            "focus": [item["skill"] for item in action_items[:2]],
            "target_outcome": "Complete basic syntax, local setup, and sandbox exercises."
        },
        {
            "phase": "Weeks 2-3: Hands-On Integration",
            "focus": [item["skill"] for item in action_items],
            "target_outcome": "Integrate technologies into existing portfolio repo and commit code."
        },
        {
            "phase": "Week 4: Mock Interview & Verification",
            "focus": ["Conceptual mastery and architectural trade-offs"],
            "target_outcome": "Demonstrate practical competency during technical mock interview."
        }
    ]

    skill_gap_report = {
        "severity": "MODERATE" if len(missing_skills) <= 2 else "SIGNIFICANT",
        "missing_skills_count": len(missing_skills),
        "total_estimated_study_hours": total_hours,
        "action_items": action_items,
        "roadmap_phases": roadmap_phases,
        "mentor_reassurance": "Missing qualifications are standard for student internships. Allocating 5–8 hours/week on these focused projects will close the gap before technical interviews."
    }

    return {
        "skill_gap_report": skill_gap_report,
        "current_node": "SkillGapAgent",
        "execution_steps": state.get("execution_steps", 0) + 1,
    }

def build_poc_agent_graph():
    workflow = StateGraph(PoCAgentState)

    workflow.add_node("matching_agent", matching_agent_node)
    workflow.add_node("skill_gap_agent", skill_gap_agent_node)

    workflow.add_edge(START, "matching_agent")
    workflow.add_edge("matching_agent", "skill_gap_agent")
    workflow.add_edge("skill_gap_agent", END)

    return workflow.compile()

def run_agent_graph_validation() -> dict:
    print("=" * 70)
    print("PoC 4: LangGraph Multi-Agent StateGraph Pipeline Validation")
    print("=" * 70)

    print("[*] Compiling LangGraph StateGraph (START -> matching_agent -> skill_gap_agent -> END)...")
    app = build_poc_agent_graph()
    print("[+] LangGraph compiled successfully.")

    initial_state: PoCAgentState = {
        "session_id": "session_test_901",
        "candidate_id": "cand_usr_44",
        "candidate_name": "Daksh Sharma",
        "candidate_skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Git", "SQL"],
        "candidate_projects": [
            {
                "title": "Distributed Task Queue",
                "summary": "Asynchronous background task worker in Python and Redis handling high-throughput queues."
            }
        ],
        "candidate_education": {
            "degree": "B.Tech Computer Science",
            "graduation_year": 2026,
            "gpa": 3.82
        },
        "target_job": {
            "title": "Backend Engineering Intern",
            "company": "CloudScale Systems",
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes"]
        },
        "match_report": None,
        "skill_gap_report": None,
        "current_node": "START",
        "execution_steps": 0,
    }

    print(f"\n[*] Invoking multi-agent pipeline for candidate: {initial_state['candidate_name']}")
    final_state = app.invoke(initial_state)
    print("[+] Pipeline execution finished.")

    match_report = final_state.get("match_report", {})
    gap_report = final_state.get("skill_gap_report", {})

    print("\n[*] Agent 1 (Matching Agent) Output Summary:")
    print(f"    - Overall Match Score: {match_report.get('overall_match_score')}/100")
    print(f"    - Matched Skills: {match_report.get('matched_skills')}")
    print(f"    - Missing Skills: {match_report.get('missing_skills')}")
    print(f"    - Verdict: {match_report.get('verdict')}")

    print("\n[*] Agent 2 (Skill Gap Agent) Output Summary:")
    print(f"    - Gap Severity: {gap_report.get('severity')}")
    print(f"    - Total Remediation Hours: {gap_report.get('total_estimated_study_hours')} hours")
    print(f"    - Action Items Planned: {len(gap_report.get('action_items', []))} items")
    for item in gap_report.get("action_items", []):
        print(f"      • {item['skill']} ({item['priority']} Priority): {item['actionable_project']}")

    print("\n[*] Running State Machine & Schema Assertions:")

    assert final_state["execution_steps"] == 2, f"Expected 2 steps, got {final_state['execution_steps']}"
    assert final_state["current_node"] == "SkillGapAgent"
    print("  [✓] Execution step counter incremented accurately (2 node hops).")

    assert match_report.get("overall_match_score") is not None
    assert 60 <= match_report["overall_match_score"] <= 90
    assert "Python" in match_report["matched_skills"]
    assert "FastAPI" in match_report["matched_skills"]
    assert "Docker" in match_report["missing_skills"]
    assert "Kubernetes" in match_report["missing_skills"]
    print("  [✓] Matching Agent correctly identified matched (Python, FastAPI, Redis, PostgreSQL) and missing skills (Docker, Kubernetes).")

    assert gap_report.get("total_estimated_study_hours", 0) > 0
    assert len(gap_report.get("action_items", [])) == 2
    assert len(gap_report.get("roadmap_phases", [])) == 3
    print("  [✓] Skill Gap Agent correctly generated time-boxed 3-phase remediation roadmap.")

    print("\n[+] SUCCESS: LangGraph multi-agent pipeline validation passed!")

    return {
        "status": "PASSED",
        "execution_steps": final_state["execution_steps"],
        "match_score": match_report["overall_match_score"],
        "matched_skills": match_report["matched_skills"],
        "missing_skills": match_report["missing_skills"],
        "remediation_hours": gap_report["total_estimated_study_hours"],
    }

if __name__ == "__main__":
    results = run_agent_graph_validation()
    print("\nTest Result Summary:", results)
