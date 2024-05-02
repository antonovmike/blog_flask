import os

from datetime import datetime
from flask import Blueprint, flash, g, make_response, redirect, render_template, request, url_for
from flaskr.routers.auth import login_required
from flaskr.db import get_db
from werkzeug.utils import secure_filename

from ..post import Post
from ..log import init_logger


logger = init_logger()

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 5
    posts = Post.get_posts(page, per_page)

    logger.debug(f'Page number: {page}')

    return render_template(
        "blog/index.html", posts=posts, current_page=page, per_page=per_page
    )


@bp.route("/<int:id>")
def post(id):
    post = Post.get_post(id)
    logger.debug(f'Post opened: {post}')
    return render_template("blog/post.html", post=post)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        tags = request.form.getlist("tags")

        error = validate_post(title, body)

        if error is not None:
            flash(error)
        else:
            post_id = Post.create(title, body, g.user["id"], tags)
            if "image" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["image"]
            if file.filename == "":
                pass
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join("flaskr/static/images", filename))

                logger.debug(f'Image file saved: {filename}')

                db = get_db()
                db.execute(
                    "INSERT INTO image (post_id, image_path) VALUES (?, ?)",
                    (post_id, "/static/images/" + filename),
                )
                db.commit()

                logger.debug(f'Post saved into database: {db}')

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = Post.get_post(id, check_author=True)

    logger.debug(f'Update post: {post}')

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        tags = request.form.get("tags")

        error = validate_post(title, body)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            Post.update(id, title, body, tags)

            tags_id = []
            for tag in tags:
                tag_id = db.execute(
                    "SELECT id FROM tags WHERE name_tag = ?", (tag,)
                ).fetchone()
                if tag_id is not None:
                    tags_id.append(tag_id[0])
                else:
                    db.execute("INSERT INTO tags (name_tag) VALUES (?)", (tag,))
                    tags_id.append(
                        db.execute("SELECT last_insert_rowid()").fetchone()[0]
                    )

            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("GET", "POST"))
@login_required
def delete(id):
    Post.get_post(id, check_author=True)
    Post.delete(id)
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/like", methods=("POST",))
@login_required
def like(id):
    db = get_db()
    existing_like = db.execute(
        "SELECT * FROM post_like WHERE user_id = ? AND post_id = ?", (g.user["id"], id)
    ).fetchone()

    if existing_like is not None:
        db.execute(
            "DELETE FROM post_like WHERE user_id = ? AND post_id = ?",
            (g.user["id"], id),
        )
    else:
        db.execute(
            "INSERT INTO post_like(user_id, post_id, liked) VALUES(?, ?, TRUE)",
            (g.user["id"], id),
        )

    db.commit()
    post = Post.get_post(id)
    post = dict(post)
    post["likes"] = db.execute(
        "SELECT COUNT(*) FROM post_like WHERE post_id = ? AND liked = TRUE", (id,)
    ).fetchone()[0]
    return render_template("blog/post.html", post=post)


@bp.route("/<int:id>/comment", methods=("POST",))
@login_required
def comment(id):
    body = request.form["body"]
    error = None

    if not body:
        error = "Body is required"

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            "INSERT INTO comment (body, created, author_id, post_id)"
            " VALUES (?, ?, ?, ?)",
            (body, datetime.now(), g.user["id"], id),
        )
        db.commit()
        return redirect(url_for("blog.post", id=id))


@bp.route("/tag/<string:tag>")
def tag(tag):
    db = get_db()
    posts_data = db.execute(
        "SELECT p.id, title, body, created, author_id, username, "
        "(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, "
        "(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments, "
        "(SELECT image_path FROM image WHERE post_id = p.id LIMIT 1) AS image, "
        "(SELECT avatar_path FROM user WHERE id = p.author_id) AS avatar "
        "FROM post p JOIN user u ON p.author_id = u.id "
        "JOIN post_tag pt ON p.id = pt.post_id "
        "JOIN tags t ON pt.tags_id = t.id "
        "WHERE t.name_tag = ? "
        "ORDER BY created DESC",
        (tag,),
    ).fetchall()

    return render_template(
        "blog/tag.html",
        posts=[Post(*post_data) for post_data in posts_data],
        tag=tag, 
    )


@bp.route("/search", methods=("POST",))
def search():
    query = request.form["query"]
    db = get_db()
    posts_data = db.execute(
        "SELECT p.id, title, body, created, author_id, username, "
        "(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, "
        "(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments, "
        "(SELECT COUNT(*) FROM image WHERE post_id = p.id) AS image, "
        "(SELECT avatar_path FROM user WHERE id = p.author_id) AS avatar "
        "FROM post p JOIN user u ON p.author_id = u.id "
        "WHERE title LIKE ?",
        ("%" + query + "%",),
    ).fetchall()

    return render_template(
        "blog/search.html",
        posts=[Post(*post_data) for post_data in posts_data],
        query=query,
    )


@bp.route('/rss')
def rss():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, p.title, p.body, p.created, u.username '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'ORDER BY p.created DESC'
    ).fetchall()
    xml = render_template('rss.xml', posts=posts)
    response = make_response(xml)
    response.headers['Content-Type'] = 'application/rss+xml'
    return response


def validate_post(title, body):
    error = None
    if not title:
        error = "Title is required"
    elif not body:
        error = "Body is required"
    return error
