import os
from datetime import datetime

from web_client import BASE_DIR, create_app, db
from web_client.models import BlogPost

app = create_app()
POSTS_LIST_PATH = os.path.join(BASE_DIR, "templates", "blog", "pages.list")


if __name__ == "__main__":
    with app.app_context():
        with open(POSTS_LIST_PATH, 'r') as fin:
            # [bug] TODO: add context usage
            for line in fin:
                date, title = line.split()
                date = datetime.strptime(date, "%Y%m%d-%H%M%S")
                title = " ".join([t.capitalize() for t in title.split("-")])
                post = BlogPost(title=title, timestamp=date)
                post._link = post.link
                db.session.add(post)
        db.session.commit()
