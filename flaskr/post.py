from flask import g
from flaskr.db import get_db
from werkzeug.exceptions import abort

from .markdown import md


class Post:
    def __init__(
        self, id, title, body, created, author_id, username, likes, comments, image, avatar
    ):
        self.id = id
        self.title = title
        self.body = body
        self.created = created
        self.author_id = author_id
        self.username = username
        self.likes = likes
        self.comments = comments
        self.image = image
        self.avatar = avatar

    @property
    def tags(self):
        db = get_db()
        tags_data = db.execute(
            "SELECT t.name_tag FROM post_tag pt JOIN "
            "tags t ON pt.tags_id = t.id WHERE pt.post_id = ?",
            (self.id,),
        ).fetchall()

        return [tag[0] for tag in tags_data]

    def get_posts(page, per_page):
        db = get_db()
        offset = (page - 1) * per_page
        posts_data = db.execute(
            "SELECT p.id, title, body, created, author_id, username, "
            "(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, "
            "(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments, "
            "(SELECT COUNT(*) FROM image WHERE post_id = p.id) AS image, "
            "(SELECT avatar_path FROM user WHERE id = p.author_id) AS avatar "
            "FROM post p JOIN user u ON p.author_id = u.id "
            "ORDER BY created DESC LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()

        return [Post(*post_data) for post_data in posts_data]

    @staticmethod
    def get_post(id, check_author=False):
        post = (
            get_db()
            .execute(
                "SELECT p.id, title, body, created, author_id, username, "
                "(SELECT COUNT(*) FROM post_like WHERE post_id = p.id AND liked = TRUE) AS likes, "
                "(SELECT COUNT(*) FROM comment WHERE post_id = p.id) AS comments, "
                "(SELECT image_path FROM image WHERE post_id = p.id LIMIT 1) AS image "
                "FROM post p JOIN user u ON p.author_id = u.id "
                "WHERE p.id = ?",
                (id,),
            )
            .fetchone()
        )

        if post is None:
            abort(404, f"Post id {id} doesn't exist.")

        if check_author and post["author_id"] != g.user["id"]:
            abort(403)

        avatar = (
            get_db()
            .execute(
                "SELECT avatar_path FROM user WHERE id = ?",
                (post["author_id"],),
            )
            .fetchone()
        )

        comments = (
            get_db()
            .execute(
                "SELECT c.id, body, created, author_id, username "
                "FROM comment c JOIN user u ON c.author_id = u.id "
                "WHERE post_id = ? "
                "ORDER BY created DESC",
                (id,),
            )
            .fetchall()
        )
        post_obj = Post(*post, avatar=avatar[0])

        return dict(
            post=post_obj, comments=comments, tags=post_obj.tags, image=post_obj.image, avatar=avatar[0]
        )

    @property
    def body_html(self):
        return md.convert(self.body)

    @classmethod
    def create(cls, title, body, author_id, tags):
        splitted = [x.strip() for x in tags[0].split(",")]
        db = get_db()
        db.execute(
            "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
            (title, body, author_id),
        )
        db.commit()

        post_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        for tag in splitted:
            tag_info = db.execute(
                "SELECT id FROM tags WHERE name_tag = ?", (tag,)
            ).fetchone()
            if tag_info is None:
                db.execute("INSERT INTO tags (name_tag) VALUES (?)", (tag,))
                tags_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            else:
                tags_id = tag_info[0]
            db.execute(
                "INSERT INTO post_tag (post_id, tags_id) VALUES (?, ?)",
                (post_id, tags_id),
            )

        db.commit()

        return post_id

    @classmethod
    def update(cls, id, title, body, tags):
        db = get_db()
        db.execute(
            "UPDATE post SET title = ?, body = ?" " WHERE id = ?", (title, body, id)
        )
        db.commit()

        db.execute("DELETE FROM post_tag WHERE post_id = ?", (id,))

        tags = tags.split(",")

        for tag in tags:
            tag = tag.strip()
            tags_id = db.execute(
                "SELECT id FROM tags WHERE name_tag = ?", (tag,)
            ).fetchone()
            if tags_id is None:
                db.execute("INSERT INTO tags (name_tag) VALUES (?)", (tag,))
                tags_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                db.execute(
                    "INSERT INTO post_tag (post_id, tags_id) VALUES (?, ?)",
                    (id, tags_id),
                )
            else:
                db.execute(
                    "INSERT INTO post_tag (post_id, tags_id) VALUES (?, ?)",
                    (id, tags_id[0]),
                )

        db.commit()

    @classmethod
    def delete(cls, id):
        db = get_db()
        db.execute("DELETE FROM post WHERE id = ?", (id,))
        db.commit()
