# InternAI — Next.js 15+ Frontend Web Application (Milestone 1)

Minimalist, responsive, and type-safe web client for the **AI-Powered Internship Application and Career Assistance Platform**. Built using **Next.js 15 (App Router)**, **React 19**, **TypeScript**, and **Tailwind CSS**, focused strictly on Milestone 1 objectives: candidate profile modeling and layout-aware PDF resume ingestion.

---

## 1. Milestone 1 User Interface Features

### 1.1 Candidate Profile Definition Form
- Relational candidate profile definition matching Pydantic v2 schemas.
- Captures Full Name, Email, University, Degree & Major, Cumulative GPA (with 0.00 - 4.00 domain validation), Graduation Term & Year, and Visa Sponsorship status.
- Core technical skills input with visual badge categorization.

### 1.2 Layout-Aware Resume PDF Upload Dropzone
- Interactive drag-and-drop interface accepting PDF resumes up to 10MB.
- Demonstrates PyMuPDF bounding-box coordinate extraction ($x_1 \le 230\text{pt}$) and vertical sorting, preventing column interleaving errors.
- Real-time extraction preview displaying:
  - Document metadata: File name, file size, SHA-256 binary hash.
  - Section partitioning: Education, Technical Skills, Projects, Experience.
  - Normalized skills inventory mapped against the ESCO taxonomy.
  - Extracted technical projects and bullet points.

### 1.3 PoC Validation Telemetry
- Quick-reference status panel verifying that all 4 backend PoC validation scripts have completed and passed with 100% assertions satisfied.

---

## 2. Directory Structure

```
frontend/
├── app/
│   ├── globals.css                # Tailwind directives and clean typography
│   ├── layout.tsx                 # Root layout with Navbar and centered container
│   └── page.tsx                   # Unified Milestone 1 Profile & Resume Dropzone
├── components/
│   ├── layout/
│   │   └── Navbar.tsx             # Minimal project header with Milestone 1 status
│   └── ui/
│       ├── Badge.tsx              # Colored status and skill badges
│       ├── Button.tsx             # Accessible Tailwind button with variants
│       ├── Card.tsx               # Card primitives (Header, Title, Content, Footer)
│       ├── Dropzone.tsx           # Drag-and-drop resume PDF upload component
│       └── Input.tsx              # Accessible form input with error state
├── lib/
│   ├── types.ts                   # Strict TypeScript contracts matching backend schemas
│   └── api-client.ts              # Fetch client pointing to http://localhost:8000/api/v1
├── package.json                   # Dependencies (Next.js 15, React 19, Lucide React)
├── tailwind.config.ts             # Tailwind CSS theme configuration
├── tsconfig.json                  # Strict TypeScript configuration
└── next.config.ts                 # Next.js 15 configuration
```

---

## 3. Running Locally

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Step 3: Production Build Verification
```bash
npm run build
```
