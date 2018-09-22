from functools import wraps
from typing import Callable

from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_babel import _
from flask_login import current_user, login_required

from web_client import db
from web_client.blog import bp
from web_client.blog.forms import CommentForm, PostForm, UploadImageForm
from web_client.models import Comment, Permission, Post


@bp.route("/")
@login_required
def posts() -> object:
    posts = (Post.query
             .filter_by(visible=True)
             .order_by(Post.create_dt.desc())
             .paginate(
                 request.args.get("page", 1, type=int),
                 current_app.config['ITEMS_PER_PAGE'],
                 True  # enable 404 error
             ))

    next_page = None if not posts.has_next else \
        url_for("blog.posts", page=posts.next_num)
    prev_page = None if not posts.has_prev else \
        url_for("blog.posts", page=posts.prev_num)

    return render_template(
        "blog/posts.html",
        title=_("Articles"),
        posts=posts.items,
        next_page_url=next_page,
        prev_page_url=prev_page
    )


@bp.route("/drafts")
@login_required
def drafts() -> object:
    if not current_user.can(Permission.WRITE):
        return abort(403)
    posts = (
        Post.query
        .filter_by(visible=False)
        .order_by(Post.create_dt.desc())
    )
    if not current_user.is_admin:
        posts = posts.filter_by(author=current_user)
    posts = posts.paginate(
        request.args.get("page", 1, type=int),
        current_app.config['ITEMS_PER_PAGE'],
        True  # enable 404 error
    )

    next_page = None if not posts.has_next else \
        url_for("blog.drafts", page=posts.next_num)
    prev_page = None if not posts.has_prev else \
        url_for("blog.drafts", page=posts.prev_num)

    return render_template(
        "blog/drafts.html",
        title=_("Drafts of Articles"),
        posts=posts.items,
        next_page_url=next_page,
        prev_page_url=prev_page
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def add() -> object:
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.title = form.title.data
        post.text = form.text.data
        post.visible = form.visible.data
        post.author = current_user

        current_app.logger.info("User %s add new post %s", current_user, post)
        db.session.add(post)
        db.session.commit()

        flash(_("New post created!"))
        return redirect(url_for("blog.view", uri=post.uri))

    return render_template(
        "blog/add.html",
        title=_("Add Post"),
        form=form
    )


@bp.route("/edit/<uri>", methods=["GET", "POST"])
@login_required
def edit(uri: str) -> object:
    if not current_user.can(Permission.WRITE):
        return abort(403)
    post = Post.query.filter_by(uri=uri).first_or_404()
    # only posts authors and admins can edit posts
    if not current_user.is_admin and not post.author == current_user:
        return abort(403)
    form = PostForm()
    if form.validate_on_submit():
        current_app.logger.info("User %s edit post %s", current_user, post)
        post.title = form.title.data
        post.text = form.text.data
        post.visible = form.visible.data
        db.session.add(post)
        db.session.commit()
        flash(_("Changes were saved!"))
        return redirect(url_for("blog.view", uri=post.uri))
    elif request.method == "GET":
        form.title.data = post.title
        form.text.data = post.text
        form.visible.data = post.visible

    return render_template(
        "blog/edit.html",
        title=_("Edit Post"),
        post=post,
        form=form
    )


@bp.route("/delete/<uri>")
@login_required
def delete(uri: str) -> object:
    if not current_user.can(Permission.WRITE):
        return abort(403)
    post = Post.query.filter_by(uri=uri).first_or_404()
    # only posts authors and admins can delete posts
    if not current_user.is_admin and not post.author == current_user:
        return abort(403)
    current_app.logger.debug("User %s remove post %s", current_user, post)
    db.session.delete(post)
    db.session.commit()
    del post
    flash(_("Post was removed"))
    return redirect(url_for("blog.posts"))


@bp.route("/post/<uri>", methods=["GET", "POST"])
@login_required
def view(uri: str) -> object:
    post = Post.query.filter_by(uri=uri).first_or_404()
    # only visible posts can be viewed for non admins
    if not post.visible and (post.author != current_user and
                             not current_user.is_admin):
        return abort(404)
    comments = (post.comments
                .order_by(Comment.create_dt)
                .paginate(
                    request.args.get("page", 1, type=int),
                    current_app.config['ITEMS_PER_PAGE'],
                    True  # enable 404 error
                ))

    next_page = None if not comments.has_next else \
        url_for("blog.view", page=comments.next_num)
    prev_page = None if not comments.has_prev else \
        url_for("blog.view", page=comments.prev_num)

    form = None
    if current_user.can(Permission.COMMENT):
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment()
            current_app.logger.info("User %s add new comment: %s",
                                    current_user, comment)
            comment.text = form.text.data
            comment.post = post
            comment.author = current_user
            db.session.add(comment)
            db.session.commit()
            flash(_("New comment created!"))
            return redirect(url_for("blog.view", uri=post.uri))
    if post.author != current_user:
        post.watch_count += 1
        db.session.commit()

    return render_template(
        "blog/view.html",
        title=post.title,
        post=post,
        comments=comments.items,
        form=form
    )


@bp.route("/c/edit/<int:iid>", methods=["GET", "POST"])
@login_required
def edit_comment(iid: int) -> object:
    comment = Comment.query.filter_by(id=iid,
                                      author=current_user).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        current_app.logger.debug("User %s edit comment: %s",
                                 current_user, comment)
        comment.text = form.text.data
        db.session.add(comment)
        db.session.commit()
        flash(_("Comment saved!"))
        return redirect(url_for("blog.view", uri=comment.post.uri))
    elif request.method == "GET":
        form.text.data = comment.text

    return render_template(
        "blog/edit_comment.html",
        title=_("Edit Comment"),
        form=form
    )


@bp.route("/c/delete/<int:iid>")
@login_required
def delete_comment(iid: int) -> object:
    if not current_user.can(Permission.COMMENT):
        return abort(403)
    comment = Comment.query.get_or_404(iid)
    # only posts authors and admins can delete comments
    if not current_user.is_admin and not comment.author == current_user:
        return abort(403)
    current_app.logger.debug("User %s remove comment %s",
                             current_user, comment)
    comment.is_deleted = True
    db.session.add(comment)
    db.session.commit()
    flash(_("Comment was removed"))
    return redirect(request.args.get("next_page", url_for("blog.posts")))


@bp.route("/c/restore/<int:iid>")
@login_required
def restore_comment(iid: int) -> object:
    if not current_user.can(Permission.COMMENT):
        return abort(403)
    comment = Comment.query.get_or_404(iid)
    # only posts authors and admins can restore comments
    if not current_user.is_admin and not comment.author == current_user:
        return abort(403)
    current_app.logger.debug("User %s restore comment %s",
                             current_user, comment)
    comment.is_deleted = False
    db.session.add(comment)
    db.session.commit()
    flash(_("Comment was restored"))
    return redirect(request.args.get("next_page", url_for("blog.posts")))
