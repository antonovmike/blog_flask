import pytest

from flaskr.db import get_db
from flaskr.routers.blog import Post, validate_post


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': 'created', 'author_id': 1, 'tags': ['one', 'two']})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'id': 1, 'title': 'updated', 'body': 'updated', 'tags': ['one']})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path, title, body', (
    ('/create', 'Test Title', 'Test Body'),
    ('/1/update', 'Updated Title', 'Updated Body'),
))
def test_create_update_validate(client, auth, path, title, body):
    auth.login()
    response = client.post(path, data={'title': title, 'body': body, 'tags': ['one']})
    assert b'Title is required' not in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None


def test_unexisting_post(client, auth):
    # Save the original get_post function to restore it after the test
    original_get_post = Post.get_post

    # Override the get_post function
    def get_post(*args, **kwargs):
        return None

    try:
        # Assign the overridden function to the module
        Post.get_post = get_post

        auth.login()
        response = client.post('/1234/update')
        assert response.status_code == 400

        response = client.post('/1234/delete')
        assert response.status_code == 302
    finally:
        # Restore the original function after the test
        Post.get_post = original_get_post


def test_like(client, app):
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        client.post('/create', data={'title': 'test post', 'body': 'test body', 'tags': ['one']})

    response = client.post('/1/like')
    assert response.status_code == 200

    with app.app_context():
        post = get_db().execute(
            'SELECT p.id, title, body, created, author_id, username, '
            '(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, '
            '(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments '
            'FROM post p JOIN user u ON p.author_id = u.id '
            'WHERE p.id = ?',
            (1, )
        ).fetchone()
        assert post['likes'] == 1


def test_comment(client, app):
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        client.post('/create', data={'title': 'test post', 'body': 'test body', 'tags': ['one']})

    response = client.post('/1/comment', data={'body': 'test comment'})
    # Redirect to the post page
    assert response.status_code == 302

    with app.app_context():
        comments = get_db().execute(
            'SELECT c.id, body, created, author_id, username '
            'FROM comment c JOIN user u ON c.author_id = u.id '
            'WHERE post_id = ? '
            'ORDER BY created DESC',
            (1,)
        ).fetchall()
        assert len(comments) == 1
        assert comments[0]['body'] == 'test comment'


def test_search(client, auth):
    auth.login()
    response = client.post('/search', data={'query': "test"})
    assert response.status_code == 200
    assert b'test' in response.data


def test_search(client, auth):
    auth.login()
    response = client.post('/search', data={'query': 'test'})

    assert response.status_code == 200
    assert b'test' in response.data


def test_rss(client):
    response = client.get('/rss')

    assert response.status_code == 200
    assert response.content_type == 'application/rss+xml'
    assert b'<?xml version="1.0" encoding="UTF-8"?>' in response.data


def test_validate_post():
    assert validate_post("Title", "Body") is None
    assert validate_post("", "Body") == "Title is required"
    assert validate_post("Title", "") == "Body is required"
    assert validate_post("", "") == "Title is required"
