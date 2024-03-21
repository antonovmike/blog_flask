from datetime import datetime

from flaskr.db import get_db
from flaskr.post import Post


def test_post_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'test', 'body': 'test', 'author_id': 1, 'tags': ['one', 'two']})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_get_posts(auth, app):
    auth.login()
    with app.app_context():
        posts = Post.get_posts(1, 5)
        assert len(posts) <= 5


def test_post_body_html(auth, app):
    auth.login()
    with app.app_context():
        post = Post(1, 'test', 'test', datetime.now(), 1, 'testuser', 0, 0, None, None)
        assert '<p>test</p>' in post.body_html


def test_post_tags(auth, app):
    auth.login()
    with app.app_context():
        post = Post(1, 'test', 'test', datetime.now(), 1, 'testuser', 0, 0, None, None)
        assert post.tags == []
