import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from essig_ai import ChatBot, ChatBotError
from dotenv import load_dotenv


load_dotenv()



bot_chat = ChatBot(os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
app.secret_key = os.urandom(24)

USER = "admin"
PASSWORD = "admin"


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['password']
        if username == USER and password == PASSWORD:
            session['email'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

        

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.json.get('prompt')
    try:
        response_text = bot_chat.send_message(prompt)
        return jsonify(response_text)
    except ChatBotError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
