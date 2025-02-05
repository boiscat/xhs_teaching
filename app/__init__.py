from flask import Flask
from flask_pymongo import PyMongo
from app.config import Config
import os
from flask_cors import CORS

mongo = PyMongo()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    
    # 启用 CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 初始化MongoDB
    mongo.init_app(app)
    
    # 注册蓝图
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)
    
    # 确保上传文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("Flask app created with routes:")  # 添加调试信息
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule.rule}")
    
    return app 