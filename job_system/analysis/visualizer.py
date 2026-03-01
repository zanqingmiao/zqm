from pyecharts import options as opts
from pyecharts.charts import Bar, Pie

class Visualizer:
    @staticmethod
    def plot_city_salary_bar(city_stats):
        """生成城市-平均薪资柱状图"""
        if city_stats.empty:
            return None
        
        c = (
            Bar()
            .add_xaxis(city_stats['city'].tolist())
            .add_yaxis("平均薪资", city_stats['avg_salary'].tolist())
            .add_yaxis("职位数量", city_stats['job_count'].tolist()) # 双Y轴更丰富
            .set_global_opts(
                title_opts=opts.TitleOpts(title="各城市平均薪资与职位分布"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                toolbox_opts=opts.ToolboxOpts(),
            )
        )
        return c

    @staticmethod
    def plot_job_pie(city_stats):
        """生成城市职位占比饼图"""
        if city_stats.empty:
            return None
            
        data_pair = [list(z) for z in zip(city_stats['city'].tolist(), city_stats['job_count'].tolist())]
        
        c = (
            Pie()
            .add(
                "",
                data_pair,
                radius=["40%", "75%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="各城市职位数量占比"),
                legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
        )
        return c
