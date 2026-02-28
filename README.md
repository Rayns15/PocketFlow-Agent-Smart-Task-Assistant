# 🚀 Smart Task Assistant

Smart Task Assistant is an interactive, terminal-based productivity tool powered by Python, **PocketFlow**, and local LLMs. It goes beyond simple to-do lists by utilizing AI to automatically break down tasks into actionable micro-steps, estimate workloads, and track your deadlines.

## ✨ Features

* **Interactive CLI Dashboard:** A clean, easy-to-use terminal menu to create, view, complete, or delete tasks.
* **AI-Powered Task Breakdown:** Uses **Ollama** (running `gemma:2b`) to automatically analyze new tasks, split them into micro-steps, and estimate completion times.
* **Bilingual Date Parsing:** Leverages `dateparser` to understand natural language deadlines in both English and Romanian (e.g., "Tomorrow at 5pm" or "astăzi la ora 16:45").
* **Proactive Deadline Tracking:** Automatically alerts you to tasks that are overdue or due within the next hour.
* **Persistent Storage:** Saves all tasks, metadata, and AI breakdowns safely to a `tasks.yaml` file.
* **Graph-Based Execution:** Built using PocketFlow, routing logic through clearly defined nodes (Validation, Categorization, Processing, etc.).

---

## 📋 Prerequisites

Before running the assistant, ensure you have the following installed on your system:

1. **Python 3.8+**
2. **Ollama:** You must have Ollama installed and running locally.
3. **Gemma Model:** Pull the required LLM model via your terminal:
```bash
ollama pull gemma:2b

```



---

## 🛠️ Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/Rayns15/Smart-Task-Assistant.git
cd smart-task-assistant

```

**2. Install dependencies**
While the `requirements.txt` specifically calls out PocketFlow, you will also need the libraries used for dates, yaml, and LLM communication. Install them using:

```bash
pip install pocketflow pyyaml ollama dateparser

```

**3. Run the application**

```bash
python main.py

```

---

## 🏗️ Project Architecture

This project is built using a directed graph flow to manage state and logic. Here is how the files interact:

* **`main.py`**: The application entry point. Initializes an empty shared dictionary and starts the PocketFlow graph.
* **`flow.py`**: Defines the application's routing logic. It connects user inputs to validation, logic branching (high vs. low priority), execution nodes, saving, and reporting.
* **`nodes.py`**: The core engine containing the PocketFlow `Node` classes:
* `InputTaskNode`: Renders the CLI menu and captures user choices.
* `CategorizeNode` & `ValidationNode`: Checks input validity and determines task priority based on keywords.
* `ProcessNode`: Contacts the local Ollama LLM to generate micro-steps and parses dates.
* `UpdateTaskNode` & `DeleteTaskNode`: Handles completing and removing tasks from the board.
* `SaveNode`: Writes the current state to `tasks.yaml`.
* `SummaryNode`: Calculates total workload times and prints the current task board.
* `CheckDeadlinesNode`: Evaluates task schedules against the current system time to trigger alerts.


* **`utils.py`**: Contains helper functions, such as `get_current_timestamp()` for standardizing default times.
* **`tasks.yaml`**: Your local database where task lists, AI outputs, and schedules are stored.

---

## 💻 Usage Guide

Upon running `main.py`, you will be greeted by the Main Menu:

```text
========================================
🎛️  MAIN MENU
1. 📝 Create a new task
2. ✅ Mark task as done
3. 🗑️ Delete task
4. 📋 View task board
5. 🚪 Exit
========================================

```

* **Creating a task:** When you select `1`, the assistant will ask for a description, priority, and deadline. The LLM will then pause to "think" and print out a structured YAML plan for your task.
* **Viewing the board:** Selecting `4` provides a neat summary of all tasks, their parsed deadlines, and a calculated total estimated workload in hours and minutes.

---