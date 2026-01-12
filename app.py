from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/register', methods=['POST'])
def register_course():
    try:
        data = request.json
        jwt_token = data.get('jwtToken')
        payload = data.get('payload')
        turn_id = data.get('turnId', '66')
        study_program_id = data.get('studyProgramId', '22110ST')
        action = data.get('action', 'REGIST')
        
        url = f"https://dangkyapi.hcmute.edu.vn/api/Regist/RegistScheduleStudyUnit?TurnID={turn_id}&Action={action}&StudyProgramID={study_program_id}"
        
        headers = {
            'host': 'dangkyapi.hcmute.edu.vn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://dkmh.hcmute.edu.vn/',
            'Content-Type': 'application/json',
            'apiKey': 'pscRBF0zT2Mqo6vMw69YMOH43IrB2RtXBS0EHit2kzv',
            'clientId': 'dtl',
            'Authorization': f'Bearer {jwt_token}',
            'Origin': 'https://dkmh.hcmute.edu.vn',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        return jsonify({
            'status': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'status': 408, 'error': 'Timeout'}), 408
    except Exception as e:
        return jsonify({'status': 500, 'error': str(e)}), 500

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
