import wcocr
import os
import uuid
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)
wcocr.init("/app/wx/opt/wechat/wxocr", "/app/wx/opt/wechat")

def extract_image_type(base64_data):
    # Check if the base64 data has the expected prefix
    if base64_data.startswith('data:image/'):
        # Extract the image type from the prefix
        prefix_end = base64_data.find(';base64,')
        if prefix_end != -1:
            return base64_data[len('data:image/'):prefix_end], base64_data.split(';base64,')[-1]
    return 'png', base64_data

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        # Get base64 image from request
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        # Extract image type from base64 data
        image_type, base64_data = extract_image_type(image_data)
        if not image_type:
            return jsonify({'error': 'Invalid base64 image data'}), 400
        
        # Create temp directory if not exists
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Generate unique filename and save image
        filename = os.path.join(temp_dir, f"{str(uuid.uuid4())}.{image_type}")
        try:
            image_bytes = base64.b64decode(base64_data)
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
