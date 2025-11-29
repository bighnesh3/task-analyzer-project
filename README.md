# Task Prioritization Engine

A robust and extensible task‑ranking system built with Django on the backend and a clean, fully client‑side JavaScript frontend. The engine evaluates tasks using urgency, importance, effort, and dependencies, then produces richly detailed, explainable priority scores. Every part of the pipeline—data validation, default handling, scoring, dependency analysis, warnings, UI messaging, and recommendations—works together to create a smooth, intelligent, and transparent task‑management experience. This project is intentionally structured to be readable, tweakable, and educational, making it easy to understand how and why a task receives the score it does.

---

## Project Overview

This project combines a Django REST API with a responsive, hand‑crafted frontend to deliver a complete task‑analysis tool. Users can input tasks with due dates, estimated hours, dependencies, and importance levels through a simple UI. The system responds with:

* Fully ranked task lists sorted according to the chosen strategy.
* Top‑three recommendations designed to help users decide what to work on first.
* Validation warnings when essential fields are missing, inconsistent, or automatically defaulted.
* Alerts for dependency cycles, past‑due tasks, and suspicious inputs.
* Clear, readable explanations for every score, including breakdowns of urgency, importance, effort weightings, and penalties.

Four different strategies allow users to shift their prioritization styles without modifying the raw task data:

* **Smart Balance** – a well‑rounded model blending urgency, importance, and effort.
* **Fastest Wins** – ideal for knocking out quick tasks by heavily rewarding low effort.
* **High Impact** – emphasizes importance for users who prioritize long‑term effects.
* **Deadline Driven** – dramatically increases urgency weight for time‑sensitive tasks.

The architecture is intentionally transparent: no black‑box behavior, no hidden weights, and no obscure decision rules. Everything is designed to help users—and reviewers—easily follow the system’s logic.

---

## Setup Instructions

### **Clone Repository**

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### **Create and Activate Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate        # Windows
```

### **Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Run Server**

```bash
python manage.py runserver
```

Once the server starts, open the root URL shown in the terminal. The full browser‑based interface is provided at the main route—this offers the best experience for testing, experimentation, and visualizing how the scoring engine behaves with different kinds of input.

---

## Short Summary of API Endpoints

### **POST /api/tasks/analyze/**

Accepts a list of task objects and a chosen strategy. Returns **all** tasks ranked from highest to lowest priority, including details such as past‑due status, dependency issues, defaulted fields, and explanation text.

### **POST /api/tasks/suggest/**

Accepts the same payload but returns **only the top three** recommended tasks. Also surfaces warnings that help the user understand any problems in the input data.

Although the frontend uses these endpoints automatically, they can also be called manually for testing or integration purposes. For everyday use, sticking to the interactive web interface is recommended because it provides instant visual feedback.

---

## Algorithm Explanation

The scoring engine blends several task attributes into a single composite score. It aims to strike a balance between mathematical soundness, transparency, and practical usefulness. Rather than hiding rules inside opaque formulas, the system breaks down its reasoning step by step.

### **Urgency**

Urgency increases as the due date approaches. The scoring engine computes the number of days until a task is due, then converts that into an urgency value. Tasks due far in the future have low urgency; tasks with imminent deadlines rise quickly in priority. Past‑due tasks are never ignored—they receive a significant urgency boost and a strong UI badge that calls attention to them.

### **Importance**

Importance is user‑supplied on a scale of 1–10. It contributes directly and substantially to the final score. When users leave this field blank, a default value of **5** is applied, and the interface makes this clear so users can refine their data later. This balances graceful error handling with honest messaging.

### **Effort**

Effort represents estimated hours needed to complete the task. Lower effort usually bumps the score—especially under the **Fastest Wins** strategy. When left empty, the system uses **1 hour** as a safe default. This choice is intentionally optimistic so tasks do not get wrongly penalized for missing data. Again, badges and warnings make this behavior transparent.

### **Dependencies and Circular Detection**

Tasks can list dependencies by ID. Each dependency introduces a small penalty because the task cannot be started immediately. More importantly, the system includes a cycle‑detection mechanism. If a loop exists—small or large—the involved tasks receive dependency‑cycle warnings and badges so the user can fix their data. Circular tasks still receive a score so they remain visible in the ranking.

### **Strategy Weighting**

Each strategy shifts the mathematical emphasis:

* **Smart Balance** spreads weight evenly to create a stable, well‑rounded score.
* **Fastest Wins** multiplies the effect of effort, strongly favoring quick tasks.
* **High Impact** pushes importance to the forefront, ideal for long‑term outcome focus.
* **Deadline Driven** multiplies urgency weight, ensuring tight schedules receive top priority.

This dynamic model allows users to view their tasks from multiple perspectives without re‑entering or modifying any data.

### **Reasoning Generation**

Every result card includes a breakdown of the reasoning: urgency score, importance score, effort contribution, penalties, defaults applied, and special flags. This makes the engine educational and trustworthy—users never have to guess why a task ended up where it did.

---

## Design Decisions

* Opted for a transparent scoring formula over a machine‑learning model to keep logic predictable and explainable.
* Allowed missing values to be handled gracefully through carefully chosen defaults.
* Implemented validation that informs users without stopping the entire process.
* Included circular dependency detection to maintain structural correctness.
* Kept the frontend framework‑free (vanilla JS) to highlight clarity and reduce overhead.
* Prioritized communication and explanation so users always understand system output.
* Chose a modular architecture so individual components—scoring, validation, parsing—can be improved independently.

---

## Unit Tests

Unit tests live in:

```
backend/tasks/tests.py
```

They validate:

* correctness of the scoring algorithm under different strategies,
* behavior when fields are missing or defaulted,
* circular dependency detection,
* and response shaping.

### **Run Tests**

```bash
python manage.py test
```

The tests cover a meaningful slice of the system while remaining readable and easy to expand.

---

## Time Breakdown

A rough estimate of time spent across major components:

* Backend scaffolding, routing, and serializers: ~45 minutes
* Scoring engine design, mathematical tuning, and explanation logic: ~1.5–2 hours
* Validation rules, default‑handling logic, and dependency cycle checks: ~40–50 minutes
* Frontend HTML/CSS/JS construction and polishing: ~1–1.25 hours
* User‑facing messaging, warning systems, and UI badges: ~30–45 minutes
* Unit tests and debugging sessions: ~45–55 minutes
* Full integration testing, refinement, and UX fixes: ~1–1.25 hours

This distribution reflects a focus on transparency and correctness over stylistic complexity.

---

## Bonus Challenges Attempted

* Adjustable scoring model with multiple distinct strategies.
* Cycle‑detection logic for dependency graphs.
* Highly readable scoring explanations.
* A complete browser interface without external UI libraries.
* Validation system combining client and server safeguards.
* Meaningful unit tests supporting the scoring model.
* Dynamic warnings and badges reflecting backend decisions.

---

## Future Improvements

* **Calendar‑Aware Urgency:** Incorporate weekends, holidays, and working hours into urgency calculations to reflect realistic scheduling constraints.
* Add persistent storage, user accounts, and long‑term task history.
* Provide a graphical dependency map showing relationships visually.
* Introduce categories, color‑coding, filtering, and sorting tools.
* Add analytics that show how scores change as fields are updated.
* Offer optional AI‑guided weight suggestions based on task history.
* Implement drag‑and‑drop task editing and richer UI interactions.

##
