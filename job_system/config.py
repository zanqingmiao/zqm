import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # 数据库配置
    # 请根据实际情况修改用户名、密码、地址和数据库名
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/job_analysis_db?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 爬虫配置
    SPIDER_DELAY = 2  # 爬虫延时秒数
    SPIDER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
