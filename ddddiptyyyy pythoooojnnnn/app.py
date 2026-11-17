from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import csv
from textblob import TextBlob

app = Flask(__name__)

EVENTS_FILE = "events.csv"
FEEDBACK_FILE = "feedback.csv"

# Initialize CSV Files
def init_files():
    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Event ID", "Event Name", "Date", "Venue", "Description"])

    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Event ID", "Student Name", "Rating", "Comments", "Sentiment"])

init_files()

@app.route('/')
def home():
    return render_template('index.html')

# Get all events
@app.route('/api/events', methods=['GET'])
def get_events():
    df = pd.read_csv(EVENTS_FILE)
    return jsonify(df.to_dict(orient='records'))

# Add new event
@app.route('/api/add_event', methods=['POST'])
def add_event():
    data = request.json
    df = pd.read_csv(EVENTS_FILE)
    
    event_id = len(df) + 1
    new_event = {
        "Event ID": event_id,
        "Event Name": data['name'],
        "Date": data['date'],
        "Venue": data['venue'],
        "Description": data['description']
    }
    
    df = pd.concat([df, pd.DataFrame([new_event])], ignore_index=True)
    df.to_csv(EVENTS_FILE, index=False)
    return jsonify({"success": True, "message": "Event created successfully!"})

# Submit Feedback with Sentiment Analysis
@app.route('/api/add_feedback', methods=['POST'])
def add_feedback():
    data = request.json
    df = pd.read_csv(FEEDBACK_FILE)

    comment = data['comments']
    
    # Sentiment Analysis using TextBlob
    analysis = TextBlob(comment)
    if analysis.sentiment.polarity > 0.1:
        sentiment = "Positive"
    elif analysis.sentiment.polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    new_feedback = {
        "Event ID": int(data['event_id']),
        "Student Name": data['student_name'],
        "Rating": int(data['rating']),
        "Comments": comment,
        "Sentiment": sentiment
    }

    df = pd.concat([df, pd.DataFrame([new_feedback])], ignore_index=True)
    df.to_csv(FEEDBACK_FILE, index=False)
    return jsonify({"success": True, "message": "Feedback submitted successfully!"})

# Get Feedback Analysis
@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    df_fb = pd.read_csv(FEEDBACK_FILE)
    
    if df_fb.empty:
        return jsonify({"has_data": False})

    sentiment_counts = df_fb['Sentiment'].value_counts().to_dict()
    avg_rating = round(df_fb['Rating'].mean(), 2)

    return jsonify({
        "has_data": True,
        "total_feedbacks": len(df_fb),
        "avg_rating": avg_rating,
        "positive": sentiment_counts.get("Positive", 0),
        "neutral": sentiment_counts.get("Neutral", 0),
        "negative": sentiment_counts.get("Negative", 0)
    })

if __name__ == '__main__':
    app.run(debug=True)