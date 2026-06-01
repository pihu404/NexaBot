# 🤖 NexaBot — AI-Powered Customer Support Chatbot

A full-stack AI chatbot for customer support and FAQs, built with Python (Flask) and SQLite.

## Features
- 💬 Natural language FAQ matching with keyword scoring
- 📜 Persistent conversation logs per session
- 📊 Real-time stats (total messages, sessions, user interactions)
- 🎨 Modern dark-themed UI with typing indicators and quick suggestions
- 💾 SQLite database for storing conversations and FAQs
- 🔌 RESTful API (`/api/chat`, `/api/history`, `/api/stats`)

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask |
| NLP | Keyword scoring + intent classification |
| Database | SQLite |
| Frontend | HTML5, CSS3, Vanilla JS |

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/nexabot.git
cd nexabot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
# http://localhost:5000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a message, get bot response |
| GET | `/api/history/<session_id>` | Retrieve chat history for a session |
| GET | `/api/stats` | Get global conversation statistics |

### POST `/api/chat`
```json
Request:  { "message": "What are your business hours?", "session_id": "abc123" }
Response: { "response": "We're open Mon-Fri...", "timestamp": "14:35", "session_id": "abc123" }
```

## Project Structure
```
chatbot/
├── app.py              # Flask backend + NLP logic
├── requirements.txt
├── chatbot.db          # SQLite DB (auto-created)
└── templates/
    └── index.html      # Frontend UI
```

## Extending the Chatbot
- Add more FAQs directly to the `faqs` list in `app.py`
- Integrate Hugging Face Transformers for advanced NLP
- Add user authentication for personalized history
- Deploy on Render / Railway / AWS EC2

## Author
Built as part of the Codec Technologies AI/ML internship project.
