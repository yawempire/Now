from flask import Blueprint, json, jsonify, render_template, redirect, request, url_for, flash
from . import db
from .forms import RegistrationForm, LoginForm
from .models.user import User
from flask_jwt_extended import create_access_token
import os
import json
import google.generativeai as genai
main = Blueprint('main', __name__)

@main.route('/home')
def home():
    return render_template('0-index.html')

# Register Route
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('User already exists', 'danger')
            return redirect(url_for('main.register'))
        
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)
 
# Login Route
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            access_token = create_access_token(identity={'username': user.username})
            flash('Logged in successfully', 'success')
            # Here you can redirect to a protected page or set a session
            return redirect(url_for('main.home'))
        
        flash('Invalid credentials', 'danger')

    return render_template('login.html', title='Log In', form=form)

@main.route('/start_quiz/<category>')
def start_quiz1(category):
    # Logic to start the quiz based on category
    return render_template('quiz.html', category=category)


# Set up generation config
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="pretend that you are a chat application, ask me questions related to SCIENCE with 4 options, only one is correct."
)

# Store active chat sessions
chat_sessions = {}

@main.route('/generate_question', methods=['POST'])
def generate_question():
    topic = request.json.get('topic')
    
    if not topic:
        return jsonify({"error": "No topic provided."}), 400

    # Start a new chat session with the model
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    f"Generate a quiz question about {topic}. The response should be formatted as JSON with the following keys:\n\n- \"question\": The quiz question text.\n- \"options\": An object with keys \"A\", \"B\", \"C\", and \"D\", representing four answer choices.\n- \"correct_answer\": The key (A, B, C, or D) corresponding to the correct answer.\n\nFor example, the output should look like this:\n\n{{\n    \"question\": \"What is the chemical symbol for water?\",\n    \"options\": {{\n        \"A\": \"H2O\",\n        \"B\": \"O2\",\n        \"C\": \"CO2\",\n        \"D\": \"NaCl\"\n    }},\n    \"correct_answer\": \"A\"\n}}\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Please provide me with the topic you would like the quiz question to be about.",
                ],
            },
        ]
    )

    # Send the message to generate the question
    response = chat_session.send_message("Generate the quiz question.")

    # Log the raw response text
    raw_response_text = response.text
    print("Raw response text from model:", raw_response_text)
    cleaned_response_text = raw_response_text.strip().replace("\\", "")
    # Attempt to parse the response
    try:
        # Assuming the raw response text is already formatted correctly
        question_data = json.loads(cleaned_response_text)
        return jsonify(question_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse question data.", "raw_response": cleaned_response_text}), 500

@main.route('/start_quiz', methods=['POST'])
def start_quiz():
    user_id = request.json.get('user_id')
    topic = request.json.get('topic', 'general knowledge')  # Default to 'general knowledge' if topic is not provided

    # Construct the prompt
    prompt = (
        f"Please generate a quiz question about {topic}. "
        "The response should be formatted as JSON with the following keys: "
        "'question', 'options' (which should contain keys A, B, C, and D), "
        "and 'correct_answer'. "
        "For example: {\"question\": \"What is the chemical symbol for water?\", "
        "\"options\": {\"A\": \"H2O\", \"B\": \"O2\", \"C\": \"CO2\", \"D\": \"NaCl\"}, "
        "\"correct_answer\": \"A\"}"
    )

    # Start a new chat session with the model using the constructed prompt
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [prompt],
            },
        ]
    )

    # Save session for the user
    chat_sessions[user_id] = chat_session

    # Inspect the structure of chat_session.history
    last_message = chat_session.history[-1]

    # Extract the text content from the last message
    if hasattr(last_message, 'parts') and last_message.parts:
        response_text = last_message.parts[0].text.strip()  # Assuming parts[0] contains a text attribute
    else:
        return jsonify({"error": "No message generated."}), 500

    # Debugging: Print the raw response text
    print("Raw response text from model:", response_text)  # Add this line

    # Parse the response text
    try:
        question_data = json.loads(response_text)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse question data."}), 500
    except TypeError as e:
        return jsonify({"error": str(e)}), 500

    # Ensure question_data has expected keys
    if not all(key in question_data for key in ["question", "options", "correct_answer"]):
        return jsonify({"error": "Incomplete question data returned."}), 500

    # Return the structured question data
    return jsonify({
        "message": "Quiz started!",
        "question": {
            "text": question_data["question"],
            "options": question_data["options"],
            "correct_answer": question_data["correct_answer"]
        }
    })


@main.route('/submit_answer', methods=['POST'])
def submit_answer():
    user_id = request.json.get('user_id')
    user_answer = request.json.get('answer')

    if user_id not in chat_sessions:
        return jsonify({"error": "No active session found for this user."}), 404

    chat_session = chat_sessions[user_id]

    # Send the user's answer to the model
    response = chat_session.send_message(user_answer)

    # Clean feedback response
    feedback = response.text.strip()  # Clean up whitespace and newlines

    return jsonify({"feedback": feedback, "next_question": response.text.strip()})  # Cleaned up response