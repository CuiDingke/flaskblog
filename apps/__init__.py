from flask import Flask
import settings
from apps.article.view import article_bp1
from apps.user.view import user_bp1
from exts import db, bootstrap, cache

config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '39.107.138.229',
    'CACHE_REDIS_PORT': 6379
}


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(settings.DevelopmentConfig)
    # 注册蓝图
    app.register_blueprint(user_bp1)
    app.register_blueprint(article_bp1)
    # 初始化
    db.init_app(app)
    # 初始化Bootstrap
    bootstrap.init_app(app)
    # 初始化缓存文件
    cache.init_app(app=app, config=config)
    return app
