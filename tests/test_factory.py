from flaskr import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    response = client.get('/hello', follow_redirects=True)
    assert response.data == b'Hello, World!'

# the original code from the documentation on the site
# response = client.get('/hello')
# causes an error, so it was replaced by
# response = client.get('/hello', follow_redirects=True)