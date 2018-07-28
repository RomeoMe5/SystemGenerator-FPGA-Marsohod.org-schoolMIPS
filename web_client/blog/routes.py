from datetime import datetime
from functools import wraps
from typing import Callable, NoReturn

from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_babel import _
from flask_login import current_user, login_required

from web_client import db
from web_client.blog import bp
from web_client.blog.forms import (EditCommentForm, EditPostForm,
                                   UploadImageForm)
from web_client.models import Comment, Post


@bp.before_request
def before_request() -> NoReturn:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


def filter_non_admins(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> object:
        if not current_user.can_edit_posts:
            current_app.logger.debug("Access denied: %s", current_user)
            flash(_("You have no rights to add posts!"))
            return redirect(url_for("blog.posts"))
        return func(*args, **kwargs)
    return wrapper


@bp.route("/")
@login_required
def posts() -> object:
    posts = (Post.query
             .filter_by(visible=True)
             .order_by(Post.create_dt.desc())
             .paginate(
                 request.args.get("page", 1, type=int),
                 current_app.config['POSTS_PER_PAGE'],
                 True  # enable 404 error
             ))

    next_page_url = None
    if posts.has_next:
        next_page_url = url_for("blog.posts", page=posts.next_num)
    prev_page_url = None
    if posts.has_prev:
        prev_page_url = url_for("blog.posts", page=posts.prev_num)

    return render_template(
        "blog/posts.html",
        title=_("Articles"),
        posts=posts.items,
        next_page_url=next_page_url,
        prev_page_url=prev_page_url
    )


@bp.route("/drafts")
@login_required
@filter_non_admins
def drafts() -> object:
    posts = (Post.query
             .filter_by(author=current_user, visible=False)
             .order_by(Post.create_dt.desc())
             .paginate(
                 request.args.get("page", 1, type=int),
                 current_app.config['POSTS_PER_PAGE'],
                 True  # enable 404 error
             ))

    next_page_url = None
    if posts.has_next:
        next_page_url = url_for("blog.posts", page=posts.next_num)
    prev_page_url = None
    if posts.has_prev:
        prev_page_url = url_for("blog.posts", page=posts.prev_num)

    return render_template(
        "blog/posts.html",
        title=_("Drafts of Articles"),
        posts=posts.items,
        next_page_url=next_page_url,
        prev_page_url=prev_page_url
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
@filter_non_admins
def add() -> object:
    form = EditPostForm()
    if form.validate_on_submit():
        post = Post()
        post.title = form.title.data
        post.text = form.text.data
        post.visible = form.visible.data
        post.author = current_user

        current_app.logger.info("Add new post %s", post)
        db.session.add(post)
        db.session.commit()

        flash(_("New post created!"))
        return redirect(post.link)

    return render_template(
        "blog/edit.html",
        title=_("Add Post"),
        form=form
    )


@bp.route("/edit/<uri>", methods=["GET", "POST"])
@login_required
@filter_non_admins
def edit(uri: str) -> object:
    # NOTE only posts authors can edit their posts
    post = Post.query.filter_by(_uri=uri,
                                user_id=current_user.id).first_or_404()
    form = EditPostForm(original_title=post.title)
    if form.validate_on_submit():
        current_app.logger.info("Edit post %s", post)
        post.title = form.title.data
        post.text = form.text.data
        post.visible = form.visible.data
        db.session.commit()
        flash(_("Changes were saved!"))
        return redirect(post.link)
    elif request.method == "GET":
        form.title.data = post.title
        form.text.data = post.raw_text
        form.visible.data = post.visible

    return render_template(
        "blog/edit.html",
        title=_("Edit Post"),
        post=post,
        form=form
    )


@bp.route("/delete/<uri>")
@login_required
@filter_non_admins
def delete(uri: str) -> object:
    # NOTE only posts authors can delete their posts
    post = Post.query.filter_by(_uri=uri,
                                user_id=current_user.id).first_or_404()
    post.delete()
    db.session.delete(post)
    db.session.commit()
    del post
    flash(_("Post was removed"))
    return redirect(url_for("blog.posts"))


@bp.route("/post/<uri>", methods=["GET", "POST"])
@login_required
def view(uri: str) -> object:
    # NOTE only visible posts can be viewed
    post = Post.query.filter_by(_uri=uri).first_or_404()
    if not post.visible and post.author != current_user:
        abort(404)
    comments = post.comments.order_by(Comment.create_dt.desc()).all()
    form = EditCommentForm()
    if form.validate_on_submit():
        comment = Comment()
        comment.text = form.text.data
        comment.post = post
        comment.author = current_user
        current_app.logger.info("Add new comment: %s", comment)
        db.session.add(comment)
        db.session.commit()
        del comment
        flash(_("New comment created!"))
        return redirect(post.link)
    elif post.author != current_user:
        post.watched()
        db.session.commit()

    return render_template(
        "blog/view.html",
        title=post.title,
        post=post,
        comments=comments,
        form=form
    )


@bp.route("/comment/edit/<int:cid>", methods=["GET", "POST"])
@login_required
def edit_comment(cid: int) -> object:
    comment = Comment.query.filter_by(id=cid,
                                      author=current_user).first_or_404()
    form = EditCommentForm()
    if form.validate_on_submit():
        comment.text = form.text.data
        current_app.logger.info("Edit comment: %s", comment)
        db.session.commit()
        flash(_("Comment saved!"))
        return redirect(post.link)
    elif request.method == "GET":
        form.text.data = comment.raw_text

    del comment
    return render_template(
        "blog/edit_comment.html",
        title=_("Edit Comment"),
        form=form
    )
