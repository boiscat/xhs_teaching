from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Flask application...")  # 添加调试信息
    app.run(debug=True, host='0.0.0.0', port=5001)  # 改用 5001 端口 