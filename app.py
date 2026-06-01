from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
import sqlite3
import os
import json
import re

app = Flask(__name__)
DB_PATH = "chatbot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)
    # Seed FAQ data
    faqs = [
        ("What are your business hours?", "We're open Monday–Friday, 9 AM to 6 PM IST. Weekend support is available via email.", "hours"),
        ("How do I reset my password?", "Click 'Forgot Password' on the login page, enter your email, and follow the reset link sent to your inbox.", "account"),
        ("What payment methods do you accept?", "We accept all major credit/debit cards, UPI, net banking, and PayPal.", "billing"),
        ("How can I track my order?", "Log in to your account, go to 'My Orders', and click on the order to see real-time tracking.", "orders"),
        ("What is your return policy?", "We offer a 30-day return policy for all items in original condition. Initiate a return from your account dashboard.", "returns"),
        ("How do I contact support?", "You can reach us via this chatbot, email at support@example.com, or call +91-XXXXXXXXXX during business hours.", "support"),
        ("Do you offer discounts?", "Yes! We offer seasonal discounts, loyalty rewards, and referral bonuses. Subscribe to our newsletter for exclusive deals.", "billing"),
        ("How long does shipping take?", "Standard shipping takes 3-5 business days. Express shipping (1-2 days) is available at checkout.", "orders"),
    ]
    c.execute("SELECT COUNT(*) FROM faqs")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO faqs (question, answer, category) VALUES (?,?,?)", faqs)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def find_faq_answer(user_msg):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT question, answer FROM faqs")
    faqs = c.fetchall()
    conn.close()
    user_lower = user_msg.lower()
    keywords = {
        "hours": ["hours", "open", "time", "working", "schedule"],
        "password": ["password", "reset", "forgot", "login", "access"],
        "payment": ["payment", "pay", "card", "upi", "billing", "method"],
        "order": ["order", "track", "tracking", "delivery", "shipment"],
        "return": ["return", "refund", "policy", "exchange"],
        "support": ["contact", "support", "help", "reach", "phone"],
        "discount": ["discount", "offer", "deal", "coupon", "reward"],
        "shipping": ["shipping", "ship", "days", "deliver", "how long"],
    }
    best_match = None
    best_score = 0
    for faq in faqs:
        score = 0
        q_lower = faq["question"].lower()
        for word in user_lower.split():
            if len(word) > 3 and word in q_lower:
                score += 2
        for kw_list in keywords.values():
            for kw in kw_list:
                if kw in user_lower and kw in q_lower:
                    score += 3
        if score > best_score:
            best_score = score
            best_match = faq["answer"]
    return best_match if best_score >= 3 else None

def generate_response(user_msg, session_id):
    user_lower = user_msg.lower().strip()
    # Greetings
    if any(w in user_lower for w in ["hi", "hello", "hey", "good morning", "good afternoon"]):
        return "Hello! 👋 Welcome to our support chatbot. I'm here to help you with orders, payments, returns, and more. What can I assist you with today?"
    # Thanks
    if any(w in user_lower for w in ["thank", "thanks", "thank you", "great", "awesome"]):
        return "You're welcome! 😊 Is there anything else I can help you with?"
    # Bye
    if any(w in user_lower for w in ["bye", "goodbye", "exit", "quit"]):
        return "Goodbye! Have a great day. Feel free to come back if you need any help! 👋"
    # FAQ match
    faq_answer = find_faq_answer(user_msg)
    if faq_answer:
        return faq_answer
    # Conversation history context
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role, message FROM conversations WHERE session_id=? ORDER BY id DESC LIMIT 6", (session_id,))
    history = c.fetchall()
    conn.close()
    # Default intelligent response
    if any(w in user_lower for w in ["problem", "issue", "error", "not working", "broken"]):
        return "I'm sorry you're experiencing issues! 😔 Could you please describe the problem in more detail? You can also contact our support team at support@example.com or call during business hours (Mon–Fri, 9AM–6PM IST)."
    if any(w in user_lower for w in ["account", "profile", "settings"]):
        return "For account-related queries, please log in to your dashboard at myaccount.example.com. If you're having trouble accessing your account, I can guide you through the password reset process."
    if any(w in user_lower for w in ["price", "cost", "how much", "fee"]):
        return "Our pricing varies by product and plan. Could you specify what you're looking for? You can also check our pricing page at example.com/pricing for detailed information."
    return "I'm not sure I fully understood your query. Could you rephrase or provide more details? You can ask me about:\n• Business hours\n• Orders & tracking\n• Payments & billing\n• Returns & refunds\n• Account issues\n• Contacting support"

def log_message(session_id, role, message):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO conversations (session_id, role, message, timestamp) VALUES (?,?,?,?)",
              (session_id, role, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id", "default")
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400
    log_message(session_id, "user", user_msg)
    response = generate_response(user_msg, session_id)
    log_message(session_id, "bot", response)
    return jsonify({
        "response": response,
        "timestamp": datetime.now().strftime("%H:%M"),
        "session_id": session_id
    })

@app.route("/api/history/<session_id>")
def history(session_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role, message, timestamp FROM conversations WHERE session_id=? ORDER BY id", (session_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/stats")
def stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM conversations")
    total = c.fetchone()["total"]
    c.execute("SELECT COUNT(DISTINCT session_id) as sessions FROM conversations")
    sessions = c.fetchone()["sessions"]
    c.execute("SELECT COUNT(*) as user_msgs FROM conversations WHERE role='user'")
    user_msgs = c.fetchone()["user_msgs"]
    conn.close()
    return jsonify({"total_messages": total, "sessions": sessions, "user_messages": user_msgs})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
