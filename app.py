import gevent

from gevent import monkey

from tools import create_uuid

monkey.patch_all()
from flask_socketio import SocketIO
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import db
import random
import time
import config
import datetime
import os
import re
from uploader import Uploader
from page_utils import Pagination
from databank import db as db2
from mail import mail
from Socket_io import socketio
from databank import Confirm,UserInformation
from coverage import Coverage
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
path_photo = '/static/img/None.jpg'
# 从对象中导入config
app.config.from_object(config)
db2.init_app(app)
mail.init_app(app)
socketio = SocketIO(cors_allowed_origins="*")
socketio.init_app(app)
from Background import admin
app.register_blueprint(admin)
from Sendemail import email
app.register_blueprint(email)
from messages import messages
app.register_blueprint(messages)
from order import order_api
app.register_blueprint(order_api)
from chatroom import chatroom, MyCustomNamespace

app.register_blueprint(chatroom)
from decorators2 import login_limit,ban_comment
# 登录状态保持
@app.context_processor
def login_status():
    # 从session中获取email
    email = session.get('email')
    type1 = session.get('type')
    # 如果有email信息，则证明已经登录了，我们从数据库中获取登陆者的昵称和用户类型，来返回到全局
    if email:
        try:
            cur = db.cursor()
            sql = "select nickname,type from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result:
                return {'email': email, 'nickname': result[0], 'user_type': result[1], 'type': type1}
        except Exception as e:
            raise e
    # 如果email信息不存在，则未登录，返回空
    return {}


# 主页
@app.route('/')
def index():
    return "主页"


# 禁止访问
@app.route('/forbid')
def forbid():
    return "禁止访问页面"


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return "注册页面"
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')
        phone = request.form.get('phone')
        address = request.form.get('address')
        type1 = request.form.get('type1')
        if not all([email, nickname, password_1, password_2, phone, address]):
            return "信息填写不全，请将信息填写完整"
        if password_1 != password_2:
            return "两次密码填写不一致"
        password = generate_password_hash(password_1, method="pbkdf2:sha256", salt_length=8)
        try:
            cur = db.cursor()
            sql = "select * from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result is not None:
                return "该用户名已存在"
            else:
                create_time = time.strftime("%Y-%m-%d %H:%M:%S")
                sql = "insert into UserInformation(email, nickname, password, type, create_time, phone, address, information ,photo) VALUES ('%s','%s','%s','%s','%s','%s','%s','','/static/img/None.jpg')" % (
                    email, nickname, password, type1, create_time, phone, address)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
                return "注册成功"
        except Exception as e:
            raise e


# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return "登录页面"
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([email, password]):
            return "请将信息填写完整"
        try:
            cur = db.cursor()
            sql = "select password, type from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result is None:
                return "该用户不存在"
            if check_password_hash(result[0], password):
                if result[1]==3:
                    return "登录后台页面"
                else:
                    session['email'] = email
                    session['type'] = result[1]
                    session.permanent = True
                    cur.close()
                    return "登录用户页面"
            else:
                return "密码错误"
        except Exception as e:
            raise e


# 邮箱修改密码
@app.route('/email_confirm', methods=['GET', 'POST'])
def email_confirm():
    if request.method == 'GET':
        return "邮箱修改密码登录页面"
    if request.method == 'POST':
        email = request.form.get('the_email')
        confirm = request.form.get('confirm')
        password = request.form.get('new_password')
        id=request.form.get('getid')
        if not all([email, password,confirm,id]):
            return "请将信息填写完整"
        inf = Confirm.query.filter_by(id=id).first()
        if not inf or not confirm==inf.secret:
            return "验证码错误"
        cur = db.cursor()
        password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        sql = "update UserInformation set password = '%s' where email = '%s'" % (password, email)
        db.ping(reconnect=True)
        cur.execute(sql)
        db.commit()
        cur.close()
        return "修改密码成功"



# 用户注销
@app.route('/logout')
def logout():
    session.clear()
    return "注销成功"


# 生成128随机id
def gengenerateID():
    re = ""
    for i in range(128):
        re += chr(random.randint(65, 90))
    return re


# 发布评论
@app.route('/post_issue/<shop>', methods=['GET', 'POST'])
@login_limit
@ban_comment
def post_issue(shop):
    if '@' not in shop:
        shop = '@'.join(shop.split('-'))
    if request.method == 'GET':
        return "发布评论页面"
    if request.method == 'POST':
        title = request.form.get('title')
        if not title: title = '未命名的标题'
        comment = request.form.get('editorValue')
        email = session.get('email')
        issue_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur = db.cursor()
            Ino = gengenerateID()
            sql = "select * from Issue where Ino = '%s'" % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            # 如果result不为空，即存在该ID，就一直生成128位随机ID,直到不重复位置
            while result is not None:
                Ino = gengenerateID()
                sql = "select * from Issue where Ino = '%s'" % Ino
                db.ping(reconnect=True)
                cur.execute(sql)
                result = cur.fetchone()
            sql = "insert into Issue(Ino, email, title, issue_time, shop) VALUES ('%s','%s','%s','%s','%s')" % (
                Ino, email, title, issue_time, shop)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            sql = "insert into Comment(Cno, Ino, comment, comment_time, email, shop) VALUES ('%s','%s','%s','%s','%s','%s')" % (
                '1', Ino, comment, issue_time, email, shop)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
            return "发表评论成功"
        except Exception as e:
            raise e


# 我的收藏
@app.route('/my_fav')
@login_limit
def my_fav():
    if request.method == 'GET':
        email = session.get("email")
        try:
            cur = db.cursor()
            sql = "select UserInformation.nickname,fav.food,fav.shop_email from fav,UserInformation where fav.shop_email = UserInformation.email and fav.email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            fav_list = list(cur.fetchall())
            pager_obj = Pagination(request.args.get("page", 1), len(fav_list), request.path, request.args,
                                   per_page_count=10,
                                   max_pager_count=11)
            index_list = fav_list[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
        except Exception as e:
            raise e
        return "我的收藏页面"


# 我的关注
@app.route('/my_follow')
@login_limit
def my_follow():
    if request.method == 'GET':
        email = session.get("email")
        try:
            cur = db.cursor()
            sql = "select UserInformation.nickname,follow.follow_email from follow,UserInformation where follow.follow_email = UserInformation.email and follow.email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            fav_list = list(cur.fetchall())
            pager_obj = Pagination(request.args.get("page", 1), len(fav_list), request.path, request.args,
                                   per_page_count=10,
                                   max_pager_count=11)
            index_list = fav_list[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
        except Exception as e:
            raise e
        return "我的关注页面"


# 我的粉丝
@app.route('/my_followed')
@login_limit
def my_followed():
    if request.method == 'GET':
        email = session.get("email")
        try:
            ans=[]
            cur = db.cursor()
            sql = "select UserInformation.nickname,follow.email from follow,UserInformation where follow.email = UserInformation.email and follow.follow_email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            fav_list = list(cur.fetchall())
            for item in fav_list:
                sql = "select others from follow where email='%s' and follow_email = '%s'" % (email,item[1])
                db.ping(reconnect=True)
                cur.execute(sql)
                list1=cur.fetchone()
                if list1:ans.append(list1)
                else:ans.append(tuple())
            pager_obj = Pagination(request.args.get("page", 1), len(fav_list), request.path, request.args,
                                   per_page_count=10,
                                   max_pager_count=11)
            index_list = fav_list[pager_obj.start:pager_obj.end]
            ans2=ans[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
        except Exception as e:
            raise e
        return "我的粉丝页面"



# 论坛页面
@app.route('/formula')
def formula():
    if request.method == 'GET':
        try:
            cur = db.cursor()
            sql = "select Issue.Ino, Issue.email,UserInformation.nickname,issue_time,Issue.title,Comment.comment from Issue,UserInformation,Comment where Issue.email = UserInformation.email and Issue.Ino = Comment.Ino and Cno = '1' order by issue_time DESC "
            db.ping(reconnect=True)
            cur.execute(sql)
            issue_information = cur.fetchall()
            cur.close()
            return "论坛页面"
        except Exception as e:
            raise e


# 商家页面
@app.route('/shop')
def shop():
    if request.method == 'GET':
        try:
            tags=[]
            cur = db.cursor()
            sql = "select shop,COUNT(shop) AS shopnum from orderdata GROUP BY shop"
            db.ping(reconnect=True)
            cur.execute(sql)
            num=cur.fetchall()
            for item in num:
                sql="UPDATE UserInformation SET num='%s' where email = '%s'" % (item[1], item[0])
                db.ping(reconnect=True)
                cur.execute(sql)
            db.commit()
            sql = "select nickname, address, information, photo, email,num from UserInformation where type = '%s' ORDER BY num DESC" % '1'
            db.ping(reconnect=True)
            cur.execute(sql)
            issue_information = list(cur.fetchall())
            for item in issue_information:
                sql = "select tag from shoptags where email='%s'" % item[4]
                db.ping(reconnect=True)
                cur.execute(sql)
                tags.append(cur.fetchall())
            cur.close()
            pager_obj = Pagination(request.args.get("page", 1), len(issue_information), request.path, request.args,
                                   per_page_count=10,
                                   max_pager_count=11)
            index_list = issue_information[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            tag = tags[pager_obj.start:pager_obj.end]
            return "商家页面"
        except Exception as e:
            raise e


# 商家详情
@app.route('/shop_detail/<Ino>', methods=['GET', 'POST'])
def shop_detail(Ino):
    if request.method == 'POST':
        result = request.form.get("result")
        cur = db.cursor()
        sql = "delete from shopdata where id = '%s'" % result
        db.ping(reconnect=True)
        cur.execute(sql)
        db.commit()
        cur.close()
        return "删除成功"
    if '@' not in Ino:
        Ino = '@'.join(Ino.split('-'))
    email = session.get('email')
    flag = False
    if email == Ino: flag = True
    try:
        cur = db.cursor()
        sql = "select * from shoptype where email = '%s'" % Ino
        db.ping(reconnect=True)
        cur.execute(sql)
        shop_type = cur.fetchone()
        sql = "select title, price, information, photo, type, movie from shopdata where email = '%s' order by type" % Ino
        db.ping(reconnect=True)
        cur.execute(sql)
        issue_information = cur.fetchall()
        cur.close()
        return "商家详情"
    except Exception as e:
        raise e


# 播放视频
@app.route('/movie/<Ino>', methods=['GET', 'POST'])
def movie(Ino):
    return "视频播放页面"


# 点餐
@app.route('/order/<Ino>', methods=['GET', 'POST'])
@login_limit
def order(Ino):
    if request.method == 'GET':
        if '@' not in Ino:
            Ino = '@'.join(Ino.split('-'))
        email = session.get('email')
        try:
            cur = db.cursor()
            sql = "select * from shoptype where email = '%s'" % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            shop_type = cur.fetchone()
            sql = "select title, price, information, photo, type, movie from shopdata where email = '%s' order by type" % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            issue_information = cur.fetchall()
            sql = "select food from likes where email = '%s' and shop_email = '%s'" % (email, Ino)
            db.ping(reconnect=True)
            cur.execute(sql)
            likes_inf = cur.fetchall()
            sql = "select food from fav where email = '%s' and shop_email = '%s'" % (email, Ino)
            db.ping(reconnect=True)
            cur.execute(sql)
            fav_inf = cur.fetchall()
            cur.close()
            k = []
            if likes_inf:
                for value in likes_inf:
                    k.append(value[0])
            k2 = []
            if fav_inf:
                for value in fav_inf:
                    k2.append(value[0])
            return "点餐页面"
        except Exception as e:
            raise e
    if request.method == 'POST':
        if '@' not in Ino:
            Ino = '@'.join(Ino.split('-'))
        email = session.get('email')
        information = request.form.get('result')
        submit_time = time.strftime("%Y-%m-%d %H:%M:%S")
        arrive_time = time.time() + random.randint(1000, 3600)
        time_tuples = time.localtime(arrive_time)
        # 转换成字符串
        arrive_time = time.strftime("%Y-%m-%d %H:%M:%S", time_tuples)
        try:
            cur = db.cursor()
            id = random.randint(1000000,9999999)
            while 1:
                sql ="select ino from orderdata where id='%s'" % id
                db.ping(reconnect=True)
                cur.execute(sql)
                if not cur.fetchone():break
            sql = "insert into orderdata(email, information, shop, submit_time, arrive_time, ino, id) VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (
                email, information, Ino, submit_time, arrive_time, "False",id)
            db.ping(reconnect=True)
            cur.execute(sql)
            money = float(str(information).split("%")[-1]) - 3
            sql = "insert into ordermoney(email, shop, submit_time, money_shop, money_horse, id) VALUES ('%s','%s','%s','%s','%s','%s')" % (
                        email, Ino,  submit_time, str(money),"3",id)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
            return "点餐完成"
        except Exception as e:
            raise e


# 订单详情
@app.route('/orderdata/<Ino>', methods=['GET', 'POST'])
@login_limit
def orderdata(Ino):
    if request.method == 'POST':
        email = session.get('email')
        type1 = session.get("type")
        information = request.form.get('result')
        information2 = request.form.get('result2')
        if information2:
            money = float(request.form.get('text' + information2))
            t = information.split("/")
            try:
                cur = db.cursor()
                sql = "select email from userinformation where nickname = '%s'" % t[0]
                db.ping(reconnect=True)
                cur.execute(sql)
                shop_name = str(cur.fetchone())
                t[0] = str(shop_name).split("'")[1]
                sql = "select money_horse from ordermoney where shop = '%s' and submit_time = '%s'" % (t[0], t[1])
                db.ping(reconnect=True)
                cur.execute(sql)
                old_money = float(cur.fetchone()[0])
                money += old_money
                sql = "update ordermoney set money_horse = '%s' where shop = '%s' and submit_time = '%s'" % (
                money, t[0], t[1])
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
            except Exception as e:
                raise e
    if '@' not in Ino:
        Ino = '@'.join(Ino.split('-'))
    email = session.get('email')
    type1 = session.get('type')
    if email == Ino:
        ans = []
        try:
            cur = db.cursor()
            sql = ""
            if type1 == 0:
                sql = "select * from orderdata where email = '%s' order by submit_time" % Ino
            elif type1 == 1:
                sql = "select * from orderdata where shop = '%s' order by submit_time" % Ino
            elif type1 == 2:
                sql = "select * from orderdata where ino = '%s' or ( (ino ='%s' or ino='%s') and horseman='%s') order by submit_time" % (
                "Get", "Go", "True", email)
            db.ping(reconnect=True)
            cur.execute(sql)
            order_data = list(cur.fetchall())
            for j in range(len(order_data)):
                p = list(order_data[j])
                if type1 == 1: p[2], p[0] = p[0], p[2]
                sql = "select nickname from userinformation where email = '%s'" % p[2]
                db.ping(reconnect=True)
                cur.execute(sql)
                shop_name = cur.fetchone()
                p[2] = shop_name[0]
                if p[6]:
                    sql = "select nickname from userinformation where email = '%s'" % p[6]
                    db.ping(reconnect=True)
                    cur.execute(sql)
                    horseman_name = cur.fetchone()
                    p.append(p[6])
                    p[6] = str(horseman_name[0])
                if p[5] == "True" and type1 == 2:
                    sql = "select money_horse from ordermoney where email = '%s' and submit_time='%s'" % (p[0], p[3])
                    db.ping(reconnect=True)
                    cur.execute(sql)
                    money_horse = cur.fetchone()[0]
                    p.append(money_horse)
                ans.append(tuple(p))
            cur.close()
            ans.reverse()
            pager_obj = Pagination(request.args.get("page", 1), len(ans), request.path, request.args, per_page_count=10,
                                   max_pager_count=11)
            index_list = ans[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return "订单详情页面"
        except Exception as e:
            raise e
    else:
        return "无法查看他人订单"


# 评论详情
@app.route('/issue/<Ino>', methods=['GET', 'POST'])
@login_limit
def issue_detail(Ino):
    if request.method == 'GET':
        try:
            if request.method == 'GET':
                email = session.get('email')
                cur = db.cursor()
                sql = "select Issue.title from Issue where Ino = '%s' and ban = '0'" % Ino
                db.ping(reconnect=True)
                cur.execute(sql)
                # 这里返回的是一个列表，即使只有一个数据，所以这里使用cur.fetchone()[0]
                issue_title = cur.fetchone()[0]
                sql = "select UserInformation.nickname,Comment.comment,Comment.comment_time,Comment.Cno, Comment.email from Comment,UserInformation where Comment.email = UserInformation.email and Ino = '%s' and Comment.ban = '0'" % Ino
                db.ping(reconnect=True)
                cur.execute(sql)
                comment = cur.fetchall()
                sql = "select comment from ban where email='%s'" % email
                db.ping(reconnect=True)
                cur.execute(sql)
                ans = cur.fetchone()
                flag = True
                if not ans or not ans[0]:
                    flag = True
                else:
                    flag = False
                cur.close()
                # 返回视图，同时传递参数
                return "评论详情页面"
        except Exception as e:
            raise e

    if request.method == 'POST':
        Ino = request.values.get('Ino')
        email = session.get('email')
        comment = request.values.get('editorValue')
        comment_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur = db.cursor()
            sql = "select max(Cno) from Comment where Ino = '%s' " % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            Cno = int(result[0]) + 1
            Cno = str(Cno)
            sql = "insert into Comment(Cno, Ino, comment, comment_time, email) VALUES ('%s','%s','%s','%s','%s')" % (
                Cno, Ino, comment, comment_time, email)
            cur.execute(sql)
            db.commit()
            cur.close()
            return "发布评论成功"
        except Exception as e:
            raise e


# 个人中心
@app.route('/personal/<Ino>')
@login_limit
def personal(Ino):
    if request.method == 'GET':
        email=session.get("email")
        if '@' not in Ino:
            Ino = '@'.join(Ino.split('-'))
        try:
            cur = db.cursor()
            sql = "select email, nickname, type, create_time, phone, address, information, photo from UserInformation where email = '%s'" % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            personal_info = cur.fetchone()
            sql = "select * from follow where email = '%s' and follow_email = '%s' " % (email,Ino)
            db.ping(reconnect=True)
            cur.execute(sql)
            flag = cur.fetchone()
        except Exception as e:
            raise e
        return "个人中心页面"


# 修改密码
@app.route('/change_password', methods=['GET', 'POST'])
@login_limit
def change_password():
    if request.method == 'GET':
        return "修改密码页面"
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password1 = request.form.get('new_password1')
        new_password2 = request.form.get('new_password2')
        if not all([old_password, new_password1, new_password2]):
            return "信息填写不全"
        if new_password1 != new_password2:
            return "两次新密码不一致"
        email = session.get('email')
        try:
            cur = db.cursor()
            sql = "select password from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            password = cur.fetchone()[0]
            if check_password_hash(password, old_password):
                password = generate_password_hash(new_password1, method="pbkdf2:sha256", salt_length=8)
                sql = "update UserInformation set password = '%s' where email = '%s'" % (password, email)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
                return "修改密码成功"
            else:
                return "旧密码错误"
        except Exception as e:
            raise e


ALLOWED_EXTENSIONS = {'jpg', 'JPG'}
ALLOWED_EXTENSIONS2 = {'MP4', 'mp4'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1]





# 修改个人信息
@app.route('/change_info', methods=['GET', 'POST'])
@login_limit
def change_info():
    if request.method == 'GET':
        email = session.get('email')
        tags=""
        try:
            cur = db.cursor()
            sql = "select nickname, phone, address, information from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            personal_info = cur.fetchone()
            sql = "select tag from shoptags where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            tuple1=cur.fetchall()
            for item in tuple1:
                tags+=item[0]
        except Exception as e:
            raise e
        return "修改个人信息页面"
    if request.method == 'POST':
        new_nickname = request.form.get('new_nickname')
        new_phone = request.form.get('new_phone')
        new_address = request.form.get('new_address')
        new_info = request.form.get('new_info')
        new_photo = request.files.get('new_photo')
        new_tags=""
        return1,return2="",""
        if str(session.get("type"))=='1': new_tags=request.form.get('tags')
        if new_photo:return1="照片"
        if new_tags:return2="标签"
        print(session.get("type"),new_tags,return2)
        if not all([new_nickname, new_phone, new_address, new_info]):
            return "信息填写不全"
        email = session.get('email')
        try:
            cur = db.cursor()
            if new_photo and not allowed_file(new_photo.filename) in ALLOWED_EXTENSIONS:
                return "上传照片格式错误"
            if new_photo and allowed_file(new_photo.filename) in ALLOWED_EXTENSIONS:
                print(new_photo)
                path = "/static/img/"
                file_path = path + create_uuid() + '.jpg'
                new_photo.save(basedir + file_path)
                sql = "select photo from UserInformation where email = '%s'" % email
                db.ping(reconnect=True)
                cur.execute(sql)
                personal_photo = cur.fetchone()
                if str(personal_photo[0]) != '/static/img/None.jpg':
                    os.remove(basedir + str(personal_photo[0]))
                sql = "UPDATE UserInformation SET photo='%s' where email = '%s'" % (file_path, email)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
            sql = "UPDATE UserInformation SET nickname='%s', phone='%s', address='%s', information='%s' where email = '%s'" % (
            new_nickname, new_phone, new_address, new_info, email)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            if new_tags:
                list1=new_tags.split("-")
                sql = "delete from shoptags where email = '%s'" % email
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                for item in list1:
                    sql = "insert into shoptags(email,tag) VALUES ('%s','%s')" % (email,item)
                    db.ping(reconnect=True)
                    cur.execute(sql)
                    db.commit()
            cur.close()
            return "修改个人信息成功"+return1+return2
        except Exception as e:
            raise e


# 上传菜品
@app.route('/create_food', methods=['GET', 'POST'])
@login_limit
def create_food():
    if request.method == 'GET':
        email=session.get('email')
        cur = db.cursor()
        sql = "select type0, type1, type2, type3, type4, type5, type6, type7, type8, type9 from shoptype where email = '%s'" % email
        db.ping(reconnect=True)
        cur.execute(sql)
        type1 = cur.fetchone()
        return "上传菜品页面"
    if request.method == 'POST':
        new_name = request.form.get('new_name')
        new_price = request.form.get('new_price')
        new_info = request.form.get('new_info')
        new_photo = request.files.get('new_photo')
        new_movie = request.files.get('new_movie')
        type1 = request.form.get('type1')
        if not all([new_name, new_price, new_photo, new_info, type1]):
            return "信息填写不全"
        if not allowed_file(new_photo.filename) in ALLOWED_EXTENSIONS:
            return "上传照片格式错误"
        if new_movie and not allowed_file(new_movie.filename) in ALLOWED_EXTENSIONS2:
            return "上传视频格式错误"
        try:
            new_price = round(float(new_price), 2)
        except:
            return "商品价格错误"
        email = session.get('email')
        try:
            cur = db.cursor()
            path = "/static/img/"
            file_path = path + create_uuid() + '.jpg'
            new_photo.save(basedir + file_path)
            movie_path = ''
            if new_movie:
                path = "/static/movie/"
                movie_path = path + create_uuid() + '.mp4'
                new_movie.save(basedir + movie_path)
            sql = "insert into shopdata(email, title, price, information, photo, type, likes, fav ,repeats, movie) VALUES ('%s','%s','%s','%s','%s','%s','0','0','0','%s')" % (
                email, new_name, new_price, new_info, file_path, type1, movie_path)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
            return "添加商品成功"
        except Exception as e:
            raise e


# 编辑菜品类型
@app.route('/change_type', methods=['GET', 'POST'])
@login_limit
def change_type():
    email = session.get('email')
    if request.method == 'GET':
        try:
            cur = db.cursor()
            sql = "select type0, type1, type2, type3, type4, type5, type6, type7, type8, type9 from shoptype where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            change_type = cur.fetchone()
        except Exception as e:
            raise e
        return "编辑菜品类型页面"
    if request.method == 'POST':
        type0 = request.form.get('type0')
        type1 = request.form.get('type1')
        type2 = request.form.get('type2')
        type3 = request.form.get('type3')
        type4 = request.form.get('type4')
        type5 = request.form.get('type5')
        type6 = request.form.get('type6')
        type7 = request.form.get('type7')
        type8 = request.form.get('type8')
        type9 = request.form.get('type9')
        try:
            cur = db.cursor()
            sql = "select * from shoptype where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            change_type = cur.fetchone()
            if change_type is None:
                sql = "insert into shoptype(email, type0, type1, type2, type3, type4, type5, type6, type7, type8, type9) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                    email, type0, type1, type2, type3, type4, type5, type6, type7, type8, type9)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
            else:
                sql = "UPDATE shoptype SET type0='%s', type1='%s',type2='%s',type3='%s',type4='%s',type5='%s',type6='%s',type7='%s',type8='%s',type9='%s' where email = '%s'" % (
                    type0, type1, type2, type3, type4, type5, type6, type7, type8, type9, email)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
            return "编辑菜品类型成功"
        except Exception as e:
            raise e


# 查看顾客评论
@app.route('/show_issue/<Ino>')
@login_limit
def show_issue(Ino):
    if request.method == 'GET':
        if '@' not in Ino:
            Ino = '@'.join(Ino.split('-'))
        ans = []
        try:
            cur = db.cursor()
            sql = "select ino, email, title, issue_time, shop from Issue where shop = '%s' and ban = '0' order by issue_time desc" % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            issue_detail = cur.fetchall()
            for item in issue_detail:
                p = list(item)
                sql = "select nickname from userinformation where email = '%s'" % item[1]
                db.ping(reconnect=True)
                cur.execute(sql)
                p.append(cur.fetchone()[0])
                ans.append(tuple(p))
        except Exception as e:
            raise e
        return "查看顾客评论页面"


# 生成120位随机id
def gengenerateFno():
    re = ""
    for i in range(120):
        re += chr(random.randint(65, 90))
    return re





# 点赞
@app.route('/like/<Ino>', methods=['POST'])
@login_limit
def like(Ino):
    t = Ino.split('-')
    cur = db.cursor()
    sql = "select judge from likes where email = '%s' and shop_email = '%s' and food = '%s'" % (t[0], t[1], t[2])
    db.ping(reconnect=True)
    cur.execute(sql)
    result = cur.fetchone()
    try:
        if not result:
            sql = "insert into likes(email, shop_email, food, judge) VALUES ('%s','%s','%s','%s')" % (
            t[0], t[1], t[2], True)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
        else:
            sql = "DELETE FROM likes WHERE email = '%s' and shop_email = '%s' and food = '%s'" % (t[0], t[1], t[2])
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
    except Exception as e:
        raise e
    return "点赞成功"


# 收藏
@app.route('/fav/<Ino>', methods=['POST'])
@login_limit
def fav(Ino):
    t = Ino.split('-')
    cur = db.cursor()
    sql = "select judge from fav where email = '%s' and shop_email = '%s' and food = '%s'" % (t[0], t[1], t[2])
    db.ping(reconnect=True)
    cur.execute(sql)
    result = cur.fetchone()
    try:
        if not result:
            sql = "insert into fav(email, shop_email, food, judge) VALUES ('%s','%s','%s','%s')" % (
            t[0], t[1], t[2], True)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
        else:
            sql = "DELETE FROM fav WHERE email = '%s' and shop_email = '%s' and food = '%s'" % (t[0], t[1], t[2])
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
    except Exception as e:
        raise e
    return "收藏成功"


# 关注
@app.route('/follow/', methods=['POST'])
@login_limit
def follow():
    t=[]
    t.append(request.form.get('email'))
    t.append(request.form.get('follow_email'))
    cur = db.cursor()
    sql = "select * from follow where email = '%s' and follow_email = '%s'" % (t[0], t[1])
    db.ping(reconnect=True)
    cur.execute(sql)
    result = cur.fetchone()
    try:
        if not result:
            sql = "insert into follow(email, follow_email, others) VALUES ('%s','%s','%s')" % (
            t[0], t[1], "normal")
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
        else:
            sql = "DELETE FROM follow WHERE email = '%s' and follow_email = '%s'" % (t[0], t[1])
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
    except Exception as e:
        raise e
    return "关注成功"


# 商家查询
@app.route('/search_ans/<path:Ino>/<int:value>', methods=['POST','GET'])
@login_limit
def search_ans(Ino,value):
    try:
        sql=""
        tags=[]
        cur = db.cursor()
        if str(value)=="0":
            sql = "select nickname, address, information, photo, email,num from UserInformation where type = '%s' and nickname like '%%%s%%'" % ('1',Ino)
        elif str(value)=="1":
            sql = "select DISTINCT userinformation.nickname, userinformation.address, userinformation.information, userinformation.photo, userinformation.email, userinformation.num from userinformation,shopdata where  shopdata.title like '%%%s%%' and shopdata.email=userinformation.email" % Ino
        elif str(value)=="2":
            sql = "select DISTINCT userinformation.nickname, userinformation.address, userinformation.information, userinformation.photo, userinformation.email, userinformation.num from userinformation,shoptags where  shoptags.tag = '%s' and shoptags.email=userinformation.email" % Ino
        else:return redirect(url_for('index'))
        db.ping(reconnect=True)
        cur.execute(sql)
        issue_information = list(cur.fetchall())
        for item in issue_information:
            sql = "select tag from shoptags where email='%s'" % item[4]
            db.ping(reconnect=True)
            cur.execute(sql)
            tags.append(cur.fetchall())
        cur.close()
        pager_obj = Pagination(request.args.get("page", 1), len(issue_information), request.path, request.args,
                               per_page_count=10,
                               max_pager_count=11)
        index_list = issue_information[pager_obj.start:pager_obj.end]
        tag=tags[pager_obj.start:pager_obj.end]
        html = pager_obj.page_html()
        return "商家查询成功"
    except Exception as e:
        raise e






# 富文本编辑器后台配置
@app.route('/upload/', methods=['GET', 'POST', 'OPTIONS'])
def upload():
    """UEditor文件上传接口

    config 配置文件
    result 返回结果
    """
    result = {}
    action = request.args.get('action')

    # 解析JSON格式的配置文件
    with open(os.path.join(app.static_folder, 'ueditor', 'php',
                           'config.json'), encoding='utf-8') as fp:

        # 删除 `/**/` 之间的注释
        CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG

    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }

        if fieldName in request.files:
            field = request.files[fieldName]
            uploader = Uploader(field, config, app.static_folder)
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in request.form:
            field = request.form[fieldName]
            uploader = Uploader(field, config, app.static_folder, 'base64')
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']

        if fieldName in request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in request.form:
            # 而是这个
            source = request.form.getlist('%s[]' % fieldName)

        _list = []
        for imgurl in source:
            uploader = Uploader(imgurl, config, app.static_folder, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })

        result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
        result['list'] = _list

    else:
        result['state'] = '请求地址出错'

    result = json.dumps(result)

    if 'callback' in request.args:
        callback = request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            return '%s(%s)' % (callback, result)
        return json.dumps({'state': 'callback参数不合法'})

    res = make_response(result)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
    return res



socketio.on_namespace(MyCustomNamespace('/chatroom'))
if __name__ == '__main__':
    cov = Coverage()
    cov.start()
    try:
        print("qidong")
        socketio.run(app)
    except KeyboardInterrupt as e:
        pass
    finally:
        cov.stop()  # 停止纪录
        print("guanbi")
        cov.save()  # 保存在 .coverage 中
        print("save")
        cov.html_report()
