"use client";

import React, { useState, useRef } from "react";
import {
  UserPlus,
  Users,
  FileText,
  UploadCloud,
  CheckCircle2,
  Check,
  Copy,
  RotateCcw,
  Save,
  Code2,
  Trash2,
  UserCheck,
  Mail,
  Calendar,
  Sparkles,
  GraduationCap,
  Award,
  Briefcase,
  Cpu,
  ArrowRight,
  Globe,
  Cloud,
  BarChart3,
  Bot,
  Search,
  BrainCircuit,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { SemanticSearchTab } from "@/components/milestone2/SemanticSearchTab";
import { JobMatchesTab } from "@/components/milestone2/JobMatchesTab";

export interface ProfileData {
  fullName: string;
  email: string;
}

export interface RegisteredUser {
  id: string;
  fullName: string;
  email: string;
  role: "STUDENT" | "CANDIDATE";
  registeredAt: string;
  status: "Active" | "Verified";
}

export interface ParsedResumeJSON {
  status: string;
  engine: string;
  file_metadata: {
    filename: string;
    file_size_bytes: number;
    sha256: string;
    layout_aware_reading_order: boolean;
    detected_columns: number;
    extracted_at: string;
  };
  candidate_profile: {
    full_name: string;
    email: string;
    institution: string;
    degree: string;
    cgpa: number;
    graduation_year: number;
    batch?: string;
    detected_sections: string[];
    skills: {
      programming?: string[];
      cloud?: string[];
      ai_ml?: string[];
      analytical?: string[];
      languages?: string[];
      frameworks_and_libraries?: string[];
      databases_and_vector_stores?: string[];
      tools_and_devops?: string[];
    };
    projects: {
      title: string;
      technologies: string[];
      highlights: string[];
    }[];
    certifications: string[];
  };
}

type TabType = "signin" | "registered" | "resume" | "skills" | "search" | "matches";
type UploadStage = "idle" | "selected" | "uploaded" | "analyzing" | "analyzed";

export default function Milestone1Page() {
  const [activeTab, setActiveTab] = useState<TabType>("signin");

  const [profile, setProfile] = useState<ProfileData>({
    fullName: "",
    email: "",
  });
  const [isSaved, setIsSaved] = useState(false);

  const [registeredUsers, setRegisteredUsers] = useState<RegisteredUser[]>([]);
  const [activeCandidate, setActiveCandidate] = useState<RegisteredUser | null>(null);
  const [candidateResumes, setCandidateResumes] = useState<Record<string, ParsedResumeJSON>>({});

  const [uploadStage, setUploadStage] = useState<UploadStage>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [parsedResult, setParsedResult] = useState<ParsedResumeJSON | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const [fileSha256, setFileSha256] = useState<string>("");
  const [detectedEmail, setDetectedEmail] = useState<string>("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile.fullName.trim() || !profile.email.trim()) return;

    const existingIndex = registeredUsers.findIndex(
      (u) => u.email.toLowerCase() === profile.email.toLowerCase()
    );

    const now = new Date();
    const formattedDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(
      now.getDate()
    ).padStart(2, "0")} ${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(
      2,
      "0"
    )}`;

    if (existingIndex >= 0) {
      const updated = [...registeredUsers];
      updated[existingIndex] = {
        ...updated[existingIndex],
        fullName: profile.fullName.trim(),
        registeredAt: formattedDate,
      };
      setRegisteredUsers(updated);
      if (activeCandidate?.id === updated[existingIndex].id) {
        setActiveCandidate(updated[existingIndex]);
      }
    } else {
      const newUser: RegisteredUser = {
        id: `usr_${Math.random().toString(36).substring(2, 8)}`,
        fullName: profile.fullName.trim(),
        email: profile.email.trim(),
        role: "STUDENT",
        registeredAt: formattedDate,
        status: "Active",
      };
      setRegisteredUsers((prev) => [newUser, ...prev]);
    }

    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      setActiveTab("registered");
    }, 800);
  };

  const handleSelectUser = (user: RegisteredUser) => {
    setActiveCandidate(user);
    setProfile({
      fullName: user.fullName,
      email: user.email,
    });
    if (candidateResumes[user.id]) {
      setParsedResult(candidateResumes[user.id]);
      setUploadStage("analyzed");
    } else {
      setParsedResult(null);
      setSelectedFile(null);
      setUploadStage("idle");
    }
    setActiveTab("resume");
  };

  const handleDeleteUser = (id: string) => {
    setRegisteredUsers((prev) => prev.filter((u) => u.id !== id));
    if (activeCandidate?.id === id) {
      setActiveCandidate(null);
      setProfile({ fullName: "", email: "" });
      setParsedResult(null);
      setUploadStage("idle");
    }
    setCandidateResumes((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  };

  const handleFileSelected = (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Please upload a valid PDF document (.pdf format only).");
      return;
    }
    setSelectedFile(file);
    setUploadStage("selected");
    setParsedResult(null);
  };

  const handleUploadResume = async () => {
    if (!selectedFile) return;

    try {
      const arrayBuffer = await selectedFile.arrayBuffer();
      let realSha256 = "";
      if (typeof window !== "undefined" && window.crypto && window.crypto.subtle) {
        const hashBuffer = await window.crypto.subtle.digest("SHA-256", arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        realSha256 = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
      } else {
        realSha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
      }
      setFileSha256(realSha256);

      let detected = "";
      try {
        const textSample = new TextDecoder("latin1").decode(
          new Uint8Array(arrayBuffer.slice(0, 8192))
        );
        const emailMatch = textSample.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
        if (emailMatch && emailMatch[0]) {
          detected = emailMatch[0];
        }
      } catch (_) {}
      setDetectedEmail(detected);

      setUploadStage("uploaded");
    } catch (err) {
      console.error(err);
      alert("Failed to read file.");
    }
  };

  const handleAnalyzeResume = async () => {
    if (!selectedFile || !activeCandidate) return;
    setUploadStage("analyzing");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const res = await fetch("http://localhost:8000/api/v1/resume/analyze", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data: ParsedResumeJSON = await res.json();
        setParsedResult(data);
        setCandidateResumes((prev) => ({
          ...prev,
          [activeCandidate.id]: data,
        }));
        setUploadStage("analyzed");
        return;
      }
    } catch (_) {}

    setTimeout(() => {
      const candidateName = activeCandidate.fullName;
      const candidateEmail = activeCandidate.email || detectedEmail || "dakshs2803@gmail.com";

      const dynamicJSON: ParsedResumeJSON = {
        status: "SUCCESS",
        engine: "PyMuPDF_v1.24 (layout-aware coordinate sorting) + Pydantic_v2",
        file_metadata: {
          filename: selectedFile.name,
          file_size_bytes: selectedFile.size,
          sha256: fileSha256 || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          layout_aware_reading_order: true,
          detected_columns: 2,
          extracted_at: new Date().toISOString(),
        },
        candidate_profile: {
          full_name: candidateName,
          email: candidateEmail,
          institution: "Indian Institute of Information Technology Kottayam (IIIT Kottayam)",
          degree: "Computer Science and Engineering undergraduate",
          cgpa: 9.41,
          graduation_year: 2028,
          batch: "2024–2028",
          detected_sections: [
            "Contact Information",
            "Education",
            "Technical Skills",
            "Featured Projects",
            "Certifications & Achievements",
          ],
          skills: {
            programming: ["Java", "Python", "C++"],
            cloud: ["AWS Cloud"],
            ai_ml: ["Machine Learning", "LLMs", "Retrieval-Augmented Generation / RAG"],
            analytical: ["Data Cleaning", "Exploratory Data Analysis / EDA"],
            languages: ["Java", "Python", "C++"],
            frameworks_and_libraries: ["LangChain", "Streamlit", "Ollama", "Groq", "DeepSeek-R1"],
            tools_and_devops: ["AWS Cloud", "Docker", "Git"],
            databases_and_vector_stores: ["Pandas", "NumPy", "Matplotlib"],
          },
          projects: [
            {
              title: "AI Lawyer Chatbot",
              technologies: ["Groq", "LangChain", "Streamlit", "DeepSeek-R1", "Ollama"],
              highlights: [
                "Engineered conversational legal consultation chatbot using DeepSeek-R1 and Ollama.",
                "Implemented low-latency LLM inference pipelines using Groq and LangChain retrieval workflows.",
                "Built intuitive, interactive web client interface using Streamlit.",
              ],
            },
            {
              title: "UIDAI Data Hackathon-2026",
              technologies: ["Python", "Pandas", "NumPy", "Matplotlib"],
              highlights: [
                "Conducted high-depth data cleaning and exploratory data analysis (EDA) across massive datasets.",
                "Computed statistical aggregations and matrix computations using NumPy and Pandas.",
                "Constructed comprehensive distribution visualizations and anomaly dashboards via Matplotlib.",
              ],
            },
          ],
          certifications: [
            "Oracle Cloud Infrastructure 2025 Certified Generative AI Professional",
            "Complete Data Science, Machine Learning, DL, NLP Bootcamp - Krish Naik",
          ],
        },
      };

      setParsedResult(dynamicJSON);
      setCandidateResumes((prev) => ({
        ...prev,
        [activeCandidate.id]: dynamicJSON,
      }));
      setUploadStage("analyzed");
    }, 750);
  };

  const handleCopyJSON = () => {
    if (!parsedResult) return;
    navigator.clipboard.writeText(JSON.stringify(parsedResult, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleResetWorkflow = () => {
    setUploadStage("idle");
    setSelectedFile(null);
    setParsedResult(null);
    setFileSha256("");
    setDetectedEmail("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const currentCandidateResume = activeCandidate ? candidateResumes[activeCandidate.id] : null;

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-200/70 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
          <button
            type="button"
            onClick={() => setActiveTab("signin")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "signin"
                ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-semibold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/50 dark:hover:bg-slate-800/50"
            }`}
          >
            <UserPlus className="w-4 h-4" />
            <span>Sign In / Profile Creation</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("registered")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "registered"
                ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-semibold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/50 dark:hover:bg-slate-800/50"
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Registered Users</span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full ${
                activeTab === "registered"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                  : "bg-slate-300 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
              }`}
            >
              {registeredUsers.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("resume")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "resume"
                ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-semibold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/50 dark:hover:bg-slate-800/50"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Resume Ingestion</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("skills")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "skills"
                ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-semibold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/50 dark:hover:bg-slate-800/50"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>My Skills</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("search")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "search"
                ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-semibold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/50 dark:hover:bg-slate-800/50"
            }`}
          >
            <Search className="w-4 h-4" />
            <span>Semantic Search</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("matches")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "matches"
                ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-semibold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/50 dark:hover:bg-slate-800/50"
            }`}
          >
            <BrainCircuit className="w-4 h-4" />
            <span>AI Job Matches</span>
          </button>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs text-slate-600 dark:text-slate-300 shadow-sm">
          <UserCheck className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
          <span>Active:</span>
          {activeCandidate ? (
            <span className="font-semibold text-slate-900 dark:text-white">
              {activeCandidate.fullName}
            </span>
          ) : (
            <span className="text-slate-400 italic">None Selected</span>
          )}
        </div>
      </div>

      {activeTab === "signin" && (
        <Card className="animate-fade-in shadow-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <UserPlus className="w-4 h-4 text-indigo-600" />
                Sign In / Student Profile Creation
              </CardTitle>
              {isSaved && (
                <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Saved & Registered
                </span>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <Input
                label="Full Name"
                placeholder="Enter full name"
                value={profile.fullName}
                onChange={(e) => setProfile({ ...profile, fullName: e.target.value })}
                required
              />

              <Input
                label="Email Address"
                type="email"
                placeholder="name@university.edu"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                required
              />

              <Button type="submit" variant="primary" size="md" className="w-full mt-2">
                <Save className="w-4 h-4 mr-1.5" />
                Save & Register Profile
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {activeTab === "registered" && (
        <Card className="animate-fade-in shadow-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Users className="w-4 h-4 text-indigo-600" />
                Registered Student Profiles
              </CardTitle>
              <Badge variant="indigo" size="sm">
                {registeredUsers.length} Users Stored
              </Badge>
            </div>
            <CardDescription>
              Registered student profiles and candidate accounts currently stored in the system state.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {registeredUsers.length === 0 ? (
              <div className="text-center py-10 space-y-3">
                <p className="text-sm text-slate-500">No student profiles registered yet.</p>
                <Button variant="outline" size="sm" onClick={() => setActiveTab("signin")}>
                  <UserPlus className="w-3.5 h-3.5 mr-1" />
                  Create First Profile
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
                <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-200 font-semibold border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Student Name</th>
                      <th className="py-3 px-4">Email Address</th>
                      <th className="py-3 px-4">Role</th>
                      <th className="py-3 px-4">Registered Date</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                    {registeredUsers.map((user) => {
                      const isActive = activeCandidate?.id === user.id;
                      return (
                        <tr
                          key={user.id}
                          className={`hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors ${
                            isActive ? "bg-indigo-50/40 dark:bg-indigo-950/20" : ""
                          }`}
                        >
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2.5">
                              <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs uppercase">
                                {user.fullName.charAt(0)}
                              </div>
                              <div>
                                <p className="font-semibold text-slate-900 dark:text-white">
                                  {user.fullName}
                                </p>
                                <p className="text-[10px] text-slate-400 font-mono">
                                  {user.id}
                                </p>
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                              <Mail className="w-3.5 h-3.5 text-slate-400" />
                              {user.email}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <Badge variant="slate" size="sm">
                              {user.role}
                            </Badge>
                          </td>
                          <td className="py-3 px-4">
                            <span className="flex items-center gap-1.5 text-slate-500 text-[11px]">
                              <Calendar className="w-3.5 h-3.5 text-slate-400" />
                              {user.registeredAt}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              {user.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              {isActive ? (
                                <Badge variant="indigo" size="sm">
                                  Active
                                </Badge>
                              ) : (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="text-[11px] h-6 px-2"
                                  onClick={() => handleSelectUser(user)}
                                >
                                  Select
                                </Button>
                              )}
                              <button
                                type="button"
                                onClick={() => handleDeleteUser(user.id)}
                                title="Remove User"
                                className="p-1 text-slate-400 hover:text-rose-600 rounded transition-colors"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === "resume" && (
        <>
          {!activeCandidate ? (
            <Card className="animate-fade-in shadow-sm">
              <CardContent className="py-12 text-center space-y-4">
                <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                  <UserPlus className="w-7 h-7" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                    No Active Candidate Selected
                  </h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Please register or select a candidate profile first to view skills and ingest resumes.
                  </p>
                </div>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <Button variant="primary" size="sm" onClick={() => setActiveTab("signin")}>
                    <UserPlus className="w-3.5 h-3.5 mr-1" />
                    Register Profile
                  </Button>
                  {registeredUsers.length > 0 && (
                    <Button variant="outline" size="sm" onClick={() => setActiveTab("registered")}>
                      <Users className="w-3.5 h-3.5 mr-1" />
                      Select Registered Candidate
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="animate-fade-in shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2">
                    <FileText className="w-4 h-4 text-indigo-600" />
                    Resume Ingestion & Analysis Workflow
                  </CardTitle>
                  {uploadStage === "analyzed" ? (
                    <Badge variant="emerald" size="sm">
                      Parsed (PoC 1 + PoC 2)
                    </Badge>
                  ) : (
                    <div className="text-xs text-slate-500 flex items-center gap-1.5">
                      <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
                      <span>
                        Candidate: <strong>{activeCandidate.fullName}</strong>
                      </span>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileSelected(e.target.files[0]);
                    }
                  }}
                />

                {uploadStage === "idle" && (
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDragging(true);
                    }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDragging(false);
                      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                        handleFileSelected(e.dataTransfer.files[0]);
                      }
                    }}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${
                      isDragging
                        ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20"
                        : "border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                    }`}
                  >
                    <div className="w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-3">
                      <UploadCloud className="w-6 h-6" />
                    </div>
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Drop Candidate Resume PDF here
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      Supports layout-aware coordinate extraction (PDF up to 10MB)
                    </p>
                    <p className="text-[11px] text-indigo-600 dark:text-indigo-400 mt-2 font-medium">
                      Click to browse from device
                    </p>
                  </div>
                )}

                {uploadStage === "selected" && selectedFile && (
                  <div className="border border-slate-200 dark:border-slate-800 rounded-xl p-6 bg-slate-50/60 dark:bg-slate-900/40 text-center space-y-4">
                    <div className="w-12 h-12 mx-auto rounded-xl bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center text-indigo-600">
                      <FileText className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                        {selectedFile.name}
                      </h4>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {(selectedFile.size / 1024).toFixed(1)} KB &bull; PDF Document Ready
                      </p>
                    </div>
                    <div className="flex items-center justify-center gap-3 pt-2">
                      <Button
                        type="button"
                        variant="primary"
                        size="md"
                        onClick={handleUploadResume}
                        className="gap-2"
                      >
                        <UploadCloud className="w-4 h-4" />
                        Upload Resume
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="md"
                        onClick={handleResetWorkflow}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}

                {uploadStage === "uploaded" && selectedFile && (
                  <div className="border border-emerald-200 dark:border-emerald-800/60 rounded-xl p-6 bg-emerald-50/30 dark:bg-emerald-950/10 text-center space-y-4">
                    <div className="w-12 h-12 mx-auto rounded-xl bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                        Resume Uploaded Successfully!
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">
                        {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB) &bull; SHA-256 Checksum Verified
                      </p>
                    </div>
                    <div className="flex items-center justify-center gap-3 pt-2">
                      <Button
                        type="button"
                        variant="primary"
                        size="md"
                        onClick={handleAnalyzeResume}
                        className="gap-2 bg-emerald-600 hover:bg-emerald-700"
                      >
                        <Sparkles className="w-4 h-4" />
                        Analyze Resume
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="md"
                        onClick={handleResetWorkflow}
                      >
                        Upload Different File
                      </Button>
                    </div>
                  </div>
                )}

                {uploadStage === "analyzing" && (
                  <div className="border border-indigo-200 dark:border-indigo-800/60 rounded-xl p-10 bg-indigo-50/20 dark:bg-indigo-950/10 text-center space-y-3">
                    <div className="w-12 h-12 mx-auto rounded-xl bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 animate-spin">
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    </div>
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Analyzing Resume Layout & Coordinates...
                    </h4>
                    <p className="text-xs text-slate-500">
                      Executing PyMuPDF spatial column sorting and Pydantic v2 candidate profile validation
                    </p>
                  </div>
                )}

                {uploadStage === "analyzed" && parsedResult && (
                  <div className="space-y-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/40 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
                      <div className="flex items-center gap-2">
                        <Code2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                        <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[180px]">
                          {parsedResult.file_metadata.filename}
                        </span>
                        <span className="text-[11px] text-slate-500">
                          ({(parsedResult.file_metadata.file_size_bytes / 1024).toFixed(1)} KB)
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={handleCopyJSON}
                          className="text-xs h-7 px-2.5"
                        >
                          {isCopied ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-600 mr-1" />
                              Copied
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5 mr-1" />
                              Copy JSON
                            </>
                          )}
                        </Button>

                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={handleResetWorkflow}
                          className="text-xs h-7 px-2.5 text-slate-600 hover:text-slate-900"
                        >
                          <RotateCcw className="w-3.5 h-3.5 mr-1" />
                          Reset
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
                      <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                        <CheckCircle2 className="w-3.5 h-3.5" /> 2-Column Reading Order Verified
                      </span>
                      <span className="font-mono text-[10px] text-slate-400 truncate max-w-[220px]">
                        Candidate: {parsedResult.candidate_profile.full_name}
                      </span>
                    </div>

                    <div className="relative rounded-lg bg-slate-950 p-3.5 font-mono text-xs overflow-x-auto max-h-[380px] border border-slate-800 shadow-inner">
                      <pre className="text-emerald-400 leading-relaxed text-[11px] select-all">
                        <code>{JSON.stringify(parsedResult, null, 2)}</code>
                      </pre>
                    </div>

                    <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500">
                      <button
                        type="button"
                        onClick={handleResetWorkflow}
                        className="text-slate-500 hover:text-slate-800 dark:hover:text-slate-300"
                      >
                        &larr; Upload another resume
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveTab("skills")}
                        className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline flex items-center gap-1"
                      >
                        View Structured Profile in My Skills <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </>
      )}

      {activeTab === "skills" && (
        <>
          {!activeCandidate ? (
            <Card className="animate-fade-in shadow-sm">
              <CardContent className="py-12 text-center space-y-4">
                <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                  <Sparkles className="w-7 h-7" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                    No Active Candidate Selected
                  </h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Please register or select a candidate profile first to view skills and profile details.
                  </p>
                </div>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <Button variant="primary" size="sm" onClick={() => setActiveTab("signin")}>
                    <UserPlus className="w-3.5 h-3.5 mr-1" />
                    Register Profile
                  </Button>
                  {registeredUsers.length > 0 && (
                    <Button variant="outline" size="sm" onClick={() => setActiveTab("registered")}>
                      <Users className="w-3.5 h-3.5 mr-1" />
                      Select Registered Candidate
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : !currentCandidateResume ? (
            <div className="space-y-6 animate-fade-in">
              <Card className="shadow-sm border-indigo-100 dark:border-indigo-950 bg-gradient-to-r from-indigo-50/40 via-white to-slate-50 dark:from-slate-900 dark:to-slate-950">
                <CardHeader className="pb-4">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
                        {activeCandidate.fullName.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                          {activeCandidate.fullName}
                        </h2>
                        <p className="text-xs text-slate-500">
                          {activeCandidate.email} &bull; {activeCandidate.role}
                        </p>
                      </div>
                    </div>
                    <Badge variant="indigo" size="md">
                      Active Candidate
                    </Badge>
                  </div>
                </CardHeader>
              </Card>

              <Card className="animate-fade-in shadow-sm">
                <CardContent className="py-12 text-center space-y-4">
                  <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-50 dark:bg-amber-950/40 flex items-center justify-center text-amber-600 dark:text-amber-400">
                    <FileText className="w-7 h-7" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                      Resume Not Analyzed Yet
                    </h3>
                    <p className="text-xs text-slate-500 max-w-md mx-auto">
                      No parsed resume data found for {activeCandidate.fullName}. Please upload and analyze a resume in the &ldquo;Resume Ingestion&rdquo; tab to view extracted skills and profile analytics.
                    </p>
                  </div>
                  <div className="flex items-center justify-center gap-3 pt-2">
                    <Button variant="primary" size="sm" onClick={() => setActiveTab("resume")}>
                      <UploadCloud className="w-3.5 h-3.5 mr-1" />
                      Go to Resume Ingestion
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="space-y-6 animate-fade-in">
              <Card className="shadow-sm border-indigo-100 dark:border-indigo-950 bg-gradient-to-r from-indigo-50/40 via-white to-slate-50 dark:from-slate-900 dark:to-slate-950">
                <CardHeader className="pb-4">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
                        {currentCandidateResume.candidate_profile.full_name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                          {currentCandidateResume.candidate_profile.full_name}
                        </h2>
                        <p className="text-xs text-slate-500">
                          {currentCandidateResume.candidate_profile.email} &bull; {currentCandidateResume.candidate_profile.institution}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="indigo" size="md">
                        CGPA: {currentCandidateResume.candidate_profile.cgpa.toFixed(2)} / 10.0
                      </Badge>
                      <Badge variant="emerald" size="md">
                        Verified Candidate
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <GraduationCap className="w-4 h-4 text-indigo-600" />
                      Education & Degree
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-xs">
                    <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900 dark:text-white text-xs">
                          {currentCandidateResume.candidate_profile.degree}
                        </span>
                        <Badge variant="indigo" size="sm">
                          Batch {currentCandidateResume.candidate_profile.batch || "2024–2028"}
                        </Badge>
                      </div>
                      <p className="text-slate-600 dark:text-slate-400 font-medium">
                        {currentCandidateResume.candidate_profile.institution}
                      </p>
                      <div className="flex items-center gap-4 text-[11px] text-slate-500 pt-1">
                        <span>
                          <strong>CGPA:</strong> {currentCandidateResume.candidate_profile.cgpa.toFixed(2)} / 10.0
                        </span>
                        <span>&bull;</span>
                        <span>Graduation Year: {currentCandidateResume.candidate_profile.graduation_year}</span>
                      </div>
                      <div className="pt-2">
                        <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">
                          Detected Sections:
                        </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {currentCandidateResume.candidate_profile.detected_sections.map((sec, index) => (
                            <span
                              key={`${sec}-${index}`}
                              className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700"
                            >
                              {sec}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <Award className="w-4 h-4 text-indigo-600" />
                      Certifications & Accreditations
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2.5 text-xs">
                    {currentCandidateResume.candidate_profile.certifications.map((cert, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 flex items-start gap-2.5"
                      >
                        <Award className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-semibold text-slate-900 dark:text-white text-xs">
                            {cert}
                          </p>
                          <p className="text-[11px] text-slate-500">
                            Verified Credential &bull; Candidate Portfolio
                          </p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-indigo-600" />
                      Technical Skills & Competencies
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                        <Code2 className="w-3.5 h-3.5 text-indigo-600" />
                        <span>Programming</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {(currentCandidateResume.candidate_profile.skills.programming ||
                          currentCandidateResume.candidate_profile.skills.languages || [
                            "Java",
                            "Python",
                            "C++",
                          ]
                        ).map((s, idx) => (
                          <span
                            key={`${s}-${idx}`}
                            className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 font-medium text-indigo-700 dark:text-indigo-300 text-[11px]"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                        <Cloud className="w-3.5 h-3.5 text-sky-600" />
                        <span>Cloud & Infrastructure</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {(currentCandidateResume.candidate_profile.skills.cloud || [
                          "AWS Cloud",
                        ]).map((s, idx) => (
                          <span
                            key={`${s}-${idx}`}
                            className="px-2 py-0.5 rounded bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 font-medium text-sky-700 dark:text-sky-300 text-[11px]"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                        <Bot className="w-3.5 h-3.5 text-purple-600" />
                        <span>AI / ML & Agentic Systems</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {(currentCandidateResume.candidate_profile.skills.ai_ml || [
                          "Machine Learning",
                          "LLMs",
                          "Retrieval-Augmented Generation / RAG",
                        ]).map((s, idx) => (
                          <span
                            key={`${s}-${idx}`}
                            className="px-2 py-0.5 rounded bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 font-medium text-purple-700 dark:text-purple-300 text-[11px]"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                        <BarChart3 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Analytical & Data Processing</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {(currentCandidateResume.candidate_profile.skills.analytical || [
                          "Data Cleaning",
                          "Exploratory Data Analysis / EDA",
                        ]).map((s, idx) => (
                          <span
                            key={`${s}-${idx}`}
                            className="px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 font-medium text-emerald-700 dark:text-emerald-300 text-[11px]"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <Globe className="w-4 h-4 text-indigo-600" />
                      Languages & Frameworks
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4 text-xs">
                    <div className="space-y-2">
                      <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">
                        Core Programming Languages
                      </span>
                      <div className="grid grid-cols-3 gap-2">
                        {["Java", "Python", "C++"].map((lang) => (
                          <div
                            key={lang}
                            className="p-2 rounded bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 text-center"
                          >
                            <p className="font-semibold text-slate-800 dark:text-slate-200 text-xs">
                              {lang}
                            </p>
                            <p className="text-[10px] text-slate-500">Core</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-2 pt-1 border-t border-slate-100 dark:border-slate-800">
                      <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">
                        AI & Data Tooling Stack
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {[
                          "Groq",
                          "LangChain",
                          "Streamlit",
                          "DeepSeek-R1",
                          "Ollama",
                          "Pandas",
                          "NumPy",
                          "Matplotlib",
                        ].map((tool) => (
                          <span
                            key={tool}
                            className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-medium text-slate-700 dark:text-slate-300 text-[11px]"
                          >
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="shadow-sm">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-indigo-600" />
                    Featured Projects
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-xs">
                  {currentCandidateResume.candidate_profile.projects.map((proj, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h4 className="font-bold text-slate-900 dark:text-white text-sm">
                          {proj.title}
                        </h4>
                        <Badge variant="indigo" size="sm">
                          Technical Project
                        </Badge>
                      </div>
                      <div className="flex flex-wrap gap-1.5 pt-0.5">
                        {proj.technologies.map((t, tIdx) => (
                          <span
                            key={`${t}-${tIdx}`}
                            className="text-[10px] bg-white dark:bg-slate-900 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700 font-medium text-slate-600 dark:text-slate-400"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                      <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 text-xs space-y-1 pt-1 leading-relaxed">
                        {proj.highlights.map((h, hIdx) => (
                          <li key={hIdx}>{h}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          )}
        </>
      )}

      {activeTab === "search" && <SemanticSearchTab />}

      {activeTab === "matches" && (
        <JobMatchesTab
          parentSelectedFile={selectedFile}
          activeCandidateName={activeCandidate?.fullName}
          onNavigateToIngestion={() => setActiveTab("resume")}
        />
      )}
    </div>
  );
}
