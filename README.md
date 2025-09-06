# AI-Powered Communication Assistant

**A Submission for the AI Engineer Fresher Coding Challenge**

This project is my approach to building an end-to-end solution for a common, high-impact business problem: managing customer support emails. My goal was to move beyond simple filtering and create a truly intelligent tool that automates the tedious work and empowers support teams to be more efficient and effective.

## 1. The Core Problem I Aimed to Solve

Support teams are constantly flooded with emails. This makes it incredibly difficult to identify urgent issues, provide consistent answers, and respond to customers in a timely manner. I wanted to build a tool that could bring order to this chaos by automating the entire triage process.

## 2. My Solution: The Intelligent Triage Dashboard

I developed a full-stack application that acts as a "mission control" for a support inbox. It connects directly to a Gmail account and provides a clean, interactive dashboard that turns a messy inbox into a prioritized and actionable work queue.

Here’s a breakdown of the key functionalities:
*   **Smart Ingestion**: The system fetches all new, unread emails, ensuring no message is missed. It then marks them as read to prevent duplicate processing.
*   **Multi-Layered AI Analysis**: Each email goes through a sophisticated AI pipeline to understand it on multiple levels:
    *   **Sentiment**: Is the customer happy or frustrated?
    *   **Priority**: Does this require immediate attention?
    *   **Intent**: What is the user's actual goal (e.g., a technical problem, a sales inquiry, a billing question)?
*   **Automated Triage and Prioritization**: Based on the analysis, emails are automatically sorted so that the most critical and high-value items always appear at the top.
*   **Context-Aware Response Generation (RAG)**: Using a local knowledge base, the system drafts accurate, professional, and empathetic replies for common queries. For complex issues, it summarizes the problem and recommends human intervention.
*   **Actionable Insights Dashboard**: All of this is presented in a user-friendly interface that includes not just the email list, but also at-a-glance analytics and interactive charts to visualize the workload.

## 3. Architecture and Tech Stack

I chose a modern and practical tech stack to build this solution, focusing on performance, reliability, and ease of development.

*   **Backend**: **Python** with **FastAPI**. I selected FastAPI for its incredible speed, asynchronous support, and automatic API documentation, which is perfect for building high-performance web services.
*   **AI & NLP Models**:
    *   **Hugging Face Transformers**: I used the `distilbert-base-uncased-finetuned-sst-2-english` model for fast and accurate sentiment analysis. It's efficient enough to run locally without significant overhead.
    *   **OpenAI GPT-4o**: For the more complex tasks of intent classification and context-aware response generation, I leveraged the power of GPT-4o. Its advanced reasoning and JSON mode were essential for creating the structured AI responses.
*   **Email Integration**: The official **Google Gmail API** for robust and secure access to the user's inbox.
*   **Frontend**: A lightweight and responsive single-page application built with vanilla **HTML, CSS, and JavaScript**. For the interactive analytics, I integrated the popular **Chart.js** library.

**High-Level Data Flow:**
`Gmail Inbox` → `Email Fetcher (Gmail API)` → `FastAPI Backend` → `AI Pipeline (Sentiment -> Priority -> Intent -> RAG)` → `Prioritization & Sorting` → `JSON API Response` → `Frontend Dashboard (HTML/JS/Chart.js)`

## 4. Key Features That Make This Project Stand Out

I focused on adding innovative features that would provide real-world value and demonstrate a deeper level of thinking.

*   **Intelligent Intent Classification**: The system goes beyond basic keyword matching. It understands the *purpose* of an email, allowing it to differentiate between a standard query, an angry complaint, and a valuable sales opportunity.
*   **"Smart Insights" at a Glance**: To save agents time, the dashboard automatically extracts and displays key information as colorful tags, including contact details (phones, emails), specific user needs (like "refund" or "pricing"), and sentiment-driving words.
*   **A Seamless Human-in-the-Loop Workflow**: My favorite feature is the **"Reply in Gmail" button**. When an email is flagged for human review, the agent doesn't have to search for it. A single click opens a pre-filled Gmail compose window, perfectly bridging the gap between AI suggestion and human action.
*   **Live Analytics & Stats**: The dashboard includes a "mission control" stats bar and an interactive chart, giving users a real-time overview of email volume, sentiment trends, and workload breakdown.

## 5. How to Set Up and Run the Project

Follow these steps to get the application running on your local machine.

**1. Prerequisites:**
*   Python 3.8 or newer
*   A Google Cloud Project with the **Gmail API** enabled.
*   An **OpenAI API Key**.

**2. Installation:**
*   Clone this repository: `git clone [your-repo-url]`
*   Navigate to the project directory and create a virtual environment:
    ```
    python -m venv venv
    ```
*   Activate the environment:
    *   On Windows: `venv\Scripts\activate`
    *   On macOS/Linux: `source venv/bin/activate`
*   Install the required libraries:
    ```
    pip install -r requirements.txt
    ```

**3. Configuration:**
*   Place your downloaded `credentials.json` file from the Google Cloud Console into the root directory of the project.
*   Create a file named `.env` in the root directory.
*   Add your OpenAI API key to the `.env` file like this:
    ```
    OPENAI_API_KEY="your-secret-api-key-here"
    ```
*   Populate the `knowledge_base.txt` file with any information you want the AI to use when answering questions.

**4. Running the Application:**
*   Start the backend server with auto-reload enabled:
    ```
    uvicorn main:app --reload
    ```
*   Open the `index.html` file in your web browser.
*   On the first run, the application will open a new browser tab asking you to authorize access to your Gmail account. Please approve the permissions to continue.

