# Python职位数据分析及可视化系统

这是一个基于Flask的职位数据分析系统，包含数据爬取、清洗、分析及可视化功能。

## 项目结构

```
job_system/
    app.py              # Flask应用入口
    config.py           # 配置文件
    models.py           # 数据库模型
    extensions.py       # Flask扩展初始化
    spider/             # 爬虫模块
        base_spider.py  # 爬虫基类
        mock_spider.py  # 模拟爬虫（用于测试）
    analysis/           # 数据分析模块
        data_processor.py # 数据处理
        visualizer.py   # 可视化图表生成
    templates/          # HTML模板
    static/             # 静态文件
```

## 快速开始

1. **安装依赖**

   确保已安装Python 3.8+，然后运行：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置数据库**

   修改 `job_system/config.py` 中的数据库连接配置：
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://用户名:密码@localhost/数据库名?charset=utf8mb4'
   ```
   请确保MySQL服务已启动，并且创建了对应的数据库（如 `job_analysis_db`）。

3. **运行系统**

   在项目根目录下运行：
   ```bash
   python -m job_system.app
   ```
   或者直接运行 `app.py`（需调整导入路径或设置PYTHONPATH）。
   
   推荐方式：
   ```bash
   set FLASK_APP=job_system.app
   flask run
   ```

4. **访问系统**

   打开浏览器访问 http://127.0.0.1:5000

   - 默认管理员账号：admin
   - 默认管理员密码：admin123

## 功能说明

- **爬虫**：在管理员后台可以启动爬虫（目前为模拟数据，可根据需要修改 `mock_spider.py` 或添加新的爬虫类）。
- **分析**：访问“数据分析”页面查看职位分布和薪资统计。
- **用户**：注册登录后可以收藏职位。
