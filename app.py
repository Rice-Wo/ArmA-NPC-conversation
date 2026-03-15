import os
import sys
import json
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify

# 匯入你的核心轉換邏輯
try:
    import spawner
except ImportError:
    # 確保 spawner.py 在同一個目錄下
    pass

# --- 1. 路徑處理邏輯 (確保打包成 EXE 後仍能運作) ---
def get_resource_path(relative_path):
    """ 取得資源的絕對路徑，相容開發環境與 PyInstaller 打包環境 """
    if getattr(sys, 'frozen', False):
        # 運行於 PyInstaller 打包後的臨時資料夾
        base_path = sys._MEIPASS
    else:
        # 運行於正常 Python 環境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 初始化 Flask，指定模板與靜態檔案路徑
app = Flask(__name__, 
            template_folder=get_resource_path('templates'),
            static_folder=get_resource_path('static'))

# 確保存檔資料夾 (input) 永遠在執行檔旁邊
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(".")

INPUT_FOLDER = os.path.join(BASE_DIR, 'input')
if not os.path.exists(INPUT_FOLDER):
    os.makedirs(INPUT_FOLDER)

# --- 2. 路由邏輯 ---

@app.route('/')
def index():
    """ 首頁 """
    return render_template('index.html')

@app.route('/list_files')
def list_files():
    """ 取得所有 JSON 存檔清單 """
    try:
        files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.json')]
        return jsonify(files)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save', methods=['POST'])
def save_file():
    """ 儲存 NPC 設定為 JSON """
    try:
        data = request.json
        filename = f"{data['npc_id']}.json"
        file_path = os.path.join(INPUT_FOLDER, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return jsonify({"status": "success", "message": f"存檔成功：{filename}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/load/<filename>')
def load_file(filename):
    """ 讀取指定的 JSON 存檔 """
    try:
        file_path = os.path.join(INPUT_FOLDER, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """ 刪除存檔 """
    try:
        file_path = os.path.join(INPUT_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"status": "success", "message": "檔案已刪除"})
        return jsonify({"status": "error", "message": "檔案不存在"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/copy_sqf', methods=['POST'])
def copy_sqf():
    """ 呼叫 spawner 生成 SQF 代碼 """
    try:
        data = request.json
        # 假設你的 spawner.py 中有一個 generate_sqf 函式
        sqf_content = spawner.generate_sqf_string(data) 
        return jsonify({"status": "success", "sqf": sqf_content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 3. 啟動邏輯 ---

def open_browser():
    """ 自動開啟瀏覽器 """
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    # 僅在非除錯模式下自動開啟瀏覽器，避免重複開啟
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()
    
    # 關閉 debug 模式以利打包後的穩定性
    app.run(debug=False, port=5000, host='127.0.0.1')