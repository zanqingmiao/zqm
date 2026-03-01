from .base_spider import BaseSpider
import random

class MockSpider(BaseSpider):
    """
    模拟爬虫类，用于生成测试数据。
    实际开发中可以替换为针对特定网站（如Boss直聘、前程无忧等）的爬虫实现。
    """
    def parse(self, response):
        pass  # MockSpider 不需要解析真实页面

    def run(self, keyword, city, pages=1):
        """生成模拟职位数据"""
        print(f"[MockSpider] Generating {pages * 10} mock jobs for {keyword} in {city}")
        
        jobs = []
        titles = [f"{keyword}开发工程师", f"高级{keyword}工程师", f"{keyword}架构师", f"{keyword}实习生", "数据分析师"]
        companies = ["腾讯", "阿里巴巴", "字节跳动", "百度", "美团", "京东", "网易", "滴滴"]
        salaries = ["10k-20k", "15k-25k", "20k-40k", "8k-12k", "25k-50k"]
        experiences = ["1-3年", "3-5年", "5-10年", "应届生", "经验不限"]
        educations = ["本科", "硕士", "博士", "大专", "学历不限"]
        
        for _ in range(pages * 10):
            job = {
                "title": random.choice(titles),
                "company": random.choice(companies) + "（模拟数据）",
                "salary": random.choice(salaries),
                "city": city,
                "experience": random.choice(experiences),
                "education": random.choice(educations),
                "requirement": f"熟练掌握{keyword}，熟悉常用的框架和数据库...",
                "source_url": "http://example.com/job/mock"
            }
            jobs.append(job)
            
        return jobs

if __name__ == "__main__":
    spider = MockSpider()
    print(spider.run("Python", "北京", 1))
