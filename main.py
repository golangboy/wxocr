import wcocr
import os
import uuid
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
wcocr.init("/app/wx/opt/wechat/wxocr", "/app/wx/opt/wechat")

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        # Get base64 image from request
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Extract image format and base64 data
        try:
            prefix, base64_string = image_data.split(',', 1)
            image_format = prefix.split(';')[0].split(':')[1].split('/')[1]  # Extract 'png', 'jpeg', etc.
        except:
            return jsonify({'error': 'Invalid image data format.  Expected "data:image/<format>;base64,<data>"'}), 400


        # Create temp directory if not exists
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Generate unique filename and save image
        filename = os.path.join(temp_dir, f"{str(uuid.uuid4())}.{image_format}")
        try:
            image_bytes = base64.b64decode(base64_string)
            with open(filename, 'wb') as f:
                f.write(image_bytes)

            # Process image with OCR
            result = wcocr.ocr(filename)
            return jsonify({'result': result})

        finally:
            # Clean up temp file
            if os.path.exists(filename):
                os.remove(filename)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)