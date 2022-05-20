from pickle import TRUE
from pickletools import read_uint1
from turtle import Turtle, title
import unittest
from unittest import result
from urllib import response

from sqlalchemy import true

from app import app,db,Movie,User, initdb

class WatchlistTestCase(unittest.TestCase):
    def setUp(self): # setUp在每一个测试方法执行前调用
        #更新配置
        app.config.update(
            TESTING=True,
            SQLALHEMY_DATABASE_URI = 'sqlite:///:memory:'
            # SQLite内存型数据库，不干扰程序使用的数据库文件
        )
        db.create_all()
        user = User(name='Test',username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie Title',year='2019')
        db.session.add_all([user,movie])
        #使用add_all()方法一次添加多个变量
        db.session.commit()

        self.client = app.test_client() #创建测试客户端
        # app.test_client()
        self.runner = app.test_cli_runner() #创建测试命令运行器

    def tearDown(self): #在每一个测试方法执行之后调用
        db.session.remove() #清除数据库会话
        db.drop_all()
    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)
    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])
    
    """
    测试视图函数
    """

    # 测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing') # 其中的一个参数接受url
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404',data)
        self.assertIn('Go back',data)
        self.assertEqual(response.status_code,404) # 判断响应码状态

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True) # 获取响应对象内容
        # as_text设置为True表示获取Unicode格式的响应
        self.assertIn('Test\'s Watchlist',data)
        self.assertIn('Test Movie Title',data)
        # assertIn判断响应内容是否包含预期需要的内容
        self.assertEqual(response.status_code,200)
        # assertEqual判断两个数值是否相等

    # 测试用户登录
    def login(self):
        self.client.post('/login',data=dict(
            username = 'test',
            password = '123'
        ),follow_redirects = True)
    # 使用dict字典的形式传数据，处理为POST请求方法
    # 其中dict的字段值对应了表单input的name属性值
    # follow_redirects参数设置为True可以跟随重定向，返回重定向响应内容

    # 测试创建条目
    def test_create_item(self):
        self.login()

        # 测试创建条目操作
        response = self.client.post('/',data=dict(
            title = 'New Movie',
            year = '2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created',data)
        self.assertIn('New Movie',data)

        #控制一个变量为空
        response = self.client.post('/',data=dict(
            title = '',
            year = '2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.',data)
        self.assertIn('Invalid input.',data)

        #控制另一个变量为空
        response = self.client.post('/',data=dict(
            title = 'New Movie',
            year = ''
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.',data)
        self.assertIn('Invalid input.',data)
    
    # 测试更新条目
    def test_update_item(self):
        self.login()

        # 测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item',data)
        self.assertIn('Test Movie',data)
        self.assertIn('2019',data)
    
        # 测试更新条目
        response = self.client.post('/movie/edit/1',dict(
            title='New Movie Edited',
            year = '2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('New Movie Edited',data)

        # 下面两个都是控制单一变量来测试，在此省略

    # 测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.',data)
        self.assertNotIn('Test Movie Title',data)
        # assert前缀的方法，若不满足条件会报错处理
    
    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Settings',data)
        self.assertNotIn('<form method="post">',data)
        self.assertNotIn('Delete',data)
        self.assertNotIn('Edit',data)
    
    # 测试登录
    def test_login(self):
        response = self.client.post('/login',data=dict(
            username = 'test',
            password = '123'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.',data)
        self.assertIn('Logout',data)
        self.assertIn('Settings',data)
        self.assertIn('Delete',data)
        self.assertIn('Edit',data)
        self.assertIn('<form method="post">',data)

    # 可以从使用错误的用户名，错误密码，空用户名，空密码来测试

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.',data)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Settings',data)
        self.assertNotIn('Delete',data)
        self.assertNotIn('Edit',data)
        self.assertNotIn('<form method="post">',data)

    # 测试设置
    def test_settings(self):
        self.login()

        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings',data)
        self.assertIn('Your name',data)

        # 测试更新设置
        response = self.client.post('/settings',data=dict(
            name = 'Grey Li',
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.',data)
        self.assertIn('Grey Li',data)

        # 可以设置为空设置来测试
    
    """
    测试（自定义）命令
    """
    from app import app,db,Movie,User,forge,initdb

    # 测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        # self.runner保存app.test_cli_runner() 方法
        # 返回一个命令运行器对象
        # self.runner调用invoke()方法执行命令，其中传入的参数为函数名
        self.assertIn('Done.',result.output)
        # output返回命令调用的结果
        self.assertNotEqual(Movie.query.count(),0)

    # 测试初始化数据库
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.',result.output)

    # 测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin','--username','peter','--password','456'])
        self.assertIn('Updating user...',result.output)
        self.assertIn('Done.',result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'peter')
        self.assertTrue(User.query.first().validate_password('456'))
    
    if __name__ == '__main__':
        unittest.main()
    
    """
    测试覆盖率
    (powershell) pip install coverage
    (powershell) coverage run --source=app test_watchlist.py
    可使用coverage html命令获取覆盖率报告文件保存本地
    """







