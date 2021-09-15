from flask import Flask

import settings
from apps.article.view import article_bp1

from apps.user.view import user_bp1

from exts import db, bootstrap


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(settings.DevelopmentConfig)
    app.register_blueprint(user_bp1)
    app.register_blueprint(article_bp1)
    # 初始化
    db.init_app(app)
    bootstrap.init_app(app)
    return app
