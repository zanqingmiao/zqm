from .base_spider import BaseSpider
from bs4 import BeautifulSoup
import time
import random

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

    def run_by_url(self, start_url, pages=1):
        """根据给定的URL开始爬取"""
        all_jobs = []
        current_url = start_url
        
        for page in range(1, pages + 1):
            print(f"正在爬取第 {page} 页: {current_url}")
            
            # 发送请求
            response = self.fetch(current_url)
            
            if response:
                # 解析数据
                jobs = self.parse(response)
                if not jobs:
                    print("未找到职位数据，可能已到末页或被反爬")
                    break
                    
                all_jobs.extend(jobs)
                print(f"第 {page} 页爬取成功，获取 {len(jobs)} 条数据")
                
                # 获取下一页链接
                soup = BeautifulSoup(response.text, 'html.parser')
                # 假设下一页按钮是 "下一页" 或者类似的 class
                # 根据实际情况，这里简化为不支持自动翻页，或者需要解析分页器
                # 一览的分页器通常在 .xjh_content_page 或底部的分页条
                # 暂时只爬取当前页，如果需要翻页，需要解析分页链接
                next_page = soup.find('a', string='下一页')
                if next_page and 'href' in next_page.attrs:
                    next_url = next_page['href']
                    if not next_url.startswith('http'):
                         # 处理相对路径
                         if next_url.startswith('/'):
                             current_url = "http://yjs.job1001.com" + next_url
                         else:
                             # 简单拼接
                             current_url = "/".join(current_url.split('/')[:-1]) + "/" + next_url
                else:
                    print("未找到下一页，停止爬取")
                    break
            else:
                print(f"第 {page} 页请求失败")
                break
            
            # 随机延时
            if page < pages:
                time.sleep(random.uniform(2, 5))
            
        return all_jobs
