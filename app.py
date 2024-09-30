from flask import Flask, request, jsonify, send_file, make_response
from gtts import gTTS
import wikipedia
import os
import openai

app = Flask(__name__)

# Set up your OpenAI API key (replace with your actual key)
openai.api_key = "sk-_5wd5PXniVTcS4iPY4InxR_mjmHQp9O7G5No9pwVWWT3BlbkFJn2B3w0ca-cGYAWyeTx5ioZK1G8Ltb3Z6g5mWIln2AA"

# Generate a response using GPT (ChatGPT)
def get_gpt_answer(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access to it
            messages=[{"role": "system", "content": "You are an expert in health-related questions."},
                      {"role": "user", "content": question}],
            max_tokens=150,
            temperature=0.7,
        )
        answer = response['choices'][0]['message']['content'].strip()
        print(f"GPT Answer: {answer}")
        return answer
    except Exception as e:
        print(f"Error getting GPT answer: {e}")
        return None

# Search Wikipedia for the answer
def search_wikipedia(query):
    try:
        wikipedia.set_lang("bn")  # Set language to Bengali
        
        # Get a summary from Wikipedia
        summary = wikipedia.summary(query, sentences=2)
        if summary:
            return summary
        
    except wikipedia.exceptions.DisambiguationError as e:
        # If disambiguation occurs, list possible options
        return f"অনুগ্রহ করে আরো নির্দিষ্ট করুন: {', '.join(e.options)}"
    
    except wikipedia.exceptions.PageError:
        return "দুঃখিত, আমি সেই বিষয়ে কিছু খুঁজে পাইনি।"
    
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
        return "দুঃখিত, আমি উত্তর জানি না।"

    return "দুঃখিত, আমি উত্তর জানি না।"

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
    
    # If GPT could not generate a response, use Wikipedia as fallback
    if not answer:
        answer = search_wikipedia(user_question)
    
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
    app.run(debug=True)
