import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/xhs_app'
    # 修改基础目录
    BASE_DIR = '/data/yangyb/ios_app'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DEBUG_DIR = os.path.join(BASE_DIR, 'debug')  # 添加调试目录配置
    MODEL_PATH = os.path.join(BASE_DIR, 'models')  # 使用绝对路径
    WHISPER_CONFIG = {
        'inter_threads': 4,    # 线程间并行数
        'intra_threads': 4     # 线程内并行数
    }