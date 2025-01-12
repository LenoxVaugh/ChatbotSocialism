from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Sử dụng mô hình từ Hugging Face (ở đây sử dụng mô hình 'distilbert-base-uncased' cho câu trả lời tự động)
# Bạn có thể thay đổi mô hình theo yêu cầu của mình
question_answerer = pipeline("question-answering", model="distilbert-base-uncased")

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message')

    # Xử lý câu hỏi và lấy câu trả lời từ mô hình
    try:
        context = "Lịch sử Việt Nam là một phần quan trọng của lịch sử Đông Nam Á. Việt Nam đã trải qua nhiều giai đoạn lịch sử quan trọng từ thời kỳ phong kiến, các cuộc chiến tranh với các quốc gia láng giềng, đến thời kỳ hiện đại."
        
        # Mô hình Hugging Face sẽ trả về câu trả lời dựa trên câu hỏi và ngữ cảnh
        result = question_answerer(question=user_message, context=context)
        return jsonify({'response': result['answer'], 'source': 'huggingface'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
