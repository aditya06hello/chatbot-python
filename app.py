from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS  # Import CORS
from gtts import gTTS
import os
import openai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up your OpenAI API key (replace with your actual key)
openai.api_key = "sk-_5wd5PXniVTcS4iPY4InxR_mjmHQp9O7G5No9pwVWWT3BlbkFJn2B3w0ca-cGYAWyeTx5ioZK1G8Ltb3Z6g5mWIln2AA"  # Replace with your OpenAI key

# Generate a response using GPT (ChatGPT)
def get_gpt_answer(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access to it
            messages=[
                {"role": "system", "content": "You are an expert in health-related questions."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        answer = response['choices'][0]['message']['content'].strip()
        print(f"GPT Answer: {answer}")
        return answer
    except Exception as e:
        print(f"Error getting GPT answer: {e}")
        return "উত্তর পাওয়া যায়নি। দয়া করে আবার চেষ্টা করুন।"  # Return a message in Bengali if GPT fails

# Generate audio response using gTTS
def generate_audio(text, filename='static/response.mp3'):
    os.makedirs('static', exist_ok=True)
    if text.strip():
        tts = gTTS(text=text, lang='bn')
        tts.save(filename)
        print(f"Audio generated and saved to {filename}.")
    else:
        print("No text to convert to audio.")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get('text', "")
    
    if not user_question:
        return make_response(jsonify({'response_text': 'দয়া করে একটি প্রশ্ন লিখুন।'}), 400)
    
    # Get an answer from GPT
    answer = get_gpt_answer(user_question)
    
    # Generate audio response using gTTS
    generate_audio(answer)
    
    # Send back the text and audio response
    response = jsonify({'response_text': answer})
    return make_response(response, 200)

@app.route('/response.mp3')
def get_audio():
    if os.path.exists('static/response.mp3'):
        return send_file('static/response.mp3', mimetype='audio/mpeg')
    else:
        return make_response(jsonify({'error': 'Audio file not found.'}), 404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
