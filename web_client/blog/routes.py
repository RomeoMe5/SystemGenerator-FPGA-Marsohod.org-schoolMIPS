from flask import abort, current_app, render_template, url_for
from flask_babel import _
from flask_login import login_required

from engine.boards import BOARDS
from web_client.blog import bp
from web_client.models import BlogPost


@bp.route('/')
@bp.route('/<link>')
@login_required
def articles(link: str = None) -> object:
    if link is not None:
        article = BlogPost.query.filter_by(_link=link).first()
        if article is None:
            return abort(404)
        return render_template(
            article.rel_path,
            base_link=article.link,
            title=article.title,
            date=article.date,
            boards=BOARDS
        )

    articles = []
    for article in BlogPost.query.all():
        articles.append((
            article.title,
            article.date,
            url_for("blog.articles", link=article.link)
        ))

    return render_template(
        "blog/posts.html",
        title=_("Articles"),
        blog_posts=articles,
        boards=BOARDS
    )
