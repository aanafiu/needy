import os
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from db import add_note_to_folder, create_folder, delete_folder, get_folders, get_user_by_id, get_wishlist, remove_note_from_folder, remove_wishlist_entry, setup_db, register_user, login_user, store_notes, get_notes, get_public_notes, delete_note, edit_note, add_wishlist_entry
from helper import login_required
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("DB_SECRET_KEY", "fallback-dev-key-change-me")

setup_db()

@app.route('/')
def index():
    return render_template('public_notes.html')

@app.route('/notes')
@login_required
def notes():
    return render_template('notes.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect("/login")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        result = login_user(email, password)
        if result["code"] == 401 or result["code"] == 500:
            flash(result["message"], "danger")
        else:
            flash(result["message"], "success")
            session["user_id"] = result["user"]["id"]
            return redirect("/")
        return redirect("/login")
    else:
        return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        result = register_user(name, email, password)
        if result["code"] == 409 or result["code"] == 500:
            flash(result["message"], "danger")
        else:
            flash(result["message"], "success")
            return redirect("/")
        return redirect("/register")
    else:
        return render_template('register.html')

@app.route('/public-notes')
def public_notes_page():
    return render_template('public_notes.html')

@app.route('/get-public-notes', methods=["GET", "POST"])
def fetch_public_notes():
    result = get_public_notes()
    if result["code"] == 200:
        return jsonify({"success": True, "notes": result["notes"]})
    return jsonify({"success": False, "message": result["message"]})

@app.route('/profile')
@login_required
def profile():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id)
    notes_data = get_notes(user_id)
    notes = notes_data["notes"] if notes_data["code"] == 200 else []
    return render_template('profile.html', user=user, notes=notes)

@app.route('/delete-note/<int:note_id>')
@login_required
def remove_note(note_id):
    user_id = session.get("user_id")
    result = delete_note(note_id, user_id)
    if result["code"] == 200:
        flash(result["message"], "success")
        return redirect("/profile")
    else:
        flash(result["message"], "danger")
        return redirect("/profile")

@app.route('/edit-note/<int:note_id>')
@login_required
def update_note(note_id):
    user_id = session.get("user_id")
    result  = get_notes(user_id)
    note    = None
    if result["code"] == 200:
        for n in result["notes"]:
            if n["id"] == note_id:
                note = n
                break
    return render_template('edit_note.html', note=note)

@app.route('/updated', methods=["POST"])
@login_required
def update_note_api():
    note_id = request.form.get("note_id")
    title   = request.form.get("title")
    user_id = session.get("user_id")
    blocks = []
    i = 0
    while True:
        headline    = request.form.get(f"headline_{i}")
        description = request.form.get(f"description_{i}")
        if headline is None:
            break
        blocks.append({"headline": headline, "description": description})
        i += 1
    result = edit_note(note_id, user_id, title, blocks)
    if result["code"] == 200:
        flash("Note updated successfully!", "success")
        return redirect("/profile")
    else:
        flash(result["message"], "danger")
        return redirect(f"/edit-note/{note_id}")

@app.route('/store-note', methods=["POST"])
@login_required
def save_note():
    data = request.get_json()
    title  = data.get("title")
    blocks = data.get("blocks")
    if not title or not blocks:
        return jsonify({"success": False, "message": "Title and blocks are required"})
    user_id = session["user_id"]
    result = store_notes(user_id, title, blocks)
    if result["code"] == 200:
        return jsonify({"success": True, "note_id": result["note_id"]})
    else:
        return jsonify({"success": False, "message": result["message"]})

@app.route('/get-notes', methods=["GET"])
@login_required
def fetch_notes():
    user_id = session["user_id"]
    result = get_notes(user_id)
    if result["code"] == 200:
        return jsonify({"success": True, "notes": result["notes"]})
    else:
        return jsonify({"success": False, "message": result["message"]})


# Save Public Notes to Profile
@app.route('/wishlist-note/<int:note_id>', methods=["GET"])
@login_required
def wishlist_note(note_id):
    user_id = session["user_id"]
    result  = add_wishlist_entry(user_id, note_id)
    if result["code"] == 200:
        flash("Note saved to wishlist!", "success")
    elif result["code"] == 409:
        flash("Already in your wishlist!", "danger")
    else:
        flash("Something went wrong.", "danger")
    return redirect(request.referrer or url_for('public_notes_page'))


@app.route('/remove-wishlist/<int:note_id>', methods=["POST"])
@login_required
def remove_wishlist(note_id):
    user_id = session["user_id"]
    result  = remove_wishlist_entry(user_id, note_id)
    return jsonify({
        "success": result["code"] == 200,
        "action":  result.get("action", ""),
        "message": result.get("message", "")
    })


@app.route('/get-wishlist', methods=["GET"])
@login_required
def fetch_wishlist():
    user_id = session["user_id"]
    result  = get_wishlist(user_id)
    if result["code"] == 200:
        return jsonify({"success": True, "notes": result["notes"]})
    return jsonify({"success": False, "message": result["message"]})


@app.route('/get-folders', methods=["GET"])
@login_required
def fetch_folders():
    user_id = session["user_id"]
    result  = get_folders(user_id)
    if result["code"] == 200:
        return jsonify({"success": True, "folders": result["folders"]})
    return jsonify({"success": False, "message": result["message"]})


@app.route('/create-folder', methods=["POST"])
@login_required
def new_folder():
    user_id = session["user_id"]
    name    = request.get_json().get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "Folder name required"})
    result = create_folder(user_id, name)
    if result["code"] == 200:
        return jsonify({"success": True, "folder_id": result["folder_id"]})
    return jsonify({"success": False, "message": result["message"]})


@app.route('/delete-folder/<int:folder_id>', methods=["POST"])
@login_required
def remove_folder(folder_id):
    user_id = session["user_id"]
    result  = delete_folder(folder_id, user_id)
    return jsonify({"success": result["code"] == 200})


@app.route('/add-to-folder', methods=["POST"])
@login_required
def add_to_folder():
    data      = request.get_json()
    note_id   = data.get("note_id")
    folder_id = data.get("folder_id")
    result    = add_note_to_folder(note_id, folder_id)
    return jsonify({"success": result["code"] == 200, "message": result.get("message","")})


@app.route('/remove-from-folder', methods=["POST"])
@login_required
def remove_from_folder():
    data      = request.get_json()
    note_id   = data.get("note_id")
    folder_id = data.get("folder_id")
    result    = remove_note_from_folder(note_id, folder_id)
    return jsonify({"success": result["code"] == 200})

if __name__ == "__main__":
    app.run(debug=False)
