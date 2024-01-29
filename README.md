# Blog Flask

This project is a blog application using Python, SQLite and Flask. The application allows users to register, log in, create posts, edit and delete them, and view other users' profiles. The project covers topics such as templates, forms, databases, authentication, blueprints, and deployment. 

![text chat](https://github.com/antonovmike/blog_flask/blob/main/screenshots/blog_post.png)


## Table of Contents
- [Requirements](https://github.com/antonovmike/blog_flask#requirements)
- [Installation](https://github.com/antonovmike/blog_flask#installation)
- [Run](https://github.com/antonovmike/blog_flask#run)
- [Tests](https://github.com/antonovmike/blog_flask#tests)
- [Secret Key](https://github.com/antonovmike/blog_flask#secret-key)
- [Flask tutorial](https://github.com/antonovmike/blog_flask#flask-tutorial)
- [License](https://github.com/antonovmike/blog_flask#license)

## [Requirements](https://github.com/antonovmike/blog_flask#table-of-contents)
To run this project, you need to have the following:
- Python 3.6 or higher
- pip, a tool for installing Python packages
- virtualenv, a tool for creating isolated Python environments (optional, but recommended)

## [Installation](https://github.com/antonovmike/blog_flask#table-of-contents)
To install this project, follow these steps:

Clone the project from GitHub using the command `git clone https://github.com/antonovmike/blog_flask.git`. Go to the project folder using the command `cd blog_flask`. Create a virtual environment using the command `python3 -m venv venv` (optional, but recommended). Activate the virtual environment using the command `source venv/bin/activate` on Linux or `venv\Scripts\activate` on Windows (optional, but recommended). Install the required packages using the command 
```bash
pip install -r requirements.txt
```
This command is only used to make the project [installable](https://flask.palletsprojects.com/en/2.1.x/tutorial/install/#install-the-project) and is not needed after that:
```bash
pip install -e .
```

## [Run](https://github.com/antonovmike/blog_flask#table-of-contents)
To run the projsect use command
```bash
flask --app flaskr run --debug
```
On first run, this command will create a database file `flaskr.sqlite` and start the server. Or you can use special command to init DB:
```bash
flask --app flaskr init-db
```

## [Tests](https://github.com/antonovmike/blog_flask#table-of-contents)
To test this project, follow these steps: 
Activate the virtual environment using the command `source venv/bin/activate` on Linux or `venv\Scripts\activate` on Windows (optional, but recommended). Run the tests using one of these commands:
```bash
pytest
```
```bash
pytest -v
```
```bash
coverage run -m pytest
```
You can also test individual modules by specifying the path to the required module. For example: 
```bash
pytest tests/test_auth.py 
```
Check the test coverage using the command coverage report.

## [Secret Key](https://github.com/antonovmike/blog_flask#table-of-contents)
The secret key is a random string that is used to secure the application data, such as cookies and tokens. It is needed to keep the client-side sessions secure and to prevent data tampering. The secret key should only be known to the application and should be kept relatively constant during the application's life cycle, including through application restarts. 
Configure the Secret Key. You can refer to the official manual to create your own key: [Configure the Secret Key](https://flask.palletsprojects.com/en/2.3.x/tutorial/deploy/#configure-the-secret-key).

## [Flask tutorial](https://github.com/antonovmike/blog_flask#table-of-contents)
This project was done under formal documentation along with additional exercises "[Keep Developing!](https://flask.palletsprojects.com/en/3.0.x/tutorial/next/)":

- ✅ A detail view to show a single post. Click a post’s title to go to its page.
- ✅ Like / unlike a post.
- ✅ Comments.
- ✅ Tags. Clicking a tag shows all the posts with that tag.
- ✅ A search box that filters the index page by name.
- ✅ Paged display. Only show 5 posts per page.
- ✅ Upload an image to go along with a post.
- ✅ Format posts using Markdown.
- ✅ An RSS feed of new posts.

## [License](https://github.com/antonovmike/blog_flask#table-of-contents)
This project is licensed under the MIT License. See the LICENSE https://www.freecodecamp.org/news/how-to-write-a-good-readme-file/ file for details.
