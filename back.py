import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template_string, render_template
import psycopg2
from urllib.parse import urlparse
import re

app = Flask(__name__)

# Parse the PostgreSQL connection URL
url = urlparse('postgresql://Hackaton_owner:CEJBvaSpU93G@ep-dark-scene-a26591bu.eu-central-1.aws.neon.tech/Hackaton?sslmode=require')

# Connection details
db_config = {
    'dbname': url.path[1:],
    'user': url.username,
    'password': url.password,
    'host': url.hostname,
    'port': url.port,
    'sslmode': 'require'
}

# Laptop model class
class Laptop:
    def __init__(self, id, name, processor, ram, video_card, storage, category, price, photo, url):
        self.id = id
        self.name = name
        self.processor = processor
        self.ram = ram
        self.video_card = video_card
        self.storage = storage
        self.category = category
        self.price = price
        self.photo = photo
        self.url = url

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'processor': self.processor,
            'ram': self.ram,
            'video_card': self.video_card,
            'storage': self.storage,
            'category': self.category,
            'price': self.price,
            'photo': self.photo,
            'url': self.url
        }

# Initialize the database
def init_db():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS laptops (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            processor VARCHAR(255) NOT NULL,
            ram VARCHAR(255) NOT NULL,
            video_card VARCHAR(255) NOT NULL,
            storage VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            price FLOAT NOT NULL,
            photo INTEGER NOT NULL,
            url VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# # Endpoint to get data from the laptops table
# @app.route('/laptops', methods=['GET'])
# def get_laptops():
#     conn = psycopg2.connect(**db_config)
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM laptops')
#     laptops = cur.fetchall()
#     cur.close()
#     conn.close()
#
#     laptops_list = [
#         Laptop(
#             id=laptop[0],
#             name=laptop[1],
#             processor=laptop[2],
#             ram=laptop[3],
#             video_card=laptop[4],
#             storage=laptop[5],
#             category=laptop[6],
#             price=laptop[7],
#             photo=laptop[8],
#             url=laptop[9]
#         ).to_dict()
#         for laptop in laptops
#     ]
#     return jsonify(laptops_list)

# Endpoint to get data from the laptops table
@app.route('/laptops', methods=['GET'])
def get_laptops():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute('SELECT * FROM laptops')
        laptops = cur.fetchall()
        cur.close()
        conn.close()

        laptops_list = [
            {
                'name': laptop[1],
                'processor': laptop[2],
                'ram': laptop[3],
                'video_card': laptop[4],
                'storage': laptop[5],
                'category': laptop[6],
                'price': laptop[7],
                'photo': laptop[8],
                'url': laptop[9]
            }
            for laptop in laptops
        ]

        return render_template('laptops.html', laptops=laptops_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sample laptops data
def get_sample_laptops():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute('SELECT * FROM laptops')
    laptops = cur.fetchall()
    cur.close()
    conn.close()

    return [
        Laptop(
            id=laptop[0],
            name=laptop[1],
            processor=laptop[2],
            ram=laptop[3],
            video_card=laptop[4],
            storage=laptop[5],
            category=laptop[6],
            price=laptop[7],
            photo=laptop[8],
            url=laptop[9]
        ) for laptop in laptops
    ]

# Helper function to extract numbers from strings
def extract_number(s):
    match = re.search(r'\d+', s)
    return int(match.group()) if match else 0

# Endpoint to get laptop recommendations
@app.route('/recommend', methods=['POST'])
def recommend_laptops():
    try:
        questionnaire = request.get_json()
        if not questionnaire:
            return jsonify({'error': 'Invalid JSON data'}), 400

        budget = questionnaire.get('budget')
        usage = questionnaire.get('usage')
        preferred_brand = questionnaire.get('preferred_brand')
        min_ram = questionnaire.get('min_ram')
        min_storage = questionnaire.get('min_storage')

        # Convert budget, min_ram, and min_storage to appropriate types
        budget = float(budget) if budget else None
        min_ram = int(min_ram) if min_ram else None
        min_storage = int(min_storage) if min_storage else None

        laptops = get_sample_laptops()

        recommendations = []

        for laptop in laptops:
            if (budget and laptop.price > budget):
                continue
            if (min_ram and extract_number(laptop.ram) < min_ram):
                continue
            if (min_storage and extract_number(laptop.storage) < min_storage):
                continue
            if (preferred_brand and preferred_brand.lower() not in laptop.name.lower()):
                continue

            recommendations.append(laptop.to_dict())

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Load the trained model and scaler
knn = joblib.load('knn_model.pkl')
scaler = joblib.load('scaler.pkl')

# Load the laptops dataset
laptops_df = pd.read_csv('laptops.csv')

# Function to convert storage to GB
def convert_storage_to_gb(storage):
    storage = storage.lower().replace('flash storage', '').replace('ssd', '').replace('hdd', '').replace('emmc', '').strip()
    if 'tb' in storage:
        return int(float(storage.replace('tb', '').strip()) * 1024)
    elif 'gb' in storage:
        return int(storage.replace('gb', '').strip())
    return 0

# Apply the conversion to storage column
laptops_df['storage'] = laptops_df['storage'].apply(convert_storage_to_gb)

# Remove the 'GB' suffix from the RAM column and convert it to integer
laptops_df['ram'] = laptops_df['ram'].str.replace('GB', '').astype(int)
laptops_df['price'] = laptops_df['price'].astype(float)

# Function to get recommendations
def get_recommendations(ram, storage, price):
    query = np.array([[ram, storage, price]])
    query_scaled = scaler.transform(query)
    distances, indices = knn.kneighbors(query_scaled)
    return laptops_df.iloc[indices[0]].to_dict(orient='records')

# Endpoint to get laptop recommendations
@app.route('/recommend_chat', methods=['POST'])
def recommend_laptops_chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        ram = data.get('min_ram')
        storage = data.get('min_storage')
        budget = data.get('budget')

        if not (ram and storage and budget):
            return jsonify({'error': 'Missing required fields'}), 400

        # Convert ram, storage, and budget to appropriate types
        ram = int(ram)
        storage = int(storage)
        budget = float(budget)

        recommendations = get_recommendations(ram, storage, budget)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def questionnaire_form():
    form_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Laptop Recommendation Chat</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 20px;
            background-color: #1b1b1b;
            color: #ffffff;
        }
        h1 {
            color: #ff9900;
            text-align: center;
            margin-bottom: 30px;
        }
        .chat-box {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #333;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        .message {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #444;
            border-radius: 5px;
            color: #fff;
        }
        .message.bot {
            text-align: left;
            color: #fff;
        }
        .message.user {
            text-align: right;
            background-color: #555;
        }
        .input-container {
            max-width: 600px;
            align-self: center;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        input[type="text"], input[type="number"] {
            flex-grow: 1;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #ccc;
            background-color: #555;
            color: #fff;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            background-color: #ff9900;
            color: #000;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #ff9900;
        }
        .home-button, .refresh-button {
            display: block;
            width: 120px;
            margin: 20px auto;
            padding: 10px;
            text-align: center;
            background-color: #ff9900;
            color: #000;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .home-button:hover, .refresh-button:hover {
            background-color: #ffcc80;
        }
        .recommendation-container {
            display: none;
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #333;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        .recommendation {
            margin-bottom: 10px;
            padding: 10px;
            background-color: #444;
            border-radius: 5px;
            color: #fff;
        }
    </style>
</head>
<body>
    <h1>Laptop Recommendation Chat</h1>
    <embed name="PH" src="/static/music.mp3" loop="true" autostart="true" hidden="true">
    <div class="chat-box" id="chatBox">
        <div class="message bot">Welcome! Let's find the perfect laptop for you.</div>
        <div class="message bot" id="question">What's your budget? ($)</div>
    </div>
    <div class="input-container">
        <input type="text" id="userInput" placeholder="Type your answer...">
        <button onclick="submitAnswer()">Send</button>
    </div>
    <!-- Updated home button -->
    <a href="http://localhost:5277" class="home-button">Back to Home</a>
    <!-- Refresh button -->
    <button class="refresh-button" onclick="refreshChat()">Refresh</button>
    <!-- Recommendation container -->
    <div class="recommendation-container" id="recommendationContainer">
        <div class="message bot">Getting recommendations...</div>
    </div>
    <script>
        const questions = [
            "What's your budget? ($)",
            "What will you use the laptop for? (e.g., Gaming, Work, School)",
            "Do you have a preferred brand?",
            "What's the minimum RAM you need? (GB)",
            "What's the minimum storage you need? (GB)"
        ];

        let currentQuestionIndex = 0;
        let answers = {};

        function typeBotMessage(message, delay) {
            const chatBox = document.getElementById('chatBox');
            const botMessage = document.createElement('div');
            botMessage.classList.add('message', 'bot');
            const cursor = document.createElement('span');
            cursor.classList.add('cursor');
            botMessage.appendChild(cursor);
            chatBox.appendChild(botMessage);

            let charIndex = 0;
            const typeEffect = setInterval(() => {
                botMessage.lastChild.textContent += message.charAt(charIndex);
                charIndex++;
                if (charIndex > message.length) {
                    clearInterval(typeEffect);
                }
            }, delay);
        }

        function submitAnswer() {
            const userInput = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');

            if (userInput.value.trim() === '') return;

            const userMessage = document.createElement('div');
            userMessage.classList.add('message', 'user');
            userMessage.textContent = userInput.value;
            chatBox.appendChild(userMessage);

            answers[currentQuestionIndex] = userInput.value;

            userInput.value = '';
            currentQuestionIndex++;

            if (currentQuestionIndex < questions.length) {
                typeBotMessage(questions[currentQuestionIndex], 50);
            } else {
                sendRecommendationRequest();
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function sendRecommendationRequest() {
            const chatBox = document.getElementById('chatBox');
            const recommendationContainer = document.getElementById('recommendationContainer');
            const noResultsContainer = document.getElementById('noResultsContainer');

            const loadingMessage = document.createElement('div');
            loadingMessage.classList.add('message', 'bot');
            loadingMessage.textContent = 'Getting recommendations...';
            chatBox.appendChild(loadingMessage);

            const data = {
                budget: answers[0],
                usage: answers[1],
                preferred_brand: answers[2],
                min_ram: answers[3],
                min_storage: answers[4]
            };

            fetch('/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(recommendations => {
                chatBox.removeChild(loadingMessage);

                if (recommendations.error) {
                    const errorMessage = document.createElement('div');
                    errorMessage.classList.add('message', 'bot');
                    errorMessage.textContent = `Error: ${recommendations.error}`;
                    chatBox.appendChild(errorMessage);
                } else if (recommendations.length === 0) {
                    const noResultsMessage = document.createElement('div');
                    noResultsMessage.classList.add('message', 'bot');
                    noResultsMessage.textContent = "We couldn't find any products matching your specifications.";
                    noResultsMessage.appendChild()
                    chatBox.appendChild(noResultsMessage);

                    noResultsContainer.style.display = 'block';
                } else {
                    recommendationContainer.style.display = 'block'; // Show recommendation container

                    recommendations.forEach(laptop => {
                        const laptopMessage = document.createElement('div');
                        laptopMessage.classList.add('recommendation');
                        laptopMessage.innerHTML = `
                            <strong>${laptop.name}</strong><br>
                            Processor: ${laptop.processor}<br>
                            RAM: ${laptop.ram}<br>
                            Video Card: ${laptop.video_card}<br>
                            Storage: ${laptop.storage}<br>
                            Category: ${laptop.category}<br>
                            Price: $${laptop.price}<br>
                            <a href="${laptop.url}" style="color: #ffc107;">More info</a>
                        `;
                        recommendationContainer.appendChild(laptopMessage);
                    });
                }

                chatBox.scrollTop = chatBox.scrollHeight;
            });
        }

        function refreshChat() {
            currentQuestionIndex = 0;
            answers = {};
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML = `
                <div class="message bot">Welcome! Let's find the perfect laptop for you.</div>
                <div class="message bot" id="question">What's your budget? ($)</div>
            `;
            document.getElementById('userInput').value = '';
            document.getElementById('recommendationContainer').style.display = 'none';
            document.getElementById('recommendationContainer').innerHTML = '<div class="message bot">Getting recommendations...</div>';
            document.getElementById('noResultsContainer').style.display = 'none';
        }

        function playAudioAndRedirect() {
            const audio = document.getElementById('noResultsAudio');
            audio.play();
            audio.onended = function() {
                window.location.href = 'https://www.pornhub.com';
            };
        }
    </script>
</body>
</html>
    '''
    return render_template_string(form_html)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
