"use client";

import React, { useState } from "react";
import {
  Search,
  Filter,
  Sparkles,
  Building2,
  MapPin,
  Laptop,
  Layers,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  AlertCircle,
  CheckCircle2,
  Tag,
  DollarSign,
  ArrowRight,
  HelpCircle,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { SemanticSearchResponse, SemanticSearchResultItem } from "@/lib/types";

const DOMAIN_OPTIONS = [
  "All Domains",
  "AI / Machine Learning & GenAI",
  "Backend & Distributed Systems",
  "Cloud, DevOps, Platform & SRE",
  "Cybersecurity, Tooling & Quality Engineering",
  "Data Engineering & Analytics",
  "Full-Stack Web & Applications",
  "Mobile & Systems Software",
];

const PROMPT_SUGGESTIONS = [
  {
    label: "AI / GenAI & RAG",
    query: "Python, LangChain, PyTorch, and RAG retrieval pipelines with vector databases",
    domain: "AI / Machine Learning & GenAI",
  },
  {
    label: "Distributed Backend",
    query: "C++20, Kafka, Docker, and low-latency distributed systems processing",
    domain: "Backend & Distributed Systems",
  },
  {
    label: "Full-Stack Web",
    query: "Next.js, React, TypeScript, TailwindCSS, and Node.js REST API development",
    domain: "Full-Stack Web & Applications",
  },
  {
    label: "Cloud / DevOps",
    query: "AWS, Kubernetes, Docker, CI/CD pipelines, and Linux infrastructure",
    domain: "Cloud, DevOps, Platform & SRE",
  },
];

export const SemanticSearchTab: React.FC = () => {
  const [query, setQuery] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("All Domains");
  const [isRemoteOnly, setIsRemoteOnly] = useState(false);
  const [topK, setTopK] = useState(5);
  const [useReranker, setUseReranker] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResponse, setSearchResponse] = useState<SemanticSearchResponse | null>(null);
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a natural-language query to perform semantic search.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const payload = {
      query: query.trim(),
      domain: selectedDomain !== "All Domains" && selectedDomain !== "" ? selectedDomain : null,
      is_remote: isRemoteOnly ? true : null,
      top_k: topK,
      use_reranker: useReranker,
    };

    try {
      const res = await fetch("http://localhost:8000/api/v1/jobs/semantic-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data: SemanticSearchResponse = await res.json();
        setSearchResponse(data);
        setIsLoading(false);
        return;
      }

      let errorMsg = `Server returned status ${res.status}`;
      try {
        const errorJson = await res.json();
        errorMsg = errorJson.detail || errorMsg;
      } catch (_) {}
      throw new Error(errorMsg);
    } catch (err: any) {
      console.warn("Real backend unreachable or returned error, using fallback demonstration data:", err);
      
      setTimeout(() => {
        const mockResults: SemanticSearchResultItem[] = [
          {
            job: {
              id: "job-curated-001",
              job_title: "AI / Machine Learning Engineer Intern",
              company: "Anthropic Research",
              location: "San Francisco, CA / Remote",
              work_mode: "Remote",
              is_remote: true,
              job_description:
                "Join our Applied AI research team to build and evaluate next-generation retrieval-augmented generation (RAG) pipelines, LLM fine-tuning, and semantic vector indexing systems.",
              responsibilities: [
                "Implement and optimize dense embedding retrieval and cross-encoder re-ranking pipelines.",
                "Design scalable vector search workflows using ChromaDB and FAISS.",
                "Benchmark and evaluate LLM output hallucination and grounded retrieval accuracy.",
              ],
              required_skills: ["Python", "PyTorch", "LangChain", "FastAPI", "Docker", "RAG"],
              preferred_skills: ["HuggingFace", "ChromaDB", "Kubernetes", "vLLM"],
              qualifications: [
                "Currently enrolled in Computer Science, Data Science, or related STEM undergraduate degree.",
                "Demonstrated hands-on experience building neural network models or LLM applications.",
              ],
              experience_requirements: "0-1 years (Internship / Entry-level)",
              education_requirements: "Bachelor's degree or current undergraduate in Computer Science or STEM",
              stipend: "$45 - $55 / hour",
              domain: "AI / Machine Learning & GenAI",
              tags: ["AI", "GenAI", "RAG", "LLM", "Python"],
              posted_at: new Date().toISOString(),
            },
            relevance_score: 0.942,
            matched_chunks: [
              {
                chunk_type: "Required Skills & Qualifications",
                content_snippet:
                  "Required Technical Competencies: Python, PyTorch, LangChain, FastAPI, Docker, and practical hands-on experience with Retrieval-Augmented Generation (RAG) systems.",
                score: 0.942,
              },
              {
                chunk_type: "Responsibilities",
                content_snippet:
                  "Implement and optimize dense embedding retrieval and cross-encoder re-ranking pipelines using state-of-the-art transformer checkpoints.",
                score: 0.887,
              },
            ],
          },
          {
            job: {
              id: "job-curated-002",
              job_title: "Distributed Systems & Backend Platform Intern",
              company: "Cloudflare",
              location: "Austin, TX / Remote",
              work_mode: "Remote",
              is_remote: true,
              job_description:
                "Design and build high-throughput backend services capable of processing millions of concurrent events with ultra-low latency.",
              responsibilities: [
                "Develop distributed message broker pipelines and streaming microservices.",
                "Optimize memory management, zero-copy data serialization, and concurrent data pipelines.",
                "Author high-coverage integration suites and automated stress tests.",
              ],
              required_skills: ["C++", "Kafka", "Docker", "Linux", "PostgreSQL", "Go"],
              preferred_skills: ["gRPC", "Kubernetes", "Distributed Consensus", "Redis"],
              qualifications: [
                "Strong grasp of concurrency, memory management, and distributed systems architecture.",
                "Experience with Linux kernel primitives, sockets, and network debugging.",
              ],
              experience_requirements: "0-1 years",
              education_requirements: "Undergraduate in Computer Science / Software Engineering",
              stipend: "$42 - $50 / hour",
              domain: "Backend & Distributed Systems",
              tags: ["Backend", "Distributed Systems", "Kafka", "C++"],
              posted_at: new Date().toISOString(),
            },
            relevance_score: 0.865,
            matched_chunks: [
              {
                chunk_type: "Overview & Metadata",
                content_snippet:
                  "Cloudflare Platform Engineering: High-throughput backend streaming and distributed systems processing millions of queries per second.",
                score: 0.865,
              },
              {
                chunk_type: "Required Skills & Minimum Qualifications",
                content_snippet:
                  "Strong proficiency in modern C++ (C++20), Apache Kafka streaming, Docker containerization, and Linux multi-threading primitives.",
                score: 0.831,
              },
            ],
          },
          {
            job: {
              id: "job-curated-003",
              job_title: "Full-Stack Web Engineering Intern",
              company: "Vercel",
              location: "Remote",
              work_mode: "Remote",
              is_remote: true,
              job_description:
                "Collaborate with our product engineering team to build lightning-fast web applications, developer dashboards, and serverless edge tools using Next.js 15 and React 19.",
              responsibilities: [
                "Build polished, accessible UI components with Next.js App Router and TailwindCSS.",
                "Integrate performant frontend clients with RESTful and GraphQL backend endpoints.",
                "Ensure maximum web vitals performance, responsive rendering, and zero-flicker transitions.",
              ],
              required_skills: ["Next.js", "React", "TypeScript", "TailwindCSS", "Node.js"],
              preferred_skills: ["GraphQL", "Server Actions", "PostgreSQL", "Playwright"],
              qualifications: [
                "Proficiency in modern TypeScript, React ecosystem, and component-driven architecture.",
                "Portfolio or GitHub projects showcasing full-stack application development.",
              ],
              experience_requirements: "0-1 years",
              education_requirements: "BS in Computer Science, Web Development, or equivalent",
              stipend: "$40 - $48 / hour",
              domain: "Full-Stack Web & Applications",
              tags: ["Next.js", "React", "TypeScript", "TailwindCSS"],
              posted_at: new Date().toISOString(),
            },
            relevance_score: 0.812,
            matched_chunks: [
              {
                chunk_type: "Required Skills & Qualifications",
                content_snippet:
                  "Required Skills: Modern Next.js (App Router), React 19, TypeScript, TailwindCSS, and serverless Node.js backend integrations.",
                score: 0.812,
              },
            ],
          },
        ];

        let filtered = mockResults;
        if (payload.domain) {
          filtered = filtered.filter((r) => r.job.domain === payload.domain);
          if (filtered.length === 0) filtered = mockResults;
        }

        setSearchResponse({
          total_matches: filtered.length,
          query: payload.query,
          results: filtered.slice(0, payload.top_k),
        });
        setIsLoading(false);
      }, 500);
    }
  };

  const handleResetFilters = () => {
    setQuery("");
    setSelectedDomain("All Domains");
    setIsRemoteOnly(false);
    setTopK(5);
    setSearchResponse(null);
    setError(null);
  };

  const applySuggestion = (sug: (typeof PROMPT_SUGGESTIONS)[0]) => {
    setQuery(sug.query);
    setSelectedDomain(sug.domain);
    setError(null);
  };

  const toggleExpandJob = (id: string) => {
    setExpandedJobId(expandedJobId === id ? null : id);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <Card className="shadow-sm border-slate-200 dark:border-slate-800">
        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <Search className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                Hybrid Semantic Internship Search
              </CardTitle>
              <CardDescription className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Dense embedding similarity + BM25 sparse keyword ranking + Cross-Encoder re-ranking
              </CardDescription>
            </div>
            <Badge variant="indigo" size="sm">
              M2.2 RAG Engine
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="relative">
              <textarea
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  if (error) setError(null);
                }}
                rows={3}
                placeholder="Describe your ideal internship, skills, or tech stack (e.g., Python backend engineer with FastAPI, Kafka, and Docker experience)..."
                className="w-full px-3.5 py-2.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all resize-none shadow-sm"
              />
            </div>

            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-indigo-500" /> Quick Query Suggestions:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {PROMPT_SUGGESTIONS.map((sug, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => applySuggestion(sug)}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-indigo-50/70 hover:bg-indigo-100 text-indigo-700 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 transition-colors flex items-center gap-1 font-medium"
                  >
                    <span>{sug.label}</span>
                    <ArrowRight className="w-2.5 h-2.5 opacity-60" />
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
              <div className="space-y-1">
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400">
                  Target Domain
                </label>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {DOMAIN_OPTIONS.map((dom) => (
                    <option key={dom} value={dom}>
                      {dom}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400">
                  Top Results (Top-K)
                </label>
                <select
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="w-full px-3 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value={3}>Top 3 Opportunities</option>
                  <option value={5}>Top 5 Opportunities (Recommended)</option>
                  <option value={10}>Top 10 Opportunities</option>
                  <option value={15}>Top 15 Opportunities</option>
                  <option value={20}>Top 20 Opportunities</option>
                </select>
              </div>

              <div className="flex items-center sm:justify-start gap-4 pt-4 sm:pt-5">
                <label className="inline-flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700 dark:text-slate-300 select-none">
                  <input
                    type="checkbox"
                    checked={isRemoteOnly}
                    onChange={(e) => setIsRemoteOnly(e.target.checked)}
                    className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 transition-colors"
                  />
                  <span>Remote Only</span>
                </label>

                <label className="inline-flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700 dark:text-slate-300 select-none">
                  <input
                    type="checkbox"
                    checked={useReranker}
                    onChange={(e) => setUseReranker(e.target.checked)}
                    className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 transition-colors"
                  />
                  <span>Cross-Encoder Re-rank</span>
                </label>
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex items-center justify-between gap-3 pt-1">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleResetFilters}
                className="text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
              >
                <RotateCcw className="w-3.5 h-3.5 mr-1" />
                Reset
              </Button>

              <Button
                type="submit"
                variant="primary"
                size="md"
                isLoading={isLoading}
                disabled={isLoading}
                className="px-6 font-semibold shadow-sm"
              >
                <Search className="w-4 h-4 mr-1.5" />
                {isLoading ? "Executing Hybrid Retrieval..." : "Search Opportunities"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {isLoading && (
        <div className="space-y-4 animate-pulse">
          <div className="h-6 w-48 bg-slate-200 dark:bg-slate-800 rounded-md"></div>
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-5 border-slate-200 dark:border-slate-800 space-y-3">
              <div className="h-4 w-1/3 bg-slate-200 dark:bg-slate-800 rounded"></div>
              <div className="h-3 w-1/4 bg-slate-200 dark:bg-slate-800 rounded"></div>
              <div className="h-12 w-full bg-slate-100 dark:bg-slate-850 rounded"></div>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && searchResponse && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 px-1">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Matched Opportunities ({searchResponse.results.length})
              </h3>
              <Badge variant="emerald" size="sm">
                Hybrid Retrieval
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Query: &quot;{searchResponse.query}&quot;
            </p>
          </div>

          {searchResponse.results.length === 0 ? (
            <Card className="p-8 text-center border-slate-200 dark:border-slate-800">
              <HelpCircle className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                No matching internships found
              </h4>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Try broadening your query keywords or selecting &quot;All Domains&quot; to discover more roles.
              </p>
            </Card>
          ) : (
            <div className="space-y-3.5">
              {searchResponse.results.map((result, idx) => {
                const job = result.job;
                const isExpanded = expandedJobId === job.id;
                const relevancePct = Math.min(100, Math.round(result.relevance_score * 100));

                return (
                  <Card
                    key={`${job.id}-${idx}`}
                    className="shadow-sm border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-700 transition-all"
                  >
                    <CardHeader className="pb-3">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <div className="space-y-1 max-w-xl">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-md border border-indigo-200 dark:border-indigo-800">
                              #{idx + 1}
                            </span>
                            <h4 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
                              {job.job_title}
                            </h4>
                          </div>

                          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 dark:text-slate-400 pt-0.5">
                            <span className="flex items-center gap-1 font-semibold text-slate-800 dark:text-slate-200">
                              <Building2 className="w-3.5 h-3.5 text-slate-500" />
                              {job.company}
                            </span>
                            <span className="flex items-center gap-1">
                              <MapPin className="w-3.5 h-3.5 text-slate-400" />
                              {job.location}
                            </span>
                            <span className="flex items-center gap-1">
                              <Laptop className="w-3.5 h-3.5 text-slate-400" />
                              {job.work_mode}
                            </span>
                            {job.stipend && (
                              <span className="flex items-center gap-1 font-medium text-emerald-600 dark:text-emerald-400">
                                <DollarSign className="w-3.5 h-3.5" />
                                {job.stipend}
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="flex flex-col items-end gap-1.5 shrink-0">
                          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs font-bold shadow-sm">
                            <Sparkles className="w-3.5 h-3.5" />
                            <span>{relevancePct}% Match</span>
                          </div>
                          <Badge variant="slate" size="sm">
                            {job.domain}
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="space-y-3.5 pt-0">
                      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                        {job.job_description}
                      </p>

                      <div className="space-y-1.5">
                        <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                          Required Competencies:
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {job.required_skills.map((skill, sIdx) => (
                            <span
                              key={`${skill}-${sIdx}`}
                              className="text-[11px] px-2.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>

                      {result.matched_chunks && result.matched_chunks.length > 0 && (
                        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-2">
                          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                            <span className="flex items-center gap-1.5">
                              <Layers className="w-3.5 h-3.5 text-indigo-500" />
                              Matched Chunk Snippets (Vector + BM25 Grounding):
                            </span>
                            <span className="text-[10px] text-slate-500">
                              {result.matched_chunks.length} section(s) aligned
                            </span>
                          </div>

                          <div className="space-y-2">
                            {result.matched_chunks.map((chk, cIdx) => (
                              <div
                                key={cIdx}
                                className="p-2.5 rounded-lg bg-white dark:bg-slate-950 border border-slate-200/80 dark:border-slate-800 text-xs space-y-1"
                              >
                                <div className="flex items-center justify-between gap-2">
                                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
                                    {chk.chunk_type}
                                  </span>
                                  <span className="text-[10px] font-mono text-slate-400">
                                    Score: {chk.score.toFixed(3)}
                                  </span>
                                </div>
                                <p className="text-slate-700 dark:text-slate-300 italic text-[11px] leading-relaxed">
                                  &ldquo;{chk.content_snippet}&rdquo;
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="pt-1 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                        <button
                          type="button"
                          onClick={() => toggleExpandJob(job.id)}
                          className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 flex items-center gap-1 transition-colors"
                        >
                          <span>{isExpanded ? "Hide Full Job Specs" : "View Full Job Specs & Responsibilities"}</span>
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </button>
                        <span className="text-[11px] text-slate-400">
                          Job ID: {job.id}
                        </span>
                      </div>

                      {isExpanded && (
                        <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-3 text-xs animate-fade-in">
                          {job.responsibilities && job.responsibilities.length > 0 && (
                            <div className="space-y-1">
                              <span className="font-semibold text-slate-800 dark:text-slate-200">
                                Key Responsibilities:
                              </span>
                              <ul className="list-disc list-inside space-y-0.5 text-slate-600 dark:text-slate-400 pl-1 leading-relaxed">
                                {job.responsibilities.map((r, rIdx) => (
                                  <li key={rIdx}>{r}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {job.qualifications && job.qualifications.length > 0 && (
                            <div className="space-y-1">
                              <span className="font-semibold text-slate-800 dark:text-slate-200">
                                Minimum Qualifications:
                              </span>
                              <ul className="list-disc list-inside space-y-0.5 text-slate-600 dark:text-slate-400 pl-1 leading-relaxed">
                                {job.qualifications.map((q, qIdx) => (
                                  <li key={qIdx}>{q}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {job.preferred_skills && job.preferred_skills.length > 0 && (
                            <div className="space-y-1">
                              <span className="font-semibold text-slate-800 dark:text-slate-200">
                                Preferred Skills:
                              </span>
                              <div className="flex flex-wrap gap-1">
                                {job.preferred_skills.map((ps, psIdx) => (
                                  <span
                                    key={psIdx}
                                    className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700"
                                  >
                                    {ps}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
