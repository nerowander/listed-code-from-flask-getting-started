from crypt import methods
from operator import imod
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
import os
import click # 编写命令来自动执行创建数据库
app = Flask(__name__)

db = SQLAlchemy(app)
# db初始化扩展，引入ORM对象关系映射
# 实例化一个类对象
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(app.root_path,'data.db')
# sqlite:///为数据库文件的绝对地址，windows的配置为///,否则为////
# 配置config变量需要配置flask.config字典
app.config['SECRET_KEY'] = 'dev' 
# 在很多操作（比如flash函数当中需要设置app对象的密钥）
# 密钥应该足够随机
name = 'Grey Li'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
]

# 下面的2个class为创建数据库模型（创建2张表）

class User(db.Model):# 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer,primary_key=True) # 主键
    name = db.Column(db.String(20))
    # 设置列名和数据类型

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

# 模型类要声明继承db.Model
# 每一个类属性（字段）要实例化db.Column
# 使用python shell(打开为flask shell命令)

# from hello import db
# db.create_all()  这两个命令用来创建数据库文件

# db.drop_all()
# db.create_all()  若改动模型类，想重新生成表模式，使用上述两个命令
# 但是这回一并删除所有的数据，需要利用Flask-Migrate扩展来迁移数据

@app.cli.command() #注册为命令
@click.option('--drop',is_flag=True,help='Create after drop.') # 设置选项
def initdb(drop):
    """数据库初始化"""
    if drop: # 判断是否输入了--drop的选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') # 输出提示信息

"""
创建--向数据库里添加记录
from hello import User,Movie 导入模型类
user = User(name='Grey Li') 创建一个User记录(调用User类)
m1 = Movie(title='Leon',year='1994') 创建一个Movie记录(调用Movie类)
m2 = Movie(title='Mahjong',year='1996') 
db.session.add(user) 将刚才的记录添加到数据库会话
db.session.add(m1)
db.session.add(m2)
db.session.commit() 提交数据库会话，只需要在最后一次调用
调用了db.session.commit()才会将记录真正提交到数据库当中

注意--id字段（主键）不需要传入,SQLAlchemy会自动处理这个字段
"""

"""
查询--从数据库里读取记录
from hello import Movie 导入模型类
movie = Movie.query.first() 格式为—— <class_name>.query.<filter_method>.<find_method>
返回第一个记录
Movie.query.all()
获取所有记录
Movie.query.count()
获取所有记录的数量
Movie.query.get(1)
获取主键值为1的记录
Movie.query.filter_by(title='Mahjong').first()
获取title字段为Mahjong的记录
Movie.query.filter(Movie.title=='Mahjong').first()
等同于上面的查询
"""

"""
更新数据
movie = Movie.query.get(2)
movie.title = 'WALL-E' 直接赋值覆盖即可
movie.year = '2008'
db.session.commit() 仍需要commit操作
"""

"""
删除数据
movie = Movie.query.get(1)
db.session.delete(movie) 使用此方法来删除记录
db.session.commit() 提交改动

"""

"""
@app.route('/')
def index():
    user = User.query.first() 读取用户记录
    movies = Movie.query.all() 读取所有电影记录
    return render_template('index.html',user=user,movies=movies)

"""

"""
index.html中读取user的name记录
{{ user.name }}'s Watchlist
"""

"""
将虚拟数据插入数据库里
"""
import click

@app.cli.command()
def forge():
    db.create_all()

    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    
    db.session.commit()
    click.echo('Done.')

    # 执行flask forge命令会将数据添加到数据库当中


from flask import escape

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)

# 利用escape将name变量进行转义处理，例如将<转换成&lt


@app.route('/')
def index():
    return render_template('index.html',name=name,movies=movies)

# 左边的movies是模板中使用的变量名称，右边的 movies 则是该变量指向的实际对象

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象为参数
    user = User.query.first()
    return render_template('404.html',user=user),404
    # 注意要返回模板和状态码
    # 当访问不存在的url的时候，会显示自定义的错误页面

# 模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)
    # 需要返回字典值
    # 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中
    # 因此可以直接在模板中使用

"""

使用例子
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html',movies=movies)

同样的，后面我们创建的任意一个模板，都可以在模板中直接使用 user 变量

"""

"""
支持GET和POST的app.route
"""
from flask import request,url_for,redirect,flash
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST': # 判断是否是POST请求
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input.') # 错误提示
            return redirect(url_for('index')) # 重定向回主界面
        # 保存数据到数据库
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        # flash向模板传递提示消息,配合get_flashed_messages()函数在模板里获取提示消息
        return redirect(url_for('index'))
    
    movies = Movie.query.all()
    return render_template('index.html',movies=movies)

"""
编辑条目
"""

@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id) # 返回对应主键的记录，如果没有找到，则返回404错误响应

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year)!=4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit',movie_id=movie_id))
        
        movie.title = title
        movie.year = year 
        # 更新数据
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index')) # 重定向回主页

    return render_template('edit.html',moive=movie) # 传入编辑数据

"""
删除条目
"""

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

"""
用户认证--管理员和普通用户
"""

from werkzeug.security import generate_password_hash,check_password_hash

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20)) # 表示是管理员还是游客
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) # 密码散列值

    def set_password(self,password): # 设置密码
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self,password): # 验证密码
        return check_password_hash(self.password_hash,password) 

"""
生成管理员账户
"""

import click

@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login.')
@click.option('--password',prompt=True,hide_input=True,hide_input=True,confirmation_prompt=True,help='The password used to login.')
# hide_input 代表了输入隐藏，应用于输入password当中
# confirmation_prompt=True会要求二次输入
def admin(username,password):
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username,name='Admin')
        user.set_password(password)
    
    db.session.commit()
    click.echo('Done.')

"""
使用Flask-login模块实现用户认证
"""

"""
初始化步骤
"""
from flask_login import LoginManager

login_manager = LoginManager(app) # 实例化拓展类

@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数
    user = User.query.get(int(user_id))
    return user #返回用户对象

from flask_login import UserMixin

# class User(db.Model,UserMixin):
    # ...
    # User类继承了UserMixin类，拥有了更多的属性和方法，例如is_authenticated

"""
使用Flask-Login模块登录
"""

from flask_login import login_user

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
    
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user) # 用户登入
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')

"""
使用flask-login模块登出
"""

from flask_login import login_required,logout_user

@app.route('/logout')
@login_required # 视图保护，即为一种认证上的保护
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

"""
使用@login_required修饰的路由，若未登录的用户访问对应的url
则会被重定向
可以通过设置login_manager.login_view = 'function_name'来设置重定向的地址
该设置置于login_manager实例的下方
"""

"""
对于某些post请求，不需要使用@login_required修饰器的处理
"""

from flask_login import login_required,current_user

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
        # is_authenticated需要在带有UserMixin的User类定义
            return redirect(url_for('index'))

"""
修改用户的名字
"""

from flask_login import login_required,current_user

@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input')
            return redirect(url_for('settings'))
        current_user.name = name
        # 相当于下面2行指令
        """
        user = User.query.first()
        user.name = name 
        """
        db.session.commit()
        flash('Settings updated')
        return redirect(url_for('index'))
    return render_template('settings.html')


"""
一些注意事项
"""
# flask run默认运行app.py和wsgi.py
# 在powershell当中可以这样:$env:FLASK_APP = "hello.py"(设置环境变量)

# 两个环境变量:FLASK_APP 和 FLASK_ENV(这个是用来设置程序运行的环境)

# 安装python-dotenv的时候，Flask 会从项目根目录的 .flaskenv 和 .env 文件读取环境变量并设置

# .flaskenv存储公开环境变量，.env存储敏感数据

# 一个视图函数(route)可以绑定多个url

# 使用SQLAlchemy--一个 Python 数据库工具（ORM，即对象关系映射）
# 可以此简化数据库操作