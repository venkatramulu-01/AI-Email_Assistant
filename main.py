import os
from dotenv import load_dotenv
from openai import OpenAI
from transformers import pipeline
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the email fetching function
from email_fetcher import fetch_and_filter_emails

# --- FastAPI App Initialization ---
# This creates our web server application.
app = FastAPI()

# This is important for allowing our HTML file to talk to this Python backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- AI & NLP MODELS SETUP (same as before) ---
load_dotenv()

# This part can be slow, so we do it once when the server starts.
print("Loading sentiment analysis model...")
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("Model loaded successfully.")


# --- HELPER FUNCTIONS (same as before) ---
def analyze_sentiment(text):
    result = sentiment_analyzer(text)
    return result[0]['label']

def determine_priority(text):
    urgent_keywords = ["urgent", "critical", "immediately", "cannot access", "down"]
    if any(keyword in text.lower() for keyword in urgent_keywords):
        return "Urgent"
    return "Not Urgent"

def extract_information(text):
    """
    Extracts detailed information from the email body, including contacts,
    keyword counts, and sentiment indicators.
    """
    # Use sets to avoid duplicate contacts
    phone_numbers = set(re.findall(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})', text))
    email_addresses = set(re.findall(r'[\w\.-]+@[\w\.-]+', text))

    # Define keywords to scan for customer requirements
    requirement_keywords = ["order", "purchase", "refund", "cancel", "pricing", "invoice"]
    detected_requirements = {kw for kw in requirement_keywords if kw in text.lower()}

    # Define sentiment indicators
    positive_indicators = {"thank", "great", "love", "happy", "awesome", "excellent"}
    negative_indicators = {"problem", "issue", "frustrated", "angry", "bad", "cannot"}
    
    detected_positive_words = {word for word in positive_indicators if word in text.lower()}
    detected_negative_words = {word for word in negative_indicators if word in text.lower()}

    return {
        "phone_numbers": list(phone_numbers),
        "email_addresses": list(email_addresses),
        "requirements": list(detected_requirements),
        "positive_words": list(detected_positive_words),
        "negative_words": list(detected_negative_words)
    }


# ... (keep all your existing code from the top down to this function) ...

def generate_response_and_classify_intent(email_body, sentiment, priority):
    """
    This function now performs two tasks:
    1. Classifies the email's intent.
    2. Generates a draft response or recommends human review.
    """
    try:
        with open("knowledge_base.txt", "r") as f:
            knowledge = f.read()

        # This is our new, more advanced prompt!
        prompt = f"""
        You are an AI Triage System. Analyze the following customer email and perform two tasks:
        1.  **Classify the intent** of the email into one of these categories:
            - "General Inquiry": The user is asking a simple question (e.g., about features, hours, etc.).
            - "Technical Support": The user is facing a technical problem (e.g., login issue, bug, error).
            - "Billing Question": The user has a question about invoices, payments, or pricing.
            - "Sales Lead": The user is expressing interest in buying or upgrading a service. This is high value.
            - "Urgent Complaint": The user is very frustrated, angry, or threatening to leave. This requires immediate human attention.

        2.  **Determine the next action**:
            - If the intent is "General Inquiry" or "Technical Support" AND the answer is clearly in the knowledge base, set the action to "Auto-Reply" and draft a response.
            - If the intent is "Sales Lead" or "Urgent Complaint", set the action to "Flag for Human Review" and write a brief summary of why (e.g., "High-value sales lead.").
            - If the answer is NOT in the knowledge base, set the action to "Flag for Human Review" and write a summary.

        **Knowledge Base for context:**
        ---
        {knowledge}
        ---

        **Customer Email Body:**
        "{email_body}"

        **Return your response ONLY in the following JSON format:**
        {{
          "intent": "category",
          "action": "Auto-Reply OR Flag for Human Review",
          "response_or_summary": "Your generated text here"
        }}
        """

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4o", # Using a more powerful model for better classification
            messages=[
                {"role": "system", "content": "You are a precise AI classification and response engine."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} # Force the model to output JSON
        )
        
        # The response is now a JSON string, so we need to parse it.
        import json
        result = json.loads(completion.choices[0].message.content)
        return result

    except Exception as e:
        if "insufficient_quota" in str(e):
            print("-> OpenAI quota exceeded. Generating a mock triage response.")
            # Mock a more advanced response for the demo
            if "critical issue" in email_body.lower():
                return {
                    "intent": "Technical Support",
                    "action": "Auto-Reply",
                    "response_or_summary": "Dear Customer,\n\nI'm sorry to hear you're having a critical issue with account access. To reset your password, please visit the 'Account' page and click 'Forgot Password'.\n\nIf this doesn't resolve your issue, our team will investigate immediately.\n\nThe Support Team"
                }
            else: # Fallback for other potential emails
                return {
                    "intent": "General Inquiry",
                    "action": "Flag for Human Review",
                    "response_or_summary": "User is asking a general question not found in the knowledge base."
                }
        else:
            return {
                "intent": "Error",
                "action": "Flag for Human Review",
                "response_or_summary": f"An unexpected error occurred: {e}"
            }


# --- API ENDPOINT ---
# This is the URL our frontend will call.
@app.get("/process-emails")
def process_emails_endpoint():
    """
    This endpoint fetches, analyzes, and triages support emails,
    then returns the structured data.
    """
    print("Received request to process and triage emails...")
    
    emails = fetch_and_filter_emails()
    
    processed_data = []
    
    if not emails:
        print("No new support emails to process.")
        return {"data": []}
    
    for email in emails:
        body = email['body']
    
        # --- THE FIX: Truncate the body for the sentiment model ---
        truncated_body = body[:512] # Use the first 512 characters for analysis
    
        sentiment = analyze_sentiment(truncated_body) # Analyze the SHORTER version
        priority = determine_priority(body) # Use the FULL body for keyword search
        extracted_info = extract_information(body)
    
        # Call our upgraded function
        triage_result = generate_response_and_classify_intent(body, sentiment, priority)

        
        processed_data.append({
            "sender": email["sender"],
            "subject": email["subject"],
            "body": body,
            "received_date": email["date"],
            "sentiment": sentiment,
            "priority": priority,
            "extracted_info": extracted_info,
            # Add the new triage data
            "intent": triage_result.get("intent", "N/A"),
            "action": triage_result.get("action", "N/A"),
            "response_or_summary": triage_result.get("response_or_summary", "N/A")
        })
        
        # --- NEW: Prioritization Logic ---
    # Assign a priority score to each email before sorting.
    for email in processed_data:
        score = 1  # Default score
        if email['priority'] == 'Urgent':
            score = 10
        elif email['sentiment'] == 'NEGATIVE':
            score = 5
        email['priority_score'] = score
    
    # Sort the list of emails by the priority score in descending order.
    # This acts as our priority queue.
    sorted_emails = sorted(processed_data, key=lambda e: e['priority_score'], reverse=True)
    
    print(f"Triaged and prioritized {len(sorted_emails)} emails successfully.")
    return {"data": sorted_emails}


