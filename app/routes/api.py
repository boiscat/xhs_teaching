from flask import Blueprint, request, jsonify, render_template
from app.services.whisper_service import WhisperService
import os
from werkzeug.utils import secure_filename
from app import Config

api_bp = Blueprint('api', __name__)

def save_uploaded_file(file):
    """保存上传的文件"""
    print("Starting to save file...")  # 添加日志
    filename = secure_filename(file.filename)
    # 确保上传目录存在
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)
    print(f"File saved successfully at: {file_path}")  # 添加日志
    return file_path

@api_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@api_bp.route('/api/process-video', methods=['POST'])
def process_video():
    print("Received process-video request")  # 添加日志
    try:
        # 基本请求验证
        if 'video' not in request.files:
            print("No video file in request")
            return jsonify({
                'error': '无效的请求',
                'detail': '需要上传视频文件'
            }), 400

        video_file = request.files['video']
        if not video_file or video_file.filename == '':
            print("Empty filename")
            return jsonify({
                'error': '无效的文件',
                'detail': '未选择文件'
            }), 400
            
        print(f"Processing file: {video_file.filename}")
        
        # 检查文件类型
        allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'm4a'}
        file_ext = video_file.filename.rsplit('.', 1)[1].lower() if '.' in video_file.filename else ''
        if not file_ext or file_ext not in allowed_extensions:
            print(f"Invalid file type: {file_ext}")
            return jsonify({
                'error': '不支持的文件类型',
                'detail': f'支持的文件类型: {", ".join(allowed_extensions)}'
            }), 400

        # 保存文件
        print("Saving file...")
        file_path = save_uploaded_file(video_file)
        print(f"File saved to: {file_path}")
        
        # 提取语音文本
        print("Creating WhisperService instance...")  # 添加日志
        whisper_service = WhisperService()
        print("Starting transcription...")  # 添加日志
        transcriptions = whisper_service.transcribe_video(file_path)
        print("Transcription completed")  # 添加日志
        
        # 删除临时文件
        try:
            os.remove(file_path)
            print("Temporary file removed")
        except Exception as e:
            print(f"Warning: Failed to remove temporary file {file_path}: {str(e)}")
        
        # 准备响应
        response_data = {
            'success': True,
            'filename': video_file.filename,
            'transcriptions': transcriptions
        }
        print("Sending response:", response_data)  # 添加日志
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print("Error in process_video:")
        print(traceback.format_exc())
        return jsonify({
            'error': '处理失败',
            'detail': str(e)
        }), 500

# 添加错误处理器
@api_bp.errorhandler(404)
def not_found(e):
    return jsonify({'error': '未找到请求的资源'}), 404

@api_bp.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': '不支持的请求方法'}), 405

@api_bp.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        'error': '服务器错误',
        'detail': str(e)
    }), 500 