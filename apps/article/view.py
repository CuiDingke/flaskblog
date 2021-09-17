from flask import Blueprint, render_template, request, g, redirect, url_for, jsonify, session
from apps.article.models import Article, Article_category, Comment
from apps.user.models import User
from exts import db

article_bp1 = Blueprint('article', __name__, url_prefix='/article')


# 只要需要查看用户信息的  都可以用钩子函数  而且 在登陆后  任何页面都应该走钩子
@article_bp1.route('/publish', methods=['GET', 'POST'])
def publish_article():
    if request.method == 'POST':
        title = request.form.get('title')
        type_id = request.form.get('type')
        content = request.form.get('content')
        print(title, type_id, content)
        # 添加文章
        article = Article()
        article.title = title
        article.category_id = type_id
        article.content = content
        # 增加的为用户的ID  不是用户对象
        article.user_id = g.user.id
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('user.index'))


# 查看文章详情
@article_bp1.route('/detail')
def article_detail():
    # 进详情页  必须传aid 文章的id
    article_id = request.args.get('aid')
    # 查询所有文章
    article = Article.query.get(article_id)
    # 文章类型
    types = Article_category.query.all()
    user_id = session.get('uid', None)
    if user_id:
        user = User.query.get(user_id)
    else:
        user = None
    page = int(request.args.get('page', 1))
    comments = Comment.query.filter(Comment.article_id == article.id).order_by(-Comment.cdatetime).paginate(page=page,
                                                                                                            per_page=5)
    return render_template('article/detail.html', article=article, types=types, user=user, comments=comments)


# 点赞量
@article_bp1.route('/love')
def article_love():
    article_id = request.args.get('aid')
    tag = request.args.get('tag')
    print(article_id)
    article = Article.query.get(article_id)
    if tag == '1':
        article.love_num -= 1
    else:
        article.love_num += 1
    db.session.commit()
    return jsonify(num_love=article.love_num)
    # return redirect(url_for('article.article_detail'))


# 收藏量
@article_bp1.route('/save')
def article_save():
    article_id = request.args.get('aid')
    tag = request.args.get('tag')
    print("tag:", tag)
    article = Article.query.get(article_id)
    if tag == '1':
        article.save_num -= 1
    else:
        article.save_num += 1
    db.session.commit()
    return jsonify(num_save=article.save_num)
    # return redirect(url_for('article.article_detail'))


# 发表评论
@article_bp1.route('/add_comment', methods=['GET', 'POST'])
def article_comment():
    if request.method == 'POST':
        comment_content = request.form.get('content')
        article_id = request.args.get('aid')
        user_id = g.user.id
        # 创建模型
        comment = Comment()
        comment.comment = comment_content
        comment.user_id = user_id
        comment.article_id = article_id
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('article.article_detail') + "?aid=" + article_id)
    return redirect(url_for('user.index'))


# 查看个人信息
@article_bp1.route('/type')
def type_article():
    type_id = request.args.get('type')
    page = int(request.args.get('page', 1))
    articles = Article.query.filter(Article.category_id == type_id).paginate(page=page, per_page=5)
    types = Article_category.query.all()
    uid = session.get('uid', None)
    user = None
    if uid:
        user = User.query.get(uid)
    return render_template('article/type.html', user=user, types=types, articles=articles, type_id=type_id)