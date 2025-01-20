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
class CNXHKHBot:
    def __init__(self):
        # Từ khóa chính
        self.core_concepts = {
            "chủ nghĩa xã hội khoa học": {
                "định nghĩa": "Học thuyết khoa học về những quy luật vận động của xã hội từ CNTB lên CNXH",
                "người sáng lập": ["Karl Marx", "Friedrich Engels"],
                "nội dung cơ bản": ["quy luật về sự phù hợp của quan hệ sản xuất với trình độ phát triển của lực lượng sản xuất",
                                  "quy luật về mối quan hệ giữa cơ sở hạ tầng và kiến trúc thượng tầng",
                                  "quy luật về vai trò của đấu tranh giai cấp"]
            },
            "duy vật biện chứng": {
                "định nghĩa": "Phương pháp luận khoa học về mối liên hệ phổ biến và sự phát triển",
                "nguyên lý cơ bản": ["mối liên hệ phổ biến", "phát triển", "mâu thuẫn"]
            },
            "duy vật lịch sử": {
                "định nghĩa": "Khoa học về những quy luật phát triển của xã hội",
                "nội dung": ["tồn tại xã hội quyết định ý thức xã hội", 
                            "cơ sở hạ tầng quyết định kiến trúc thượng tầng"]
            }
        }

        # Giai cấp và tổ chức
        self.class_concepts = {
            "giai cấp công nhân": "Giai cấp tiên tiến, đại diện cho lực lượng sản xuất tiên tiến",
            "giai cấp vô sản": "Giai cấp không có tư liệu sản xuất, phải bán sức lao động",
            "giai cấp tư sản": "Giai cấp sở hữu tư liệu sản xuất chủ yếu của xã hội",
            "đảng cộng sản": "Đội tiên phong của giai cấp công nhân, được trang bị lý luận Mác-Lênin"
        }

        # Quá trình phát triển
        self.development_concepts = {
            "cách mạng xã hội": "Sự thay đổi căn bản trong đời sống xã hội",
            "cách mạng vô sản": "Cuộc cách mạng do giai cấp vô sản lãnh đạo",
            "chuyên chính vô sản": "Chính quyền của giai cấp công nhân và nhân dân lao động",
            "xây dựng cnxh": "Quá trình cải tạo xã hội cũ và xây dựng xã hội mới"
        }

        # Các nhà tư tưởng
        self.theorists = {
            "marx": "Người sáng lập chủ nghĩa xã hội khoa học",
            "engels": "Người cùng sáng lập chủ nghĩa xã hội khoa học với Marx",
            "lenin": "Người phát triển chủ nghĩa Mác trong thời đại đế quốc chủ nghĩa",
            "hồ chí minh": "Người vận dụng sáng tạo chủ nghĩa Mác-Lênin vào Việt Nam"
        }

        # Negative keywords để tránh
        self.negative_keywords = [
            "chủ nghĩa tư bản",
            "chủ nghĩa đế quốc",
            "chủ nghĩa phát xít",
            "chủ nghĩa cơ hội",
            "xét lại",
            "giáo điều"
        ]

    def extract_keywords(self, text):
        # Tokenize input text using Pyvi
        tokens = tokenize(text).lower().split()
        # Remove negative keywords
        tokens = [token for token in tokens if token not in self.negative_keywords]
        return tokens

    def respond(self, user_input):
        keywords = self.extract_keywords(user_input)
        print(f"Keywords extracted: {keywords}")  # Debugging

        # Check intent keywords
        intent_keywords = ["là gì", "định nghĩa", "giải thích", "phân tích", "vai trò", "ý nghĩa", "nội dung", "bản chất"]
        has_intent = any(intent in user_input.lower() for intent in intent_keywords)

        # Search in core concepts
        for keyword in keywords:
            if keyword in self.core_concepts:
                concept = self.core_concepts[keyword]
                if has_intent:
                    return f"{keyword.title()}: {concept['định nghĩa']}"
                return f"Về {keyword}:\nĐịnh nghĩa: {concept['định nghĩa']}\nNgười sáng lập: {', '.join(concept.get('người sáng lập', []))}\nNội dung cơ bản: {', '.join(concept.get('nội dung cơ bản', []))}"

        # Search in class concepts
        for keyword in keywords:
            if keyword in self.class_concepts:
                return f"{keyword.title()}: {self.class_concepts[keyword]}"

        # Search in development concepts
        for keyword in keywords:
            if keyword in self.development_concepts:
                return f"{keyword.title()}: {self.development_concepts[keyword]}"

        # Search in theorists
        for keyword in keywords:
            if keyword in self.theorists:
                return f"{keyword.title()}: {self.theorists[keyword]}"

        # Use Gemini API if no match found
        return self.ask_gemini(user_input)

    def ask_gemini(self, user_input):
        # Thêm ngữ cảnh CNXHKH vào prompt
        context = """Trả lời với tư cách là một chatbot chuyên về chủ nghĩa xã hội khoa học. 
        Chỉ trả lời các câu hỏi liên quan đến CNXHKH và các khái niệm liên quan.
        Trả lời ngắn gọn, súc tích và dễ hiểu."""
        
        prompt = f"{context}\n\nCâu hỏi: {user_input}"

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            url,
            headers=headers,
            params={"key": GEMINI_API_KEY},
            json=payload
        )

        if response.status_code == 200:
            try:
                result = response.json()
                content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [])
                if content:
                    full_text = ''.join([part.get('text', '') for part in content])
                    full_text = full_text.replace("**", "")
                    return full_text.strip()
                else:
                    return "Xin lỗi, tôi không tìm thấy thông tin phù hợp về chủ nghĩa xã hội khoa học cho câu hỏi của bạn."
            except Exception as e:
                print(f"Error parsing Gemini API response: {str(e)}")
                return "Xin lỗi, tôi gặp vấn đề khi xử lý câu trả lời."
        else:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này."

# Initialize chatbot
bot = CNXHKHBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Không có câu hỏi được cung cấp'}), 400
        
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