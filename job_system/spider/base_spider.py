import time
import requests
import random
from abc import ABC, abstractmethod

class BaseSpider(ABC):
    def __init__(self, headers=None, delay=2):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    @abstractmethod
    def parse(self, response):
        """解析响应内容，返回职位列表"""
        pass

    def fetch(self, url, params=None):
        """发送请求获取页面内容"""
        try:
            time.sleep(self.delay + random.uniform(0, 1))  # 随机延时
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def run(self, keyword, city, pages=1):
        """执行爬虫的主入口"""
        all_jobs = []
        # 这里需要子类实现具体的翻页逻辑
        # 这是一个简单的示例框架
        print(f"Starting crawl for {keyword} in {city}...")
        return all_jobs
