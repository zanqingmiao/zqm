from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from .extensions import db
from .config import Config
from .models import User, Job, Favorite
from .spider.mock_spider import MockSpider
from .spider.yilan_spider import YilanSpider
from .spider.china_public_spider import ChinaPublicSpider
from .analysis.data_processor import DataProcessor
from .analysis.visualizer import Visualizer
import pandas as pd
from pyecharts.charts import Bar, Pie

app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()
    # 创建默认管理员账号
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# --- 路由定义 ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('register'))
            
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/jobs')
def job_list():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    city = request.args.get('city', '')
    
    query = Job.query
    if keyword:
        query = query.filter(Job.title.like(f'%{keyword}%'))
    if city:
        query = query.filter(Job.city.like(f'%{city}%'))
        
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    jobs = pagination.items
    return render_template('job_list.html', jobs=jobs, pagination=pagination, keyword=keyword, city=city)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    is_favorite = False
    if 'user_id' in session:
        fav = Favorite.query.filter_by(user_id=session['user_id'], job_id=job_id).first()
        if fav:
            is_favorite = True
    return render_template('job_detail.html', job=job, is_favorite=is_favorite)

@app.route('/favorite/<int:job_id>', methods=['POST'])
def toggle_favorite(job_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    user_id = session['user_id']
    fav = Favorite.query.filter_by(user_id=user_id, job_id=job_id).first()
    
    if fav:
        db.session.delete(fav)
        message = '取消收藏成功'
        is_favorite = False
    else:
        new_fav = Favorite(user_id=user_id, job_id=job_id)
        db.session.add(new_fav)
        message = '收藏成功'
        is_favorite = True
        
    db.session.commit()
    return jsonify({'success': True, 'message': message, 'is_favorite': is_favorite})

@app.route('/my_favorites')
def my_favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    favorites = Favorite.query.filter_by(user_id=session['user_id']).all()
    jobs = [fav.job for fav in favorites]
    return render_template('my_favorites.html', jobs=jobs)

@app.route('/analysis')
def analysis():
    # 获取所有职位数据用于分析
    jobs = Job.query.all()
    if not jobs:
        return render_template('analysis.html', no_data=True)
        
    data = [{
        'id': j.id, 
        'city': j.city, 
        'salary': j.salary, 
        'avg_salary': j.avg_salary,
        'title': j.title,
        'requirement': j.requirement
    } for j in jobs]
    
    df = pd.DataFrame(data)
    
    # 使用DataProcessor进行分析
    processor = DataProcessor()
    # 确保avg_salary有值（虽然入库时已处理，但为了保险再做一次或直接用）
    # 这里直接用数据库中的avg_salary
    
    city_stats = processor.get_city_stats(df)
    
    # 关键词分析
    keywords = processor.extract_keywords(df['requirement'].tolist())
    
    # 生成图表
    vis = Visualizer()
    bar_chart = vis.plot_city_salary_bar(city_stats)
    pie_chart = vis.plot_job_pie(city_stats)
    
    bar_html = bar_chart.render_embed() if bar_chart else ""
    pie_html = pie_chart.render_embed() if pie_chart else ""
    
    return render_template('analysis.html', 
                           bar_html=bar_html, 
                           pie_html=pie_html, 
                           city_stats=city_stats.to_dict('records'),
                           keywords=keywords)

# --- 管理员功能 ---

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('需要管理员权限')
        return redirect(url_for('index'))
    return render_template('admin/dashboard.html')

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/jobs')
def admin_jobs():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.paginate(page=page, per_page=20)
    return render_template('admin/jobs.html', jobs=jobs.items, pagination=jobs)

@app.route('/admin/crawl', methods=['POST'])
def start_crawl():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': '无权限'})
    
    keyword = request.form.get('keyword', 'Python')
    city = request.form.get('city', '全国')
    pages = int(request.form.get('pages', 1))
    
    # 启动爬虫
    spider = MockSpider() # 实际项目中替换为真实爬虫
    jobs_data = spider.run(keyword, city, pages)
    
    # 保存数据
    count = 0
    for job_data in jobs_data:
        # 简单查重
        exists = Job.query.filter_by(title=job_data['title'], company=job_data['company']).first()
        if not exists:
            # 处理薪资
            avg_salary = DataProcessor.standardize_salary(job_data['salary'])
            
            job = Job(
                title=job_data['title'],
                company=job_data['company'],
                salary=job_data['salary'],
                avg_salary=avg_salary,
                city=job_data['city'],
                experience=job_data['experience'],
                education=job_data['education'],
                requirement=job_data['requirement'],
                source_url=job_data['source_url'],
                is_audited=True # 爬虫自动入库默认通过或需审核
            )
            db.session.add(job)
            count += 1
            
    db.session.commit()
    return jsonify({'success': True, 'message': f'成功抓取并入库 {count} 条职位信息'})

@app.route('/admin/spider/yilan', methods=['GET', 'POST'])
def spider_yilan():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        target_url = request.form.get('url')
        start_page = int(request.form.get('start_page', 0))
        end_page = int(request.form.get('end_page', start_page))
        
        if not target_url:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请输入目标URL'})
            else:
                flash('请输入目标URL')
                return redirect(url_for('spider_yilan'))
            
        spider = YilanSpider()
        try:
            jobs_data = spider.run_by_range(target_url, start_page, end_page)
            count = 0
            for job_data in jobs_data:
                exists = Job.query.filter_by(title=job_data['title'], company=job_data['company']).first()
                if not exists:
                    avg_salary = DataProcessor.standardize_salary(job_data['salary'])
                    job = Job(
                        title=job_data['title'],
                        company=job_data['company'],
                        salary=job_data['salary'],
                        avg_salary=avg_salary,
                        city=job_data['city'],
                        experience=job_data['experience'],
                        education=job_data['education'],
                        requirement=job_data['requirement'],
                        source_url=job_data['source_url'],
                        is_audited=True 
                    )
                    db.session.add(job)
                    count += 1
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if count > 0:
                    return jsonify({'success': True, 'message': f'爬取完成，成功入库 {count} 条数据', 'count': count})
                else:
                    return jsonify({'success': True, 'message': '爬取完成，但未入库任何数据（可能已存在或未抓到数据）', 'count': 0})
            else:
                if count > 0:
                    flash(f'爬取完成，成功入库 {count} 条数据')
                else:
                    flash('爬取完成，但未入库任何数据（可能已存在或未抓到数据）')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'爬取失败: {str(e)}'})
            else:
                flash(f'爬取失败: {str(e)}')
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return redirect(url_for('spider_yilan'))
            
    return render_template('admin/spider_yilan.html')

@app.route('/admin/spider/china_public', methods=['GET', 'POST'])
def spider_china_public():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        target_url = request.form.get('url')
        start_page = int(request.form.get('start_page', 1))
        end_page = int(request.form.get('end_page', start_page))
        
        if not target_url:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请输入目标URL'})
            else:
                flash('请输入目标URL')
                return redirect(url_for('spider_china_public'))
            
        spider = ChinaPublicSpider()
        try:
            jobs_data = spider.run_by_range(target_url, start_page, end_page)
            count = 0
            for job_data in jobs_data:
                exists = Job.query.filter_by(title=job_data['title'], company=job_data['company']).first()
                if not exists:
                    avg_salary = DataProcessor.standardize_salary(job_data['salary'])
                    job = Job(
                        title=job_data['title'],
                        company=job_data['company'],
                        salary=job_data['salary'],
                        avg_salary=avg_salary,
                        city=job_data['city'],
                        experience=job_data['experience'],
                        education=job_data['education'],
                        requirement=job_data['requirement'],
                        source_url=job_data['source_url'],
                        is_audited=True 
                    )
                    db.session.add(job)
                    count += 1
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': f'爬取完成，成功入库 {count} 条数据', 'count': count})
            else:
                flash(f'爬取完成，成功入库 {count} 条数据')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'爬取失败: {str(e)}'})
            else:
                flash(f'爬取失败: {str(e)}')
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return redirect(url_for('spider_china_public'))
            
    return render_template('admin/spider_china_public.html')

@app.route('/admin/audit/<int:job_id>', methods=['POST'])
def audit_job(job_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False})
    job = Job.query.get_or_404(job_id)
    job.is_audited = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False})
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
