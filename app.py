from flask import Flask, render_template, request, jsonify, session
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

llm = Ollama(model="llama2")
output_parser = StrOutputParser()

@app.route('/')
def index():
    # Clear chat and config on new session
    session.clear()
    return render_template('chat.html')

@app.route('/set-config', methods=['POST'])
def set_config():
    data = request.json
    domain = data.get("domain")
    ai_name = data.get("ai_name")

    if not domain or not ai_name:
        return jsonify({"error": "Domain and AI name required"}), 400

    # Store in session
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

    # Create prompt dynamically from history
    messages = [(msg["role"], msg["content"]) for msg in session['chat_history']]
    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | output_parser

    response = chain.invoke({})
    session['chat_history'].append({"role": "assistant", "content": response})
    session.modified = True

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
