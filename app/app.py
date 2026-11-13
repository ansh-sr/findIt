import os
import uuid
import psycopg2
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

UPLOAD_FOLDER = "/app/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "lostfound_db"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgrespassword"),
        port=5432,
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            location VARCHAR(100) NOT NULL,
            contact VARCHAR(100) NOT NULL,
            image_filename VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS image_filename VARCHAR(255);")
    conn.commit()
    cur.close()
    conn.close()


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    cur = conn.cursor()

    if query:
        like_pattern = f"%{query}%"
        cur.execute(
            """
            SELECT title, category, location, contact, image_filename, created_at
            FROM items
            WHERE title ILIKE %s OR location ILIKE %s OR category ILIKE %s
            ORDER BY id DESC
            """,
            (like_pattern, like_pattern, like_pattern),
        )
    else:
        cur.execute(
            """
            SELECT title, category, location, contact, image_filename, created_at
            FROM items
            ORDER BY id DESC
            """
        )

    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", items=items, query=query)


@app.route("/post", methods=["GET", "POST"])
def post_item():
    if request.method == "POST":
        title = request.form["title"].strip()
        category = request.form["category"]
        location = request.form["location"].strip()
        contact = request.form["contact"].strip()

        image_filename = None
        file = request.files.get("image")
        if file and file.filename and allowed_file(file.filename):
            ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
            image_filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO items (title, category, location, contact, image_filename)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title, category, location, contact, image_filename),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    return render_template("post.html")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)