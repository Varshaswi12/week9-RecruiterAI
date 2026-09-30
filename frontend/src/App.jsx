import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  BriefcaseBusiness,
  Users,
  Upload,
  BarChart3,
  LogOut,
  Plus,
  FileText,
  Sparkles,
  CheckCircle2,
  XCircle,
  Loader2,
  UserCircle,
  LockKeyhole,
  Mail,
  UserPlus,
  ArrowRight,
  RefreshCw,
} from "lucide-react";

import "./App.css";


const API_URL = "http://127.0.0.1:8000";


function App() {

  const [token, setToken] = useState(
    localStorage.getItem("token")
  );

  const [user, setUser] = useState(null);

  const [authMode, setAuthMode] = useState("login");

  const [loadingUser, setLoadingUser] = useState(
    Boolean(token)
  );

  const [page, setPage] = useState("dashboard");

  const [jobs, setJobs] = useState([]);

  const [candidates, setCandidates] = useState([]);

  const [ranking, setRanking] = useState([]);

  const [selectedJob, setSelectedJob] = useState(null);

  const [selectedCandidate, setSelectedCandidate] =
    useState(null);

  const [selectedMatch, setSelectedMatch] =
    useState(null);

  const [jobText, setJobText] = useState("");

  const [resumeFile, setResumeFile] =
    useState(null);

  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");

  const [error, setError] = useState("");


  // ============================================================
  // AUTH
  // ============================================================

  useEffect(() => {

    if (!token) {

      setUser(null);
      setLoadingUser(false);

      return;
    }

    loadCurrentUser();

  }, [token]);


  async function loadCurrentUser() {

    try {

      setLoadingUser(true);

      const response = await fetch(
        `${API_URL}/auth/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {

        localStorage.removeItem("token");

        setToken(null);

        setUser(null);

        return;
      }

      const data = await response.json();

      setUser(data.user);

    } catch (err) {

      console.error(err);

      setError(
        "Could not connect to the backend."
      );

    } finally {

      setLoadingUser(false);

    }
  }


  async function loginUser(
    email,
    password
  ) {

    setLoading(true);
    setError("");
    setMessage("");

    try {

      const response = await fetch(
        `${API_URL}/auth/login`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            email,
            password
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Login failed."
        );

      }

      localStorage.setItem(
        "token",
        data.access_token
      );

      setToken(
        data.access_token
      );

      setUser(data.user);

      setMessage(
        "Login successful."
      );

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  async function registerUser(
    name,
    email,
    password
  ) {

    setLoading(true);
    setError("");
    setMessage("");

    try {

      const response = await fetch(
        `${API_URL}/auth/register`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            name,
            email,
            password
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Registration failed."
        );

      }

      setMessage(
        "Account created successfully. Please login."
      );

      setAuthMode("login");

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  function logout() {

    localStorage.removeItem("token");

    setToken(null);

    setUser(null);

    setJobs([]);

    setCandidates([]);

    setRanking([]);

    setSelectedJob(null);

    setSelectedCandidate(null);

    setSelectedMatch(null);

    setPage("dashboard");

    setMessage("");

    setError("");

  }


  // ============================================================
  // API HELPERS
  // ============================================================

  async function authenticatedFetch(
    endpoint,
    options = {}
  ) {

    if (!token) {

      throw new Error(
        "Please login first."
      );

    }

    const headers = {
      ...(options.headers || {}),
      Authorization:
        `Bearer ${token}`
    };

    const response = await fetch(
      `${API_URL}${endpoint}`,
      {
        ...options,
        headers
      }
    );

    const data =
      await response.json();

    if (!response.ok) {

      throw new Error(
        data.detail ||
        "Request failed."
      );

    }

    return data;
  }


  // ============================================================
  // LOAD JOBS
  // ============================================================

  async function loadJobs() {

    try {

      setLoading(true);
      setError("");

      const data =
        await authenticatedFetch(
          "/jobs"
        );

      setJobs(
        data.jobs || []
      );

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  // ============================================================
  // LOAD CANDIDATES
  // ============================================================

  async function loadCandidates() {

    try {

      setLoading(true);
      setError("");

      const response =
        await fetch(
          `${API_URL}/resumes/candidates`
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Could not load candidates."
        );

      }

      setCandidates(
        data.candidates || []
      );

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  // ============================================================
  // CREATE JOB
  // ============================================================

  async function createJob() {

    if (!jobText.trim()) {

      setError(
        "Please enter a job description."
      );

      return;
    }

    try {

      setLoading(true);
      setError("");
      setMessage("");

      const data =
        await authenticatedFetch(
          "/jobs/create",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
              text: jobText
            })
          }
        );

      setMessage(
        "Job created successfully."
      );

      setJobText("");

      await loadJobs();

      setPage("jobs");

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  // ============================================================
  // UPLOAD RESUME
  // ============================================================

  async function uploadResume() {

    if (!resumeFile) {

      setError(
        "Please select a PDF or DOCX resume."
      );

      return;
    }

    try {

      setLoading(true);
      setError("");
      setMessage("");

      const formData =
        new FormData();

      formData.append(
        "file",
        resumeFile
      );

      const response =
        await fetch(
          `${API_URL}/resumes/upload`,
          {
            method: "POST",
            body: formData
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Resume upload failed."
        );

      }

      setMessage(
        `${data.candidate.name} was uploaded successfully.`
      );

      setResumeFile(null);

      await loadCandidates();

      setPage("candidates");

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  // ============================================================
  // RUN MATCH
  // ============================================================

  async function runMatch(
    jobId,
    candidateId
  ) {

    try {

      setLoading(true);
      setError("");
      setMessage("");

      const response =
        await fetch(
          `${API_URL}/matching/run`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
              job_id: jobId,
              candidate_id: candidateId
            })
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Matching failed."
        );

      }

      setSelectedMatch(
        data.match
      );

      setSelectedJob(
        jobs.find(
          job =>
            job.id === jobId
        ) || null
      );

      setSelectedCandidate(
        candidates.find(
          candidate =>
            candidate.id === candidateId
        ) || null
      );

      setPage("match");

      setMessage(
        "Candidate matching completed."
      );

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  // ============================================================
  // LOAD RANKING
  // ============================================================

  async function loadRanking(
    jobId
  ) {

    try {

      setLoading(true);
      setError("");

      const data =
        await fetch(
          `${API_URL}/matching/job/${jobId}/rank`
        );

      const result =
        await data.json();

      if (!data.ok) {

        throw new Error(
          result.detail ||
          "Could not load ranking."
        );

      }

      setRanking(
        result.ranking || []
      );

      setSelectedJob(
        jobs.find(
          job =>
            job.id === jobId
        ) || null
      );

      setPage("ranking");

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  // ============================================================
  // REFRESH DATA
  // ============================================================

  async function refreshData() {

    setError("");

    await Promise.all([
      loadJobs(),
      loadCandidates()
    ]);

  }


  // ============================================================
  // PAGE CHANGES
  // ============================================================

  async function changePage(
    nextPage
  ) {

    setPage(nextPage);

    setMessage("");

    setError("");

    if (nextPage === "jobs") {

      await loadJobs();

    }

    if (nextPage === "candidates") {

      await loadCandidates();

    }

    if (nextPage === "dashboard") {

      await refreshData();

    }

  }


  // ============================================================
  // LOADING SCREEN
  // ============================================================

  if (loadingUser) {

    return (
      <div className="loading-screen">

        <Loader2
          size={42}
          className="spin"
        />

        <p>
          Connecting to RecruitAI...
        </p>

      </div>
    );

  }


  // ============================================================
  // LOGIN SCREEN
  // ============================================================

  if (!token || !user) {

    return (
      <AuthScreen
        mode={authMode}
        setMode={setAuthMode}
        onLogin={loginUser}
        onRegister={registerUser}
        loading={loading}
        error={error}
        message={message}
      />
    );

  }


  // ============================================================
  // DASHBOARD
  // ============================================================

  return (
    <div className="app-shell">

      <Sidebar
        page={page}
        setPage={changePage}
        logout={logout}
      />

      <main className="main-content">

        <TopBar
          user={user}
          onRefresh={refreshData}
          loading={loading}
        />

        {message && (
          <div className="success-alert">

            <CheckCircle2 size={18} />

            <span>
              {message}
            </span>

          </div>
        )}

        {error && (
          <div className="error-alert">

            <XCircle size={18} />

            <span>
              {error}
            </span>

          </div>
        )}

        {page === "dashboard" && (

          <DashboardPage
            jobs={jobs}
            candidates={candidates}
            loading={loading}
            onNavigate={changePage}
          />

        )}

        {page === "jobs" && (

          <JobsPage
            jobs={jobs}
            loading={loading}
            jobText={jobText}
            setJobText={setJobText}
            createJob={createJob}
            loadRanking={loadRanking}
          />

        )}

        {page === "candidates" && (

          <CandidatesPage
            candidates={candidates}
            loading={loading}
            onMatch={runMatch}
            jobs={jobs}
            onUpload={() =>
              changePage("upload")
            }
          />

        )}

        {page === "upload" && (

          <UploadPage
            resumeFile={resumeFile}
            setResumeFile={setResumeFile}
            uploadResume={uploadResume}
            loading={loading}
          />

        )}

        {page === "ranking" && (

          <RankingPage
            ranking={ranking}
            selectedJob={selectedJob}
            loading={loading}
            onMatch={runMatch}
          />

        )}

        {page === "match" && (

          <MatchPage
            match={selectedMatch}
            candidate={selectedCandidate}
            job={selectedJob}
          />

        )}

      </main>

    </div>
  );
}


// ============================================================
// AUTH SCREEN
// ============================================================

function AuthScreen({
  mode,
  setMode,
  onLogin,
  onRegister,
  loading,
  error,
  message
}) {

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");


  function submit(event) {

    event.preventDefault();

    if (mode === "login") {

      onLogin(
        email,
        password
      );

    } else {

      onRegister(
        name,
        email,
        password
      );

    }

  }


  return (
    <div className="auth-page">

      <div className="auth-card">

        <div className="auth-brand">

          <div className="brand-icon">
            <Sparkles size={24} />
          </div>

          <div>
            <h1>
              RecruitAI
            </h1>

            <p>
              AI Recruitment Platform
            </p>
          </div>

        </div>

        <div className="auth-heading">

          <h2>
            {mode === "login"
              ? "Welcome back"
              : "Create recruiter account"}
          </h2>

          <p>
            {mode === "login"
              ? "Sign in to manage jobs and candidates."
              : "Create an account to start recruiting with AI."}
          </p>

        </div>

        {error && (
          <div className="error-alert">

            <XCircle size={18} />

            <span>
              {error}
            </span>

          </div>
        )}

        {message && (
          <div className="success-alert">

            <CheckCircle2 size={18} />

            <span>
              {message}
            </span>

          </div>
        )}

        <form
          onSubmit={submit}
          className="auth-form"
        >

          {mode === "register" && (

            <label>

              <span>
                Full Name
              </span>

              <div className="input-wrapper">

                <UserCircle size={18} />

                <input
                  type="text"
                  placeholder="Your name"
                  value={name}
                  onChange={event =>
                    setName(
                      event.target.value
                    )
                  }
                  required
                />

              </div>

            </label>

          )}

          <label>

            <span>
              Email
            </span>

            <div className="input-wrapper">

              <Mail size={18} />

              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={event =>
                  setEmail(
                    event.target.value
                  )
                }
                required
              />

            </div>

          </label>

          <label>

            <span>
              Password
            </span>

            <div className="input-wrapper">

              <LockKeyhole size={18} />

              <input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={event =>
                  setPassword(
                    event.target.value
                  )
                }
                required
              />

            </div>

          </label>

          <button
            type="submit"
            className="primary-button full-width"
            disabled={loading}
          >

            {loading ? (
              <>
                <Loader2
                  size={18}
                  className="spin"
                />

                Please wait...
              </>
            ) : (
              <>
                {mode === "login"
                  ? "Login"
                  : "Create Account"}

                <ArrowRight
                  size={18}
                />
              </>
            )}

          </button>

        </form>

        <div className="auth-switch">

          {mode === "login"
            ? "Don't have an account?"
            : "Already have an account?"}

          <button
            type="button"
            onClick={() => {

              setMode(
                mode === "login"
                  ? "register"
                  : "login"
              );

            }}
          >
            {mode === "login"
              ? "Create account"
              : "Login"}
          </button>

        </div>

      </div>

    </div>
  );
}


// ============================================================
// SIDEBAR
// ============================================================

function Sidebar({
  page,
  setPage,
  logout
}) {

  const items = [

    {
      id: "dashboard",
      label: "Dashboard",
      icon: LayoutDashboard
    },

    {
      id: "jobs",
      label: "Jobs",
      icon: BriefcaseBusiness
    },

    {
      id: "candidates",
      label: "Candidates",
      icon: Users
    },

    {
      id: "upload",
      label: "Upload Resume",
      icon: Upload
    },

    {
      id: "ranking",
      label: "Ranking",
      icon: BarChart3
    }

  ];


  return (
    <aside className="sidebar">

      <div className="sidebar-brand">

        <div className="brand-icon">
          <Sparkles size={21} />
        </div>

        <div>
          <strong>
            RecruitAI
          </strong>

          <span>
            DStarix Techno
          </span>
        </div>

      </div>


      <nav className="sidebar-nav">

        <p className="nav-label">
          WORKSPACE
        </p>

        {items.map(item => {

          const Icon =
            item.icon;

          return (
            <button
              key={item.id}
              className={
                page === item.id
                  ? "nav-item active"
                  : "nav-item"
              }
              onClick={() =>
                setPage(item.id)
              }
            >

              <Icon size={19} />

              <span>
                {item.label}
              </span>

            </button>
          );

        })}

      </nav>


      <button
        className="logout-button"
        onClick={logout}
      >

        <LogOut size={18} />

        Logout

      </button>

    </aside>
  );
}


// ============================================================
// TOP BAR
// ============================================================

function TopBar({
  user,
  onRefresh,
  loading
}) {

  return (
    <header className="topbar">

      <div>

        <p className="eyebrow">
          AI RECRUITMENT PLATFORM
        </p>

        <h1>
          Welcome, {user.name}
        </h1>

      </div>

      <div className="topbar-actions">

        <button
          className="icon-button"
          onClick={onRefresh}
          title="Refresh data"
          disabled={loading}
        >

          <RefreshCw
            size={18}
            className={
              loading
                ? "spin"
                : ""
            }
          />

        </button>

        <div className="user-chip">

          <div className="avatar">
            {user.name
              ?.charAt(0)
              ?.toUpperCase()}
          </div>

          <div>

            <strong>
              {user.name}
            </strong>

            <span>
              {user.email}
            </span>

          </div>

        </div>

      </div>

    </header>
  );
}


// ============================================================
// DASHBOARD
// ============================================================

function DashboardPage({
  jobs,
  candidates,
  loading,
  onNavigate
}) {

  return (
    <section className="page">

      <div className="page-heading">

        <div>

          <h2>
            Recruitment Dashboard
          </h2>

          <p>
            Manage jobs, candidates and AI-powered matching.
          </p>

        </div>

        <button
          className="primary-button"
          onClick={() =>
            onNavigate("jobs")
          }
        >

          <Plus size={18} />

          Create Job

        </button>

      </div>


      <div className="stats-grid">

        <StatCard
          label="Active Jobs"
          value={jobs.length}
          icon={BriefcaseBusiness}
        />

        <StatCard
          label="Candidates"
          value={candidates.length}
          icon={Users}
        />

        <StatCard
          label="Resumes Processed"
          value={candidates.length}
          icon={FileText}
        />

        <StatCard
          label="AI Matching"
          value="Ready"
          icon={Sparkles}
        />

      </div>


      <div className="workflow-card">

        <div className="section-title">

          <div>

            <h3>
              Recruitment Workflow
            </h3>

            <p>
              From job description to candidate analysis.
            </p>

          </div>

        </div>


        <div className="workflow-grid">

          <WorkflowStep
            number="01"
            title="Create Job"
            description="Enter a job description and extract requirements using AI."
            onClick={() =>
              onNavigate("jobs")
            }
          />

          <WorkflowStep
            number="02"
            title="Upload Resume"
            description="Upload candidate PDF or DOCX resumes for AI extraction."
            onClick={() =>
              onNavigate("upload")
            }
          />

          <WorkflowStep
            number="03"
            title="Match Candidates"
            description="Compare skills, experience, projects and education."
            onClick={() =>
              onNavigate("candidates")
            }
          />

          <WorkflowStep
            number="04"
            title="Rank Candidates"
            description="View candidate ranking and detailed skill gaps."
            onClick={() =>
              onNavigate("ranking")
            }
          />

        </div>

      </div>


      <div className="two-column">

        <div className="content-card">

          <div className="section-title">

            <h3>
              Recent Jobs
            </h3>

            <button
              className="text-button"
              onClick={() =>
                onNavigate("jobs")
              }
            >
              View all
            </button>

          </div>

          {jobs.length === 0 ? (

            <EmptyState
              icon={BriefcaseBusiness}
              text="No jobs created yet."
            />

          ) : (

            <div className="mini-list">

              {jobs.slice(0, 4).map(job => (

                <div
                  className="mini-list-item"
                  key={job.id}
                >

                  <div className="list-icon">
                    <BriefcaseBusiness
                      size={17}
                    />
                  </div>

                  <div>

                    <strong>
                      {job.title}
                    </strong>

                    <span>
                      {job.company ||
                        "Company not specified"}
                    </span>

                  </div>

                </div>

              ))}

            </div>

          )}

        </div>


        <div className="content-card">

          <div className="section-title">

            <h3>
              Recent Candidates
            </h3>

            <button
              className="text-button"
              onClick={() =>
                onNavigate("candidates")
              }
            >
              View all
            </button>

          </div>

          {candidates.length === 0 ? (

            <EmptyState
              icon={Users}
              text="No candidates uploaded yet."
            />

          ) : (

            <div className="mini-list">

              {candidates
                .slice(0, 4)
                .map(candidate => (

                  <div
                    className="mini-list-item"
                    key={candidate.id}
                  >

                    <div className="avatar small">

                      {candidate.name
                        ?.charAt(0)
                        ?.toUpperCase()}

                    </div>

                    <div>

                      <strong>
                        {candidate.name}
                      </strong>

                      <span>
                        {candidate.email ||
                          "Email not provided"}
                      </span>

                    </div>

                  </div>

                ))}

            </div>

          )}

        </div>

      </div>

    </section>
  );
}


// ============================================================
// JOBS PAGE
// ============================================================

function JobsPage({
  jobs,
  loading,
  jobText,
  setJobText,
  createJob,
  loadRanking
}) {

  return (
    <section className="page">

      <div className="page-heading">

        <div>

          <h2>
            Job Management
          </h2>

          <p>
            Create jobs and extract requirements using Ollama AI.
          </p>

        </div>

      </div>


      <div className="content-card create-job-card">

        <div className="section-title">

          <div>

            <h3>
              Create New Job
            </h3>

            <p>
              Paste the complete job description below.
            </p>

          </div>

          <Sparkles
            size={22}
          />

        </div>

        <textarea
          className="large-textarea"
          placeholder="Example: We are looking for an AI Engineer with Python, FastAPI, Generative AI, LLMs and RAG experience..."
          value={jobText}
          onChange={event =>
            setJobText(
              event.target.value
            )
          }
        />

        <div className="form-footer">

          <span>
            AI will extract skills, experience, education and responsibilities.
          </span>

          <button
            className="primary-button"
            onClick={createJob}
            disabled={loading}
          >

            {loading ? (
              <Loader2
                size={18}
                className="spin"
              />
            ) : (
              <Sparkles
                size={18}
              />
            )}

            Create Job

          </button>

        </div>

      </div>


      <div className="content-card">

        <div className="section-title">

          <div>

            <h3>
              Your Jobs
            </h3>

            <p>
              Jobs saved in PostgreSQL.
            </p>

          </div>

        </div>


        {jobs.length === 0 ? (

          <EmptyState
            icon={BriefcaseBusiness}
            text="No jobs found."
          />

        ) : (

          <div className="job-grid">

            {jobs.map(job => (

              <div
                className="job-card"
                key={job.id}
              >

                <div className="job-card-header">

                  <div className="list-icon purple">
                    <BriefcaseBusiness
                      size={19}
                    />
                  </div>

                  <span className="job-id">
                    JOB #{job.id}
                  </span>

                </div>

                <h3>
                  {job.title}
                </h3>

                <p className="company-name">
                  {job.company ||
                    "Company not specified"}
                </p>

                <p className="job-description">
                  {job.description}
                </p>

                <div className="skill-tags">

                  {(job.required_skills || [])
                    .slice(0, 6)
                    .map(skill => (

                      <span
                        key={skill}
                        className="skill-tag"
                      >
                        {skill}
                      </span>

                    ))}

                </div>

                <button
                  className="secondary-button full-width"
                  onClick={() =>
                    loadRanking(job.id)
                  }
                >

                  <BarChart3
                    size={17}
                  />

                  View Ranking

                </button>

              </div>

            ))}

          </div>

        )}

      </div>

    </section>
  );
}


// ============================================================
// CANDIDATES PAGE
// ============================================================

function CandidatesPage({
  candidates,
  loading,
  onMatch,
  jobs,
  onUpload
}) {

  return (
    <section className="page">

      <div className="page-heading">

        <div>

          <h2>
            Candidates
          </h2>

          <p>
            Resume profiles extracted by AI.
          </p>

        </div>

        <button
          className="primary-button"
          onClick={onUpload}
        >

          <Upload size={18} />

          Upload Resume

        </button>

      </div>


      {candidates.length === 0 ? (

        <div className="content-card">

          <EmptyState
            icon={Users}
            text="No candidates found. Upload a resume to get started."
          />

        </div>

      ) : (

        <div className="candidate-grid">

          {candidates.map(candidate => (

            <div
              className="candidate-card"
              key={candidate.id}
            >

              <div className="candidate-header">

                <div className="large-avatar">

                  {candidate.name
                    ?.charAt(0)
                    ?.toUpperCase()}

                </div>

                <div>

                  <h3>
                    {candidate.name}
                  </h3>

                  <p>
                    {candidate.email ||
                      "Email not provided"}
                  </p>

                </div>

              </div>


              <div className="candidate-section">

                <span className="field-label">
                  Skills
                </span>

                <div className="skill-tags">

                  {(candidate.skills || [])
                    .slice(0, 8)
                    .map(skill => (

                      <span
                        key={skill}
                        className="skill-tag"
                      >
                        {typeof skill === "string"
                          ? skill
                          : JSON.stringify(skill)}
                      </span>

                    ))}

                </div>

              </div>


              <div className="candidate-actions">

                {jobs.length === 0 ? (

                  <span className="muted-text">
                    Create a job first to match.
                  </span>

                ) : (

                  <select
                    className="job-select"
                    defaultValue=""
                    onChange={event => {

                      if (
                        event.target.value
                      ) {

                        onMatch(
                          Number(
                            event.target.value
                          ),
                          candidate.id
                        );

                      }

                    }}
                  >

                    <option
                      value=""
                    >
                      Match with a job...
                    </option>

                    {jobs.map(job => (

                      <option
                        key={job.id}
                        value={job.id}
                      >
                        {job.title}
                      </option>

                    ))}

                  </select>

                )}

              </div>

            </div>

          ))}

        </div>

      )}

    </section>
  );
}


// ============================================================
// UPLOAD PAGE
// ============================================================

function UploadPage({
  resumeFile,
  setResumeFile,
  uploadResume,
  loading
}) {

  return (
    <section className="page">

      <div className="page-heading">

        <div>

          <h2>
            Upload Candidate Resume
          </h2>

          <p>
            PDF and DOCX files are supported.
          </p>

        </div>

      </div>


      <div className="upload-card">

        <div className="upload-icon">
          <Upload size={32} />
        </div>

        <h3>
          Upload a resume
        </h3>

        <p>
          RecruitAI will extract candidate information using document processing and Ollama.
        </p>


        <label className="file-picker">

          <input
            type="file"
            accept=".pdf,.docx"
            onChange={event =>
              setResumeFile(
                event.target.files?.[0] ||
                null
              )
            }
          />

          <FileText size={18} />

          {resumeFile
            ? resumeFile.name
            : "Choose PDF or DOCX"}

        </label>


        {resumeFile && (

          <div className="selected-file">

            <CheckCircle2
              size={18}
            />

            {resumeFile.name}

          </div>

        )}


        <button
          className="primary-button"
          onClick={uploadResume}
          disabled={
            loading ||
            !resumeFile
          }
        >

          {loading ? (
            <>
              <Loader2
                size={18}
                className="spin"
              />

              Processing Resume...
            </>
          ) : (
            <>
              <Sparkles
                size={18}
              />

              Process Resume
            </>
          )}

        </button>

      </div>

    </section>
  );
}


// ============================================================
// RANKING PAGE
// ============================================================

function RankingPage({
  ranking,
  selectedJob,
  loading,
  onMatch
}) {

  return (
    <section className="page">

      <div className="page-heading">

        <div>

          <p className="eyebrow">
            CANDIDATE RANKING
          </p>

          <h2>
            {selectedJob
              ? selectedJob.title
              : "Candidate Ranking"}
          </h2>

          <p>
            Candidates ranked using weighted matching.
          </p>

        </div>

      </div>


      <div className="content-card">

        {loading ? (

          <div className="loading-inline">

            <Loader2
              size={26}
              className="spin"
            />

            Loading ranking...

          </div>

        ) : ranking.length === 0 ? (

          <EmptyState
            icon={BarChart3}
            text="No ranking results available yet."
          />

        ) : (

          <div className="ranking-table">

            <div className="ranking-row ranking-header">

              <span>
                Rank
              </span>

              <span>
                Candidate
              </span>

              <span>
                Score
              </span>

              <span>
                Matching Skills
              </span>

              <span>
                Missing Skills
              </span>

              <span>
                Action
              </span>

            </div>


            {ranking.map(
              (candidate, index) => (

                <div
                  className="ranking-row"
                  key={
                    candidate.candidate_id ||
                    index
                  }
                >

                  <strong>
                    #{candidate.rank ||
                      index + 1}
                  </strong>

                  <div>

                    <strong>
                      {candidate.candidate_name}
                    </strong>

                    <span>
                      {candidate.candidate_email ||
                        "No email"}
                    </span>

                  </div>

                  <div className="score-pill">

                    {Number(
                      candidate.overall_score ||
                      0
                    ).toFixed(2)}
                    %

                  </div>

                  <div className="table-skills">

                    {(candidate.matching_skills || [])
                      .slice(0, 4)
                      .map(skill => (

                        <span
                          key={skill}
                          className="success-tag"
                        >
                          {skill}
                        </span>

                      ))}

                  </div>

                  <div className="table-skills">

                    {(candidate.missing_skills || [])
                      .slice(0, 4)
                      .map(skill => (

                        <span
                          key={skill}
                          className="danger-tag"
                        >
                          {skill}
                        </span>

                      ))}

                  </div>

                  <button
                    className="small-button"
                    onClick={() =>
                      onMatch(
                        selectedJob.id,
                        candidate.candidate_id
                      )
                    }
                  >
                    Analyze
                  </button>

                </div>

              )
            )}

          </div>

        )}

      </div>

    </section>
  );
}


// ============================================================
// MATCH PAGE
// ============================================================

function MatchPage({
  match,
  candidate,
  job
}) {

  if (!match) {

    return (
      <section className="page">

        <div className="content-card">

          <EmptyState
            icon={BarChart3}
            text="Run a candidate match to view analysis."
          />

        </div>

      </section>
    );

  }


  const componentScores =
    match.component_scores || {};


  return (
    <section className="page">

      <div className="page-heading">

        <div>

          <p className="eyebrow">
            AI MATCH ANALYSIS
          </p>

          <h2>
            {match.candidate_name}
          </h2>

          <p>
            {match.job_title}
          </p>

        </div>

        <div className="big-score">

          {Number(
            match.overall_score || 0
          ).toFixed(2)}
          %

        </div>

      </div>


      <div className="score-grid">

        <ScoreCard
          title="Required Skills"
          value={
            componentScores.required_skills
          }
          weight="40%"
        />

        <ScoreCard
          title="Relevant Experience"
          value={
            componentScores.relevant_experience
          }
          weight="25%"
        />

        <ScoreCard
          title="Projects"
          value={
            componentScores.projects
          }
          weight="20%"
        />

        <ScoreCard
          title="Education & Certifications"
          value={
            componentScores.education_certifications
          }
          weight="10%"
        />

        <ScoreCard
          title="Additional Skills"
          value={
            componentScores.additional_skills
          }
          weight="5%"
        />

      </div>


      <div className="two-column">

        <div className="content-card">

          <div className="section-title">

            <h3>
              Matching Skills
            </h3>

            <CheckCircle2
              size={20}
            />

          </div>

          <div className="large-tags">

            {(match.matching_skills || [])
              .map(skill => (

                <span
                  className="success-tag"
                  key={skill}
                >
                  {skill}
                </span>

              ))}

          </div>

        </div>


        <div className="content-card">

          <div className="section-title">

            <h3>
              Skill Gaps
            </h3>

            <XCircle
              size={20}
            />

          </div>

          <div className="large-tags">

            {(match.missing_skills || [])
              .map(skill => (

                <span
                  className="danger-tag"
                  key={skill}
                >
                  {skill}
                </span>

              ))}

          </div>

        </div>

      </div>


      <div className="content-card explanation-card">

        <div className="section-title">

          <div>

            <h3>
              AI Explanation
            </h3>

            <p>
              Generated by Ollama Llama 3.2.
            </p>

          </div>

          <Sparkles size={22} />

        </div>

        <div className="ai-explanation">

          {match.ai_explanation
            ?.split("\n")
            .map(
              (line, index) => (

                <p
                  key={index}
                >
                  {line}
                </p>

              )
            )}

        </div>

      </div>

    </section>
  );
}


// ============================================================
// SMALL COMPONENTS
// ============================================================

function StatCard({
  label,
  value,
  icon: Icon
}) {

  return (
    <div className="stat-card">

      <div className="stat-icon">
        <Icon size={21} />
      </div>

      <div>

        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>

      </div>

    </div>
  );
}


function WorkflowStep({
  number,
  title,
  description,
  onClick
}) {

  return (
    <button
      className="workflow-step"
      onClick={onClick}
    >

      <span className="workflow-number">
        {number}
      </span>

      <div>

        <strong>
          {title}
        </strong>

        <p>
          {description}
        </p>

      </div>

      <ArrowRight
        size={18}
      />

    </button>
  );
}


function EmptyState({
  icon: Icon,
  text
}) {

  return (
    <div className="empty-state">

      <Icon size={30} />

      <p>
        {text}
      </p>

    </div>
  );
}


function ScoreCard({
  title,
  value,
  weight
}) {

  const score =
    Number(value || 0);

  return (
    <div className="score-card">

      <div>

        <span>
          {title}
        </span>

        <small>
          Weight {weight}
        </small>

      </div>

      <strong>
        {score.toFixed(2)}%
      </strong>

      <div className="progress-bar">

        <div
          className="progress-fill"
          style={{
            width:
              `${Math.min(
                score,
                100
              )}%`
          }}
        />

      </div>

    </div>
  );
}


export default App;