https://flask.palletsprojects.com/

Libraries:
```bash
pip install pytest coverage
```
Run:
```bash
flask --app flaskr run --debug
```
```bash
flask --app flaskr init-db
```
Install the Project:
```bash
pip install -e .
```
Test:
```bash
pytest
```
```bash
pytest -v
```
```bash
coverage run -m pytest
```

[Configure the Secret Key](https://flask.palletsprojects.com/en/2.3.x/tutorial/deploy/#configure-the-secret-key)
Swap SECRET_KEY='dev' with some random bytes

[Keep Developing!](https://flask.palletsprojects.com/en/3.0.x/tutorial/next/):

- ✅ A detail view to show a single post. Click a post’s title to go to its page.
- ➡️ Like / unlike a post.
- Comments.
- Tags. Clicking a tag shows all the posts with that tag.
- A search box that filters the index page by name.
- Paged display. Only show 5 posts per page.
- Upload an image to go along with a post.
- Format posts using Markdown.
- An RSS feed of new posts.
