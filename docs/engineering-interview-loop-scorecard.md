# Engineering Interview Loop and Scorecard

## Hiring Principles

- Bias toward builders who can ship useful product increments under ambiguity.
- Evaluate execution ownership, not just coding fluency.
- Use structured rubrics and calibration to reduce false positives from charisma or pedigree.

## Interview Loop (5 stages)

### Stage 1 — Recruiter / Founder Screen (30 min)

**Owner:** Founder or hiring manager

**Purpose:** Confirm baseline fit before spending engineering bandwidth.

**Signals to collect:**
- Mission motivation and reason for joining early-stage environment
- Communication clarity and ownership language ("I did" vs "we did")
- Basic role constraints (timezone overlap, compensation band, start timeline)

**Exit rule:**
- Pass only if candidate demonstrates clear motivation for startup execution and acceptable logistics.

---

### Stage 2 — Technical Depth Screen (45 min)

**Owner:** Founding Engineer

**Purpose:** Validate core coding and debugging fundamentals in the stack.

**Format:**
- 10 min: project deep-dive from candidate
- 25 min: live debugging/coding prompt
- 10 min: tradeoff discussion

**Signals to collect:**
- Problem decomposition speed
- Correctness under time pressure
- Ability to explain tradeoffs and constraints
- Use of tests/verification instincts

**Exit rule:**
- Pass only if candidate is independently productive at day-1 contributor level.

---

### Stage 3 — Systems Thinking Interview (60 min)

**Owner:** Senior engineer / Founding Engineer

**Purpose:** Assess ability to design reliable systems and reason about failure modes.

**Format:**
- Architecture scenario relevant to product domain
- Deep dive on scaling, observability, and operational risks

**Signals to collect:**
- Clear requirements capture before solutioning
- Sound architectural choices and tradeoff awareness
- Reliability thinking (monitoring, rollback, incident handling)
- Security and data integrity awareness

**Exit rule:**
- Pass only if candidate can propose pragmatic architecture with explicit tradeoffs and risk controls.

---

### Stage 4 — Execution Ownership Simulation (75 min)

**Owner:** Founding Engineer + cross-functional partner (PM/Founder)

**Purpose:** Measure end-to-end ownership from ambiguous requirement to shipped plan.

**Format:**
- Candidate receives a realistic product issue
- Produces implementation approach, milestones, risks, and verification strategy
- 15 min playback + Q&A

**Signals to collect:**
- Converts ambiguity into executable scope
- Prioritization and sequencing quality
- Dependency/risk management
- Definition of done quality and measurable outcomes

**Exit rule:**
- Pass only if candidate shows ownership behavior consistent with autonomous execution.

---

### Stage 5 — Values & Collaboration (45 min)

**Owner:** Founder or leadership partner

**Purpose:** Validate collaboration style and cultural contribution.

**Signals to collect:**
- Feedback receptiveness
- Low-ego, high-accountability behavior
- Partnering effectiveness across functions
- Ethical judgment and user empathy

**Exit rule:**
- Pass only if candidate demonstrates strong trust-building behaviors.

## Scorecard Rubric

Use 1–4 scale for each competency:
- **1 — Below bar:** Significant gaps; would require heavy support.
- **2 — Borderline:** Partial signal; concerns remain in core job requirements.
- **3 — Meets bar:** Solid independent contributor signal.
- **4 — Raises bar:** Exceptional signal with repeatable impact.

### Competency A: Coding & Debugging (Weight: 35%)

Evaluate:
- Produces correct, maintainable code
- Debugs systematically
- Uses verification (tests, checks, instrumentation)
- Balances speed with quality

Red flags:
- Jumps to code without understanding constraints
- Cannot recover from debugging dead-ends
- Skips verification entirely

### Competency B: Systems Thinking (Weight: 30%)

Evaluate:
- Frames requirements and constraints clearly
- Designs with reliability, observability, and security in mind
- Makes explicit tradeoffs
- Anticipates failure modes and recovery paths

Red flags:
- Hand-wavy scaling/reliability answers
- No monitoring or rollback strategy
- Over-engineering disconnected from business need

### Competency C: Execution Ownership (Weight: 35%)

Evaluate:
- Breaks work into executable milestones
- Identifies dependencies and unblock paths
- Makes decisions with limited information
- Drives to clear definition of done and outcome

Red flags:
- Treats planning as deliverable instead of shipping
- Defers critical decisions without rationale
- No explicit accountability for outcomes

## Pass/Fail Guidance (False-Positive Reduction)

### Decision rules

- **Strong Hire:**
  - No competency below 3
  - Weighted average >= 3.3
  - At least one competency at 4
  - No critical red flags

- **Hire:**
  - No competency below 3
  - Weighted average >= 3.0
  - No unresolved execution-ownership concerns

- **No Hire:**
  - Any competency at 1
  - Two or more competencies at 2
  - Weighted average < 3.0
  - Any unmitigated integrity/collaboration red flag

### Guardrails to reduce false positives

1. **Evidence-only scoring:** every score requires concrete observed behavior.
2. **Independent write-up before debrief:** interviewers submit scores before group discussion.
3. **Bar-raiser veto on ownership risk:** if execution ownership is below bar, do not hire despite strong coding.
4. **Counter-signal check:** for every strong score, interviewer must note one risk area.
5. **Reference prompt alignment:** references must explicitly validate ownership and reliability claims.

## Debrief Template (Use in final panel)

- Recommendation: Strong Hire / Hire / No Hire
- Top 3 evidence points
- Top 2 risks and mitigation confidence
- Competency scores (A/B/C)
- Final rationale tied to role requirements

## Implementation Notes

- Revisit rubric calibration after first 5 hires.
- Track interview-to-offer and 6-month performance correlation to refine thresholds.
