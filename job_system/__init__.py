from flask import Flask
from .config import Config
from .extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # 注册蓝图或路由
    # 这里为了简单起见，路由都在 app.py 中定义，所以可能不需要在这里注册
    # 但如果要拆分模块，可以在这里注册蓝图
    
    return app
