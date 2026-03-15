from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# 設定路徑
INPUT_DIR = 'input'
if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)

@app.route('/')
def index():
    return render_template('index.html')

# 取得 input 資料夾內所有的檔案列表
@app.route('/list_files', methods=['GET'])
def list_files():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    return jsonify(files)

# 讀取特定檔案內容
@app.route('/load/<filename>', methods=['GET'])
def load_file(filename):
    try:
        with open(os.path.join(INPUT_DIR, filename), 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 儲存 JSON 到後端
@app.route('/save', methods=['POST'])
def save_json():
    try:
        data = request.json
        npc_id = data.get('npc_id', 'unknown_npc')
        file_path = os.path.join(INPUT_DIR, f"{npc_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        return jsonify({"status": "success", "message": f"儲存成功：{file_path}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
import spawner # 確保能 import 你的 spawner.py

@app.route('/copy_sqf', methods=['POST'])
def copy_sqf():
    try:
        data = request.json
        # 直接使用 spawner 的邏輯產出字串，不用存檔
        sqf_content = spawner.generate_sqf_string(data)
        return jsonify({"status": "success", "sqf": sqf_content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
import os

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join('input', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"status": "success", "message": f"已刪除 {filename}"})
        else:
            return jsonify({"status": "error", "message": "檔案不存在"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)