import json
import os
from flask import Flask, render_template, request, jsonify
from thefuzz import fuzz  # Install via: pip install thefuzz

app = Flask(__name__)

# Load Knowledge Base
DATA_FILE = 'config.json'

def load_knowledge_base():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

kb = load_knowledge_base()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').lower().strip()
    
    # Filter unrelated questions (Simple heuristic)
    irrelevant_terms = ['movie', 'weather', 'joke', 'news']
    if any(term in user_input for term in irrelevant_terms):
        return jsonify({
            "response": "I specialize in CDP technical support (Segment, mParticle, Lytics, Zeotap). Please ask about data integration, profiles, or segments.",
            "match_score": 0
        })

    best_match_answer = None
    best_match_score = 0
    matched_platform = None

    # Iterate through platforms and their questions
    for platform, entries in kb.items():
        for entry in entries:
            # Combine keywords for better matching coverage
            keyword_text = " ".join(entry['keywords'])
            
            # Calculate similarity ratio
            score = fuzz.partial_ratio(user_input, keyword_text)
            
            # If this is the highest score so far, update it
            if score > best_match_score and score >= 70: # Threshold of 70%
                best_match_score = score
                best_match_answer = entry['answer']
                matched_platform = platform

    if best_match_answer:
        return jsonify({
            "response": f"**Platform: {matched_platform.capitalize()}**\n\n{best_match_answer}",
            "match_score": best_match_score
        })
    else:
        return jsonify({
            "response": "I couldn't find a direct match for that question. Please try rephrasing your query or check the official documentation for Segment, mParticle, Lytics, or Zeotap.",
            "match_score": 0
        })

if __name__ == '__main__':
    # Ensure dependencies are installed
    # pip install flask thefuzz
    app.run(debug=True)