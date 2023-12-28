from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from datetime import datetime
from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('blog', __name__)


class Post:
    def __init__(self, id, title, body, created, author_id, username, likes, comments):
        self.id = id
        self.title = title
        self.body = body
        self.created = created
        self.author_id = author_id
        self.username = username
        self.likes = likes
        self.comments = comments

    @property
    def tags(self):
        db = get_db()
        tags_data = db.execute(
            'SELECT t.name_tag FROM post_tag pt JOIN'
            ' tags t ON pt.tags_id = t.id WHERE pt.post_id = ?',
            (self.id,)
        ).fetchall()

        return [tag[0] for tag in tags_data]
    
    def check_tags(self):
        if self.tags:
            print("SOME TAGS")
        else:
            print("NO TAGS")

    @staticmethod
    def get_posts():
        db = get_db()
        posts_data = db.execute(
            'SELECT p.id, title, body, created, author_id, username, '
            '(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, '
            '(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments '
            'FROM post p JOIN user u ON p.author_id = u.id '
            'ORDER BY created DESC'
        ).fetchall()

        return [Post(*post_data) for post_data in posts_data]

    @staticmethod
    def get_post(id, check_author=False):
        post = get_db().execute(
            'SELECT p.id, title, body, created, author_id, username, '
            '(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, '
            '(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments '
            'FROM post p JOIN user u ON p.author_id = u.id '
            'WHERE p.id = ?',
            (id, )
        ).fetchone()

        if post is None:
            abort(404, f"Post id {id} doesn't exist.")

        if check_author and post['author_id'] != g.user['id']:
            abort(403)

        comments = get_db().execute(
            'SELECT c.id, body, created, author_id, username '
            'FROM comment c JOIN user u ON c.author_id = u.id '
            'WHERE post_id = ? '
            'ORDER BY created DESC',
            (id,)
        ).fetchall()
        post_obj = Post(*post)
        return dict(post=post_obj, comments=comments, tags=post_obj.tags)

    @classmethod
    def create(cls, title, body, author_id, tags):
        splitted = [x.strip() for x in tags[0].split(',')]
        db = get_db()
        db.execute(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (?, ?, ?)',
            (title, body, author_id)
        )
        db.commit()

        post_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        created = datetime.now()
        username = db.execute(
            'SELECT username FROM user WHERE id = ?',
            (author_id,)
        ).fetchone()[0]
        likes = db.execute(
            'SELECT COUNT(*) FROM post_like WHERE post_id = ?',
            (post_id,)
        ).fetchone()[0]
        comments = db.execute(
            'SELECT COUNT(*) FROM comment WHERE post_id = ?',
            (post_id,)
        ).fetchone()[0]
        post = Post(post_id, title, body, created, author_id, username, likes, comments)
        post.check_tags()

        for tag in splitted:
            tag_info = db.execute('SELECT id FROM tags WHERE name_tag = ?', (tag,)).fetchone()
            if tag_info is None:
                db.execute('INSERT INTO tags (name_tag) VALUES (?)', (tag,))
                tags_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            else:
                tags_id = tag_info[0]
            db.execute('INSERT INTO post_tag (post_id, tags_id) VALUES (?, ?)', (post_id, tags_id))

        db.commit()

    @classmethod
    def update(cls, id, title, body, tags):
        db = get_db()
        db.execute(
            'UPDATE post SET title = ?, body = ?'
            ' WHERE id = ?',
            (title, body, id)
        )
        db.commit()

        db.execute('DELETE FROM post_tag WHERE post_id = ?', (id,))

        tags = tags.split(',')

        for tag in tags:
            tag = tag.strip()
            tags_id = db.execute('SELECT id FROM tags WHERE name_tag = ?', (tag,)).fetchone()
            if tags_id is None:
                db.execute('INSERT INTO tags (name_tag) VALUES (?)', (tag,))
                tags_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
                db.execute('INSERT INTO post_tag (post_id, tags_id) VALUES (?, ?)', (id, tags_id))
            else:
                db.execute('INSERT INTO post_tag (post_id, tags_id) VALUES (?, ?)', (id, tags_id[0]))

        db.commit()

    @classmethod
    def delete(cls, id):
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()


@bp.route('/')
def index():
    posts = Post.get_posts()
    return render_template('blog/index.html', posts=posts)


@bp.route('/<int:id>')
def post(id):
    post = Post.get_post(id)
    return render_template('blog/post.html', post=post)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags = request.form.getlist('tags')

        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            Post.create(title, body, g.user['id'], tags)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = Post.get_post(id, check_author=True)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags = request.form.get('tags')

        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            Post.update(id, title, body, tags)

            tags_id = []
            for tag in tags:
                tag_id = db.execute('SELECT id FROM tags WHERE name_tag = ?', (tag,)).fetchone()
                if tag_id is not None:
                    tags_id.append(tag_id[0])
                else:
                    db.execute('INSERT INTO tags (name_tag) VALUES (?)', (tag,))
                    tags_id.append(db.execute('SELECT last_insert_rowid()').fetchone()[0])

            # Tag.add_tags(id, tags)
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    Post.get_post(id, check_author=True)
    Post.delete(id)
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/like', methods=('POST',))
@login_required
def like(id):
    db = get_db()
    existing_like = db.execute(
        'SELECT * FROM post_like WHERE user_id = ? AND post_id = ?',
        (g.user['id'], id)
    ).fetchone()

    if existing_like is not None:
        db.execute(
            'DELETE FROM post_like WHERE user_id = ? AND post_id = ?',
            (g.user['id'], id)
        )
    else:
        db.execute(
            'INSERT INTO post_like(user_id, post_id, liked) VALUES(?, ?, TRUE)',
            (g.user['id'], id)
        )

    db.commit()
    post = Post.get_post(id)
    post = dict(post)
    post['likes'] = db.execute('SELECT COUNT(*) FROM post_like WHERE post_id = ? AND liked = TRUE', (id,)).fetchone()[0]
    return render_template('blog/post.html', post=post)


@bp.route('/<int:id>/comment', methods=('POST',))
@login_required
def comment(id):
    body = request.form['body']
    error = None

    if not body:
        error = 'Body is required'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO comment (body, created, author_id, post_id)'
            ' VALUES (?, ?, ?, ?)',
            (body, datetime.now(), g.user['id'], id)
        )
        db.commit()
        return redirect(url_for('blog.post', id=id))


@bp.route('/tag/<string:tag>')
def tag(tag):
    db = get_db()
    posts_data = db.execute(
        'SELECT p.id, title, body, created, author_id, username, '
        '(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, '
        '(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'JOIN post_tag pt ON p.id = pt.post_id '
        'JOIN tags t ON pt.tags_id = t.id '
        'WHERE t.name_tag = ? '
        'ORDER BY created DESC',
        (tag,)
    ).fetchall()

    return render_template('blog/tag.html', posts=[Post(*post_data) for post_data in posts_data], tag=tag)


@bp.route('/search', methods=('POST',))
def search():
    query = request.form['query']
    db = get_db()
    posts_data = db.execute(
        'SELECT p.id, title, body, created, author_id, username, '
        '(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, '
        '(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'WHERE title LIKE ?',
        ('%' + query + '%',)
    ).fetchall()
    return render_template('blog/search.html', posts=[Post(*post_data) for post_data in posts_data], query=query)


class Tag:
    def __init__(self):
        pass

    @classmethod
    def add_tags(cls, post_id, tags_id):
        db = get_db()
        if isinstance(tags, str):
            tags = tags.split(', ')
        for tag in tags:
            tags_id = db.execute('SELECT id FROM tags WHERE name_tag = ?', (tag,)).fetchone()
            if tags_id is None:
                db.execute('INSERT INTO tags (name_tag) VALUES (?)', (tag,))
                tags_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            post_tag_exists = db.execute('SELECT * FROM post_tag WHERE post_id = ? AND tags_id = ?', (post_id, tags_id)).fetchone()
            if post_tag_exists is None:
                db.execute('INSERT INTO post_tag (post_id, tags_id) VALUES (?, ?)', (post_id, tags_id))
        db.commit()
