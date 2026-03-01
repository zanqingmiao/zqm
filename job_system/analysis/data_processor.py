import re
import pandas as pd
import jieba
from collections import Counter
import numpy as np

class DataProcessor:
    def __init__(self, db_session=None):
        self.db_session = db_session

    @staticmethod
    def standardize_salary(salary_str):
        """
        将薪资字符串转换为月平均薪资（元）
        支持格式如：10k-20k, 15000-25000, 10-20k/月, 15k*13薪等
        """
        if not salary_str:
            return 0
        
        salary_str = salary_str.lower().replace('k', '000').replace('w', '0000')
        # 提取数字范围
        matches = re.findall(r'(\d+\.?\d*)', salary_str)
        if not matches:
            return 0
            
        nums = [float(x) for x in matches]
        
        if len(nums) >= 2:
            avg_salary = (nums[0] + nums[1]) / 2
        elif len(nums) == 1:
            avg_salary = nums[0]
        else:
            avg_salary = 0
            
        # 处理可能的年薪情况（简单判断如果薪资过高可能是年薪，这里假设超过50k且没说是月薪可能是年薪，或者根据单位）
        # 这里简化处理，假设大部分是月薪。如果是年薪通常带有"年"字
        if '年' in salary_str:
            avg_salary /= 12
            
        return round(avg_salary, 2)

    @staticmethod
    def extract_keywords(text_list, top_n=20):
        """
        从文本列表中提取关键词统计
        """
        text = "".join([str(t) for t in text_list if t])
        words = jieba.lcut(text)
        # 停用词过滤（实际项目中应加载更完善的停用词表）
        stop_words = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '在', '对', '等', '能', '有', '会', '熟练', '掌握', '熟悉', '具备', '优先', '了解', '精通', '使用', '进行', '相关', '工作', '经验', '能力', '负责', '开发', '技术', '以及', '或者', '具有', '参与', '编写', '完成', '配合', '根据', '能够', '以上', '学历', '要求', '任职', '岗位', '职责', '公司', '业务', '团队', '项目', '沟通', '协作', '良好', '强', '并', '所', '但', '这里', '那里', '这个', '那个'}
        
        filtered_words = [w for w in words if len(w) > 1 and w not in stop_words]
        return Counter(filtered_words).most_common(top_n)

    def get_city_stats(self, df):
        """统计城市职位数量和平均薪资"""
        if df.empty:
            return pd.DataFrame()
        
        # 确保薪资是数值类型
        df['avg_salary'] = pd.to_numeric(df['avg_salary'], errors='coerce').fillna(0)
        
        stats = df.groupby('city').agg({
            'id': 'count',
            'avg_salary': 'mean'
        }).reset_index()
        stats.columns = ['city', 'job_count', 'avg_salary']
        stats['avg_salary'] = stats['avg_salary'].round(2)
        return stats.sort_values('job_count', ascending=False)
