import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

def connect_db(database=None):
    config = {
        'host':     os.environ.get('MYSQL_HOST'),
        'user':     os.environ.get('MYSQL_USER'),
        'password': os.environ.get('MYSQL_PASSWORD'),
        'port':     int(os.environ.get('MYSQL_PORT')),
    }
    if database:
        config['database'] = database
    return mysql.connector.connect(**config)

def create_database():
    db = connect_db()
    cursor = db.cursor()
    dbname = os.environ.get('MYSQL_DATABASE', 'project_needy')
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")
    cursor.close()
    db.close()

def get_dbname():
    return os.environ.get('MYSQL_DATABASE', 'project_needy')

def create_tables():
    db = connect_db(get_dbname())
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_blocks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            note_id INT NOT NULL,
            headline VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            position INT DEFAULT 0,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlists (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            note_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_note (user_id, note_id)
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS folders (
        id         INT AUTO_INCREMENT PRIMARY KEY,
        user_id    INT NOT NULL,
        name       VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_folders (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            note_id   INT NOT NULL,
            folder_id INT NOT NULL,
            UNIQUE KEY unique_note_folder (note_id, folder_id),
            FOREIGN KEY (note_id)   REFERENCES notes(id)   ON DELETE CASCADE,
            FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
        )
    """)
    db.commit()
    cursor.close()
    db.close()

def get_user_by_id(user_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    except Exception:
        return None
    finally:
        if cursor: cursor.close()
        if db: db.close()

def store_notes(user_id, title, blocks):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute("INSERT INTO notes (user_id, title) VALUES (%s, %s)", (user_id, title))
        note_id = cursor.lastrowid
        for index, block in enumerate(blocks):
            cursor.execute("""
                INSERT INTO note_blocks (note_id, headline, description, position)
                VALUES (%s, %s, %s, %s)
            """, (note_id, block["headline"], block["description"], index))
        db.commit()
        return {"status": "success", "code": 200, "message": "Note saved successfully", "note_id": note_id}
    except Exception as err:
        return {"status": "error", "code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()

def get_notes(user_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, title, created_at FROM notes WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        notes = cursor.fetchall()
       # inside get_notes, after fetching blocks:
        for note in notes:
            cur2 = db.cursor(dictionary=True)
            cur2.execute("SELECT id, headline, description FROM note_blocks WHERE note_id = %s ORDER BY position ASC", (note["id"],))
            note["blocks"] = cur2.fetchall()
            cur2.close()
            if note.get("created_at"):
                note["created_at"] = str(note["created_at"])
        return {"code": 200, "notes": notes}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()

def get_public_notes():
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT notes.id, notes.title, notes.created_at, users.name AS author
            FROM notes
            JOIN users ON notes.user_id = users.id
            ORDER BY notes.created_at DESC
        """)
        notes = cursor.fetchall()
        for note in notes:
            cur2 = db.cursor(dictionary=True)
            cur2.execute("SELECT headline, description FROM note_blocks WHERE note_id = %s ORDER BY position ASC", (note["id"],))
            note["blocks"] = cur2.fetchall()
            cur2.close()
            if note.get("created_at"):
                note["created_at"] = str(note["created_at"])
        return {"code": 200, "notes": notes}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()
def add_wishlist_entry(user_id, note_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute(
            "SELECT id FROM wishlists WHERE user_id = %s AND note_id = %s",
            (user_id, note_id)
        )
        if cursor.fetchone():
            return {"code": 409, "message": "Already in wishlist"}
        cursor.execute(
            "INSERT INTO wishlists (user_id, note_id) VALUES (%s, %s)",
            (user_id, note_id)
        )
        db.commit()
        return {"code": 200, "action": "saved"}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()


def remove_wishlist_entry(user_id, note_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM wishlists WHERE user_id = %s AND note_id = %s",
            (user_id, note_id)
        )
        db.commit()
        return {"code": 200, "action": "removed"}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()
def get_wishlist(user_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT notes.id, notes.title, notes.created_at, users.name AS author
            FROM wishlists
            JOIN notes ON wishlists.note_id = notes.id
            JOIN users ON notes.user_id = users.id
            WHERE wishlists.user_id = %s
            ORDER BY wishlists.id DESC
        """, (user_id,))
        notes = cursor.fetchall()
        for note in notes:
            cur2 = db.cursor(dictionary=True)
            cur2.execute(
                "SELECT headline, description FROM note_blocks WHERE note_id = %s ORDER BY position ASC",
                (note["id"],)
            )
            note["blocks"] = cur2.fetchall()
            cur2.close()
            if note.get("created_at"):
                note["created_at"] = str(note["created_at"])
        return {"code": 200, "notes": notes}
    except Exception as err:
        print("get_wishlist error:", err)
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()

def delete_note(note_id, user_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute("DELETE FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
        db.commit()
        if cursor.rowcount == 0:
            return {"code": 403, "message": "Not allowed or note not found"}
        return {"code": 200, "message": "Note deleted"}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()

def edit_note(note_id, user_id, title, blocks):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute("SELECT id FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
        if not cursor.fetchone():
            return {"code": 403, "message": "Not allowed or note not found"}
        cursor.execute("UPDATE notes SET title = %s WHERE id = %s", (title, note_id))
        cursor.execute("DELETE FROM note_blocks WHERE note_id = %s", (note_id,))
        for i, block in enumerate(blocks):
            cursor.execute("""
                INSERT INTO note_blocks (note_id, headline, description, position)
                VALUES (%s, %s, %s, %s)
            """, (note_id, block["headline"], block["description"], i))
        db.commit()
        return {"code": 200, "message": "Note updated"}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()

def register_user(name, email, password):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return {"status": "error", "code": 409, "message": "User already exists"}
        hashed = generate_password_hash(password)
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed))
        db.commit()
        return {"status": "success", "code": 201, "message": "User registered successfully"}
    except Exception as err:
        return {"status": "error", "code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()

def login_user(email, password):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user or not check_password_hash(user["password"], password):
            return {"status": "error", "code": 401, "message": "Invalid email or password"}
        return {"status": "success", "code": 200, "message": "Login successful", "user": {"id": user["id"], "name": user["name"]}}
    except Exception as err:
        return {"status": "error", "code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()


def create_folder(user_id, name):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO folders (user_id, name) VALUES (%s, %s)",
            (user_id, name)
        )
        db.commit()
        return {"code": 200, "folder_id": cursor.lastrowid}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()


def delete_folder(folder_id, user_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id)
        )
        db.commit()
        if cursor.rowcount == 0:
            return {"code": 403, "message": "Not allowed"}
        return {"code": 200}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()


def add_note_to_folder(note_id, folder_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute(
            "SELECT id FROM note_folders WHERE note_id = %s AND folder_id = %s",
            (note_id, folder_id)
        )
        if cursor.fetchone():
            return {"code": 409, "message": "Already in folder"}
        cursor.execute(
            "INSERT INTO note_folders (note_id, folder_id) VALUES (%s, %s)",
            (note_id, folder_id)
        )
        db.commit()
        return {"code": 200}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()


def remove_note_from_folder(note_id, folder_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM note_folders WHERE note_id = %s AND folder_id = %s",
            (note_id, folder_id)
        )
        db.commit()
        return {"code": 200}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()


def get_folders(user_id):
    db = None
    cursor = None
    try:
        db = connect_db(get_dbname())
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, created_at FROM folders WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        folders = cursor.fetchall()
        for folder in folders:
            if folder.get("created_at"):
                folder["created_at"] = str(folder["created_at"])
            cur2 = db.cursor(dictionary=True)
            cur2.execute("""
                SELECT notes.id, notes.title
                FROM note_folders
                JOIN notes ON note_folders.note_id = notes.id
                WHERE note_folders.folder_id = %s
            """, (folder["id"],))
            folder["notes"] = cur2.fetchall()
            cur2.close()
        return {"code": 200, "folders": folders}
    except Exception as err:
        return {"code": 500, "message": str(err)}
    finally:
        if cursor: cursor.close()
        if db: db.close()

def setup_db():
    create_database()
    create_tables()
