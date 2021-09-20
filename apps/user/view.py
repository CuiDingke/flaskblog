import codecs
import os.path

from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from apps.article.models import Article_category, Article
from apps.user.models import User, Photo, AboutMe, MessageBoard
from apps.utils.util import *
from exts import db, cache
from settings import Config
from flask_caching import Cache

user_bp1 = Blueprint('user', __name__, url_prefix='/user')

# 需要验证的路径  验证是否登录了
required_login_list = ['/user/center', '/user/change', '/article/publish', '/user/upload_photo', '/user/photo_del',
                       '/article/add_comment', '/user/about', '/user/me']


@user_bp1.before_app_first_request
def first_request():
    print('before_app_first_request')


# 钩子 勾到登录页面  ============== 重点********
@user_bp1.before_app_request
def before_request():
    print('before_app_request', request.path)
    if request.path in required_login_list:
        id = session.get('uid')
        if not id:
            types = Article_category.query.all()
            return render_template('user/login.html', types=types)
        else:
            user = User.query.get(id)
            # 本次请求的一个对象  g只在这一次请求是有效的
            g.user = user
            # return render_template('user/center.html', user=user)


# 一定要拿着response对象 往回走
# 一般也不会用   只有做特殊处理时  才会使用
@user_bp1.after_app_request
def after_request(response):
    # response.set_cookie('a', 'b', max_age = 19)
    print('after_request')
    return response


@user_bp1.teardown_app_request
def teardown_request(response):
    print('teardown_request')
    return response


@user_bp1.app_template_filter('cdecode')
def content_decode(content):
    content = content.decode('utf-8')
    return content[:200]


# @cache.cached(timeout=5)
# 首页
@user_bp1.route('/')
def index():
    # 获取cookie 通过request对象获取
    # uid = request.cookies.get('uid', None)
    # 2.session 获取 session底层默认获取
    uid = session.get('uid', None)
    # 接收页码数   如果收不到默认为1
    page = int(request.args.get('page', 1))
    types = Article_category.query.all()
    # 查询了所有的文章
    articles = Article.query.order_by(-Article.pdatetime).all()
    # 为了实现分页  用paginate  page第几页的数据  每页多少个  也可以设置最大页  返回的是对象 不是列表
    pagination = Article.query.order_by(-Article.pdatetime).paginate(page=page, per_page=7)
    print(pagination.items)  # [<Article 5>, <Article 4>, <Article 3>, <Article 2>]
    print(pagination.page)  # 2  当前的页码数
    print(pagination.prev_num)  # 1  当前页的前一页的页码数
    print(pagination.next_num)  # 3  当前页的后一页的页码数
    print(pagination.has_next)  # True 是否有下一页
    print(pagination.has_prev)
    print(pagination.pages)  # 一共有多少页
    print(pagination.total)  # 一共有多少条目
    if uid:
        user = User.query.get(uid)
        params = {
            'user': user,
            'types': types,
            'articles': articles,
            'pagination': pagination,

        }
        return render_template('user/index.html', **params)
    else:
        return render_template('user/index.html', types=types, articles=articles, pagination=pagination)


# 用户注册
@user_bp1.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if password == repassword:
            # 注册用户
            users = User.query.filter(User.isdelele == False).all()
            for user_c in users:
                if user_c.phone == phone:
                    return render_template('user/register.html')
            user = User()
            user.username = username
            # 使用自带的函数加密 generate_password_hash
            user.password = generate_password_hash(password)
            user.phone = phone
            user.email = email
            user.icon = 'Images/touxiang.jpg'
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user.user_login'))
        else:
            return render_template('user/register.html')
    return render_template('user/register.html')


# 手机号码
@user_bp1.route('/checkphone')
def check_phone():
    phone = request.args.get('phone')
    user = User.query.filter(User.phone == phone).all()
    # code:400 不能用  code:200 可以用
    if user:
        return jsonify(code=400, msg='此号码已被注册')
    else:
        return jsonify(code=200, msg='此号码可用')


# 登录
@user_bp1.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        f = request.args.get('f')
        print(f)
        if f == '1':
            username = request.form.get('username')
            password = request.form.get('password')
            user_list = User.query.filter(User.username == username).all()
            for user in user_list:
                flag = check_password_hash(user.password, password)
                # 查看flag是否为true
                if flag:
                    # 1.设置cookie  保存cookie    response.set_cookie(key,value,max_age)
                    # response = redirect(url_for('user.index'))
                    # response.set_cookie('uid', str(user.id), max_age=1800)
                    # return response
                    # 2.session机制,session当作字典使用
                    session['uid'] = user.id
                    return redirect(url_for('user.index'))
            return render_template('user/login.html', msg='密码有误')
        elif f == '2':
            phone = request.form.get('phone')
            code = request.form.get('code')
            # 先验证验证码 session 取值
            # valid_code = session.get(phone, None)
            # redis 取值
            valid_code = cache.get(phone)
            if code == valid_code:
                user = User.query.filter(User.phone == phone).first()
                if user:
                    session['uid'] = user.id
                    return redirect(url_for('user.index'))
                return render_template('user/login.html', msg='此号码未注册')
            return render_template('user/login.html', msg='验证码有误！')
        return render_template('user/login.html')
    else:
        return render_template('user/login.html')


@user_bp1.route('/logout')
def logout():
    response = redirect(url_for('user.index'))
    # 通过response对象的deledelete_cookie(key) key就是要删除的键值 直接删除uid
    # 1. cookie删除
    # response.delete_cookie('uid')
    # 2. session删除  del只清除键值对,不会删除session空间和cookie  clear可以删除session的内存空间和删除空间
    # del session['uid']
    # 一般用session.clear()
    session.clear()
    return response


# 点击获取验证码后  会走这个路由  第三方会将所有的信息返回给服务器  服务器通过session存储关键信息
@user_bp1.route('/sendMsg')
def send_message():
    phone = request.args.get('phone')
    print(phone)
    user = User.query.filter(User.phone == phone).first()
    if user:
        ret = util_sendmsg(phone)
        print(ret)
        # 验证是否发送成功
        if ret is not None:
            if ret["code"] == 200:
                obj = ret["obj"]
                print(obj)
                # 用session记录phone 和 验证码
                # session[phone] = obj
                # 将phone和验证码放入redis缓存中  cache.set(key, value, Timeout)
                cache.set(phone, obj, timeout=180)
                return jsonify(cood=200, msg='短信发送成功')
        print("error: ret.code=%s, msg=%s" % (ret["code"], ret["msg"]))
        return jsonify(cood=400, msg='短信发送失败')
        # session[phone] = '111111'
        # return jsonify(cood=200, msg='短信发送成功')
    else:
        return jsonify(cood=450, msg='此号码未注册')


@user_bp1.route('/center')
def user_center():
    # 1. 不用钩子 自己验证  但是这个在浏览器上直接输 也可以进入  不是我们所需要的
    # uid = session.get('uid', None)
    # if uid:
    #     user = User.query.get(uid)
    #     return render_template('user/center.html', user=user)
    # else:
    #     return render_template('user/index.html')
    # 2. 用钩子函数
    types = Article_category.query.all()
    # 获取用户photo的名字
    photos = Photo.query.filter(Photo.user_id == g.user.id).all()
    # 获取用户留言
    messages = MessageBoard.query.filter(MessageBoard.user_id == g.user.id).order_by(-MessageBoard.mdatetime).all()
    print(messages)
    return render_template('user/center.html', user=g.user, types=types, photos=photos, messages=messages)


# 可以上传的图片的扩展名
ALLOWED_EXTENSTIONS = ['jpg', 'png', 'gif', 'bmp']


# 用户信息修改
@user_bp1.route('/change', methods=['GET', 'POST'])
def user_change():
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        # 只要有文件、图片，获取的方式必须使用request.files.get()
        icon = request.files.get('icon')  # FileStorage 类型
        # 属性：filename 用户获取文件的名字
        # 方法: save(保存路径)
        icon_name = icon.filename  # 1111.jpg
        # 判断 后缀名是不是图片
        suffix = icon_name.rsplit('.')[-1]
        if suffix in ALLOWED_EXTENSTIONS:
            # 将文件进行安全检查  比如将空格、其他符号给搞掉  保证文件名符合python规则
            icon_name = secure_filename(icon_name)
            print(icon_name)
            file_path = os.path.join(Config.UPLOAD_ICON_DIR, icon_name)
            file_path = Path(file_path).as_posix()
            # file_path = file_path.replace('/', '\\')
            print('== == == == == == == == == == == == == ==')
            print(file_path)
            print('== == == == == == == == == == == == == ==')
            # 保存在本地  将图片
            icon.save(file_path)
            # 保存成功
            user = g.user
            user.username = username
            user.phone = phone
            user.email = email
            # 在页面加载时 是基于static文件夹去寻找的文件 只需要上传相对路径就行 upload/icon/...jpg
            # 将图片的本地路径加载到数据库
            path = 'upload/icon'
            file_path = Path(os.path.join(path, icon_name)).as_posix()
            user.icon = file_path
            db.session.commit()
            return redirect(url_for('user.user_center'))
        else:
            render_template('user/center.html', user=g.user, msg='文件格式错误')
        # 查询手机号码   ajax已经做了 ==这段可以不用
        # users = User.query.all()
        # for user in users:
        #     if user.phone == phone:
        #         # 说明已经有人用了 手机号码
        #         user = g.user
        #         user.username = username
        #         user.phone = phone
        #         user.email = email
        #         # 在页面加载时 是基于static文件夹去寻找的文件 只需要上传相对路径就行 upload/icon/...jpg
        #         path = 'upload/icon'
        #         user.icon = os.path.join(path, icon_name)
        #         db.session.commit()
        #         return render_template('user/center.html', user=g.user, msg='此号码已经注册')
    return render_template('user/center.html', user=g.user)


# 上传照片===>已经是登陆状态
@user_bp1.route('upload_photo', methods=['GET', 'POST'])
def upload_photo():
    # 获取上传的内容
    photo = request.files.get('photo')
    ret, info = upload_qiniu(photo)
    print(info.status_code)
    print(ret)
    if info.status_code == 200:
        photo = Photo()
        photo.photo_name = ret['key']
        photo.user_id = g.user.id
        db.session.add(photo)
        db.session.commit()
        return redirect(url_for('user.user_center'))
    else:
        return render_template('500.html', err_msg='上传相册图片失败！！')


# 我的相册
@user_bp1.route('/myphoto')
def myphoto():
    # photos = Photo.query.all()
    # 不要忘记那个1
    page = int(request.args.get('page', 1))
    # 分页操作
    # photos是一个pagination对象
    photos = Photo.query.paginate(page=page, per_page=6)
    types = Article_category.query.all()
    id = session.get('uid', None)
    user = User.query.get(id)
    return render_template('user/photos.html', photos=photos, types=types, user=user)


# 删除相册图片
@user_bp1.route('photo_del')
def del_photo():
    pid = request.args.get('pid')
    photo = Photo.query.get(pid)
    filename = photo.photo_name
    # 封装好的一个删除七牛存储文件的函数
    info = del_qiniu(filename)
    # 判断状态码
    if info.status_code == 200:
        # 删除数据库的内容
        db.session.delete(photo)
        db.session.commit()
        return redirect(url_for('user.user_center'))
    else:
        referer = request.headers.get('Referer', None)
        return render_template('500.html', err_msg='删除相册图片失败！！', referer=referer)


# 提交个人介绍
@user_bp1.route('/about', methods=['GET', 'POST'])
def about_me():
    if request.method == 'POST':
        content = request.form.get('content')
        print(content)
        # all() 是个列表 需要遍历 不管返回值有多少个对象  first()  是一个对象
        flag = AboutMe.query.filter(AboutMe.use_id == g.user.id).first()
        if flag:
            flag.content = content.encode('utf-8')
            db.session.commit()
        else:
            me = AboutMe()
            me.content = content.encode('utf-8')
            me.use_id = g.user.id
            db.session.add(me)
            db.session.commit()
        return redirect(url_for('user.me'))
    # try:
    # except Exception as err:
    else:
        referer = request.headers.get('Referer', None)
        return render_template('500.html', err_msg='删除相册图片失败！！', referer=referer)


# 查看个人信息
@user_bp1.route('/me')
def me():
    content = AboutMe.query.filter(AboutMe.use_id == g.user.id).all()
    types = Article_category.query.all()
    return render_template('user/aboutme.html', content=content, user=g.user, types=types)


# 留言板
@user_bp1.route('/board', methods=['GET', 'POST'])
def show_board():
    if request.method == 'POST':
        content = request.form.get('content')
        message = MessageBoard()
        uid = session.get('uid', None)
        if uid:
            message.user_id = uid
        message.content = content
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('user.show_board'))
    else:
        uid = session.get('uid', None)
        user = None
        if uid:
            user = User.query.get(uid)
        page = int(request.args.get('page', 1))
        messages = MessageBoard.query.order_by(-MessageBoard.mdatetime).paginate(page=page, per_page=5)
        types = Article_category.query.all()
        return render_template('user/board.html', user=user, messages=messages, types=types)


# 删除留言
@user_bp1.route('/board_del')
def delete_board():
    mid = request.args.get('mid')
    if mid:
        del_b = MessageBoard.query.get(mid)
        db.session.delete(del_b)
        db.session.commit()
        return redirect(url_for('user.user_center'))
