from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import google.generativeai as genai
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

genai.configure(api_key="AIzaSyCWMhElsvio4Loo7Ie6URFcFr6Arv1vdeU")
model = genai.GenerativeModel("gemini-2.0-flash-exp")

@app.route('/')
def index():
    session.clear()
    return render_template('chat.html')

@app.route('/set-config', methods=['POST'])
def set_config():
    data = request.json
    domain = data.get("domain")
    ai_name = data.get("ai_name")

    if not domain or not ai_name:
        return jsonify({"error": "Domain and AI name required"}), 400

    session['domain'] = domain
    session['ai_name'] = ai_name
    session['chat_history'] = [
        {"role": "system", "content": f"You are a helpful AI assistant named {ai_name}. "
                                      f"You are an expert in {domain}. Be friendly and expressive with emojis."}
    ]
    return jsonify({"message": "Configuration set successfully"})

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    if 'chat_history' not in session:
        return jsonify({"error": "AI configuration not set"}), 400

    session['chat_history'].append({"role": "user", "content": user_query})

    # Build conversation string
    conversation = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" 
                              for msg in session['chat_history']])

    # Get Gemini response
    response = model.generate_content(conversation)
    ai_reply = response.text

    session['chat_history'].append({"role": "assistant", "content": ai_reply})
    session.modified = True

    return jsonify({"response": ai_reply})

if __name__ == '__main__':
    app.run(debug=True)
