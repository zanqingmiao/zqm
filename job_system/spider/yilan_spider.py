from .base_spider import BaseSpider
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse, parse_qsl, urlencode, urlunparse

class YilanSpider(BaseSpider):
    """
    一览应届生网爬虫
    """
    def __init__(self):
        super().__init__()
        self.base_url = "http://yjs.job1001.com/job/index.htm"

    def parse(self, response):
        """解析HTML页面内容"""
        # 显式设置编码为utf-8，防止中文乱码
        # 如果还是乱码，可以尝试 'gbk' 或 response.apparent_encoding
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        
        # 1. 定位职位列表容器
        job_items = soup.select('ul.job_list_A > li')
        
        for item in job_items:
            try:
                # 2. 提取职位名称和详情链接
                title_elem = item.select_one('.item_l_A a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                detail_url = title_elem.get('href', '')
                if detail_url and not detail_url.startswith('http'):
                    detail_url = "http://yjs.job1001.com" + detail_url
                
                # 3. 提取公司信息
                company_elem = item.select_one('.item_r_A a')
                company = company_elem.text.strip() if company_elem else "未知公司"
                
                # 4. 提取薪资、城市、经验、学历
                # 结构：经验 | 学历 | 城市 | 薪资
                info_elem = item.select_one('.item_l_B')
                if info_elem:
                    # 移除薪资标签，获取剩余文本
                    salary_elem = info_elem.select_one('.top_c_page')
                    salary = salary_elem.text.strip() if salary_elem else "面议"
                    
                    # 获取文本并分割
                    # 文本类似于 "不限经验 | 大专 | 江西 | "
                    # 使用 text 获取纯文本，可能包含 salary，所以先去除 salary 标签或单独处理
                    # 这里简单处理：获取所有文本，去掉薪资，然后分割
                    full_text = info_elem.get_text(strip=True)
                    # 替换掉薪资部分以便分割
                    if salary != "面议":
                        full_text = full_text.replace(salary, "")
                    
                    parts = [p.strip() for p in full_text.split('|') if p.strip()]
                    
                    # 尝试按顺序提取，通常顺序是：经验、学历、城市
                    experience = parts[0] if len(parts) > 0 else "经验不限"
                    education = parts[1] if len(parts) > 1 else "学历不限"
                    city = parts[2] if len(parts) > 2 else "未知城市"
                else:
                    salary = "面议"
                    experience = "经验不限"
                    education = "学历不限"
                    city = "未知城市"

                # 5. 提取福利作为职位要求的一部分
                welfare_elems = item.select('.item_r_C .welfare_item')
                welfare = [w.text.strip() for w in welfare_elems]
                requirement = "福利待遇：" + "，".join(welfare) if welfare else "暂无描述"
                
                # 6. 获取公司地址
                address_elem = item.select_one('.item_r_B')
                address = address_elem.text.strip() if address_elem else ""
                if address:
                    requirement += f"\n工作地址：{address}"

                job = {
                    "title": title,
                    "company": company,
                    "salary": salary,
                    "city": city,
                    "experience": experience,
                    "education": education,
                    "requirement": requirement,
                    "source_url": detail_url
                }
                jobs.append(job)
            except Exception as e:
                print(f"Error parsing item: {e}")
                continue
                
        return jobs
    
    def make_url_with_page(self, url, page_index):
        parsed = urlparse(url)
        q = dict(parse_qsl(parsed.query, keep_blank_values=True))
        q['page'] = str(int(page_index))
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(q, doseq=True), parsed.fragment))
    
    def run_by_range(self, start_url, start_page=0, end_page=0):
        all_jobs = []
        for idx in range(int(start_page), int(end_page) + 1):
            current_url = self.make_url_with_page(start_url, idx)
            response = self.fetch(current_url)
            if response:
                jobs = self.parse(response)
                if not jobs:
                    break
                all_jobs.extend(jobs)
            else:
                break
            if idx < end_page:
                time.sleep(random.uniform(2, 5))
        return all_jobs
    
    def run_by_url(self, start_url, pages=1):
        parsed = urlparse(start_url)
        q = dict(parse_qsl(parsed.query, keep_blank_values=True))
        try:
            s = int(q.get('page', '0'))
        except Exception:
            s = 0
        e = s + int(pages) - 1
        return self.run_by_range(start_url, s, e)
