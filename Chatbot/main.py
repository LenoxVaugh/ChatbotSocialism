from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from pyvi.ViTokenizer import tokenize

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure Gemini API Key using environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Chatbot class
class VietnamHistoryBot:
    def __init__(self):
        self.historical_events = {
            "khởi nghĩa hai bà trưng": {
                "năm": "40-43",
                "mô tả": "Cuộc khởi nghĩa do Hai Bà Trưng lãnh đạo chống lại ách đô hộ của nhà Hán",
                "nhân vật": ["Trưng Trắc", "Trưng Nhị"]
            },
            "chiến thắng bạch đằng": {
                "năm": "938",
                "mô tả": "Ngô Quyền đánh thắng quân Nam Hán, chấm dứt 1000 năm Bắc thuộc",
                "nhân vật": ["Ngô Quyền"]
            },
            "nhà lý": {
                "năm": "1009-1225",
                "mô tả": "Triều đại phong kiến độc lập do Lý Công Uẩn sáng lập",
                "nhân vật": ["Lý Công Uẩn", "Lý Thái Tổ", "Lý Thường Kiệt"]
            }
        }
        
        self.historical_figures = {
            "lê lợi": "Anh hùng dân tộc, người lãnh đạo khởi nghĩa Lam Sơn (1418-1427)",
            "trần hưng đạo": "Danh tướng thời Trần, ba lần đánh thắng quân Nguyên Mông",
            "ngô quyền": "Người chấm dứt thời kỳ Bắc thuộc năm 938",
            "hai bà trưng": "Hai chị em anh hùng lãnh đạo khởi nghĩa chống Hán năm 40",
            "quang trung": "Vị vua anh minh của nhà Tây Sơn, đánh thắng quân Thanh năm 1789"
        }

    def extract_keywords(self, text):
        # Tokenize input text using Pyvi
        tokens = tokenize(text).lower().split()
        return tokens

    def respond(self, user_input):
        keywords = self.extract_keywords(user_input)
        print(f"Keywords extracted: {keywords}")  # Debugging

        # Search in historical figures
        for keyword in keywords:
            if keyword in self.historical_figures:
                return f"{keyword.title()}: {self.historical_figures[keyword]}"
    
        # Search in historical events
        for keyword in keywords:
            if keyword in self.historical_events:
                event = self.historical_events[keyword]
                return f"Về {keyword}:\nNăm: {event['năm']}\n{event['mô tả']}\nCác nhân vật liên quan: {', '.join(event['nhân vật'])}"

        # Use Gemini API if no match found
        return self.ask_gemini(user_input)

    def ask_gemini(self, user_input):
        # Xây dựng payload cho Gemini API
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": user_input
                        }
                    ]
                }
            ]
        }

        # Thực hiện yêu cầu đến Gemini API
        response = requests.post(
            url,
            headers=headers,
            params={"key": GEMINI_API_KEY},
            json=payload
        )

        # Kiểm tra trạng thái HTTP
        if response.status_code == 200:
            try:
                # In ra phản hồi thô từ Gemini API để kiểm tra
                print("Gemini API Raw Response:", response.text)

                # Thử phân tích JSON của phản hồi
                result = response.json()
                print("Parsed Gemini API Response:", result)

                # Lấy nội dung từ phần trả lời
                content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [])
                if content:
                    full_text = ''.join([part.get('text', '') for part in content])
                    
                    # Loại bỏ dấu ** bôi đậm trong phản hồi
                    full_text = full_text.replace("**", "")
                    return full_text.strip()
                else:
                    return "Không tìm thấy nội dung trong phản hồi."
            except Exception as e:
                print(f"Error parsing Gemini API response: {str(e)}")
                return "Xin lỗi, tôi gặp vấn đề khi xử lý câu trả lời từ Gemini."
        else:
            # In ra mã lỗi nếu có vấn đề với yêu cầu API
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return f"Gemini API gặp sự cố: {response.status_code} - {response.text}"
# Initialize chatbot
bot = VietnamHistoryBot()

@app.route('/')
def home():
    return render_template('index.html')  # Create a simple HTML interface

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        response = bot.respond(user_message)
        
        return jsonify({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
