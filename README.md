# Blog Flask

This project is a blog application using Python, SQLite and Flask. The application allows users to register, log in, create posts, edit and delete them, and view other users' profiles. The project covers topics such as templates, forms, databases, authentication, blueprints, and deployment. 

![text chat](https://github.com/antonovmike/blog_flask/blob/main/screenshots/blog_post.png)


## Table of Contents
- Requirements
- Installation
- Run

## Requirements
To run this project, you need to have the following:
- Python 3.6 or higher
- pip, a tool for installing Python packages
- virtualenv, a tool for creating isolated Python environments (optional, but recommended)

## Installation
To install this project, follow these steps:

Clone the project from GitHub using the command `git clone https://github.com/antonovmike/blog_flask.git`. Go to the project folder using the command `cd blog_flask`. Create a virtual environment using the command `python3 -m venv venv` (optional, but recommended). Activate the virtual environment using the command `source venv/bin/activate` on Linux or `venv\Scripts\activate` on Windows (optional, but recommended). Install the required packages using the command `pip install -r requirements.txt`.

## Run
To run the projsect use command
```bash
flask --app flaskr run --debug
```
On first run, this command will create a database file `flaskr.sqlite` and start the server.

Init DB (or reset DB):
```bash
flask --app flaskr init-db
```
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
- ✅ Like / unlike a post.
- ✅ Comments.
- ✅ Tags. Clicking a tag shows all the posts with that tag.
- ✅ A search box that filters the index page by name.
- ✅ Paged display. Only show 5 posts per page.
- ✅ Upload an image to go along with a post.
- ✅ Format posts using Markdown.
- ✅ An RSS feed of new posts.
