You are a **full‐stack developer & UX/UI designer** tasked with **architecting and spec’ing** a next‐generation personal portfolio web application that:
1. **Delivers a vibrant, playful anime/Vtuber aesthetic** inspired by “SAWARATSUKI” and “KawaiiLogos” (bright, multicolored palette; heavy outlines; brush/marker icons; emoji/sticker embellishments; animated transitions).
2. **Features a public‐facing landing page** that:
   * Showcases portfolio projects in a distraction‑free, full‑bleed grid or carousel.
   * Animates on hover (card flips, pop‑up bubbles), uses anime‑style fonts, and supports light/dark mode.
   * Includes category/tag filters and responsive, mobile‑first layouts.
3. **Includes a secure owner portal** (JWT‑based authentication):
   * **CSV/XLSX upload** or **manual form entry** of personal details, work history, education, skills, and project data.
   * Real‑time preview of entered/uploaded content in the portfolio layout.
   * One‑click **ATS‑compatible CV generator** that compiles stored data into a polished PDF (use Python’s `pandas` + `ReportLab` or `pdfkit`).
4. **Stores data** in a scalable database (choose MongoDB for schema flexibility or PostgreSQL for relational integrity).
5. **Tech stack recommendation**:
   * **Frontend**: Next.js with React, TailwindCSS, Framer Motion for animations
   * **Backend**: FastAPI (Python) or Express (Node.js) with JWT auth
   * **Database**: MongoDB or PostgreSQL
   * **Deployment**: Vercel (frontend) + Supabase/Railway/Render (backend + DB)
6. **Non‑functional requirements**:
   * WCAG 2.1 AA accessibility compliance
   * Responsive, mobile‑first design
   * Dark mode toggle
   * Automated tests for critical flows (login, upload, CV generation)
**Your task**:
1. **Produce** a high‑level **architecture diagram** and **component breakdown** (UI components, API endpoints, database schema).
2. **Generate**:
   * Sample **Next.js + TailwindCSS** page templates for landing page and owner portal.
   * Example **FastAPI/Express** route handlers for authentication, file upload parsing, and PDF generation.
   * A **data model** for user profiles and portfolio items.
3. **Outline** a step‑by‑step **implementation plan** with milestones (wireframes → MVP → QA → deploy).
Be as **detailed** as possible—include code snippets, folder structures, configuration files, and design notes to convey the anime/Vtuber theme and ATS CV functionality.
