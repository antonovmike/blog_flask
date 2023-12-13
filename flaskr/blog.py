from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, '
        '(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/<int:id>')
def post(id):
    post = get_post(id)
    return render_template('blog/post.html', post=post)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, '
        '(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'WHERE p.id = ?',
        (id, )
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/like', methods=('POST',))
@login_required
def like(id):
    db = get_db()
    existing_like = db.execute(
        'SELECT * FROM post_like WHERE user_id = ? AND post_id = ?',
        (g.user['id'], id)
    ).fetchone()

    # Likes should be unique
    if existing_like is not None:
        return redirect(url_for('blog.post', id=id))
    db.execute(
        'INSERT INTO post_like (user_id, post_id, liked) VALUES (?, ?, TRUE)',
        (g.user['id'], id)
    )

    db.commit()
    post = get_post(id)
    post = dict(post)
    post['likes'] = db.execute('SELECT COUNT(*) FROM post_like WHERE post_id = ? AND liked = TRUE', (id,)).fetchone()[0]
    return render_template('blog/post.html', post=post)


@bp.route('/<int:id>/unlike', methods=('POST',))
@login_required
def unlike(id):
    db = get_db()
    db.execute(
        'DELETE FROM post_like WHERE user_id = ? AND post_id = ?',
        (g.user['id'], id)
    )
    db.commit()
    post = get_post(id)
    post = dict(post)
    post['likes'] = db.execute('SELECT COUNT(*) FROM post_like WHERE post_id = ? AND liked = TRUE', (id,)).fetchone()[0]
    return render_template('blog/post.html', post=post)
