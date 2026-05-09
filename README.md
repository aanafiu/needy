# Needy — Community Note Sharing Platform
#### Video Demo: https://www.youtube.com/watch?v=j42gokC9tQg
#### Description:

## What is Needy?

Needy is a full-stack web application that allows users to write, organize, and discover structured notes shared across a community. Think of it as a lightweight, block-based knowledge-sharing platform where every note is publicly readable, but only registered users can create, edit, and manage their own content. The name "Needy" reflects the idea that everyone needs a place to store and share what they know — and this is that place.

The project was built using **Python Flask** for the backend, **MySQL** for persistent data storage, **Jinja2** for server-side HTML templating, and **Vanilla JavaScript** for all client-side interactivity. No JavaScript frameworks were used — every interactive element including modals, search filtering, folder management, and wishlist toggling was written from scratch.

---

## Project Files and What They Do

### `app.py`
This is the main Flask application file. It defines all the URL routes and connects the frontend templates to the backend database logic. Routes include user registration and login, note creation and editing, the public explore page, the user profile page, wishlist management, and folder operations. The file also initializes the database on startup by calling `setup_db()` at the module level, which ensures all tables exist before the first request is handled. Flask sessions are used to track the logged-in user across requests.

### `db.py`
This file contains every database operation in the application. It connects to a MySQL database using environment variables for credentials, making it safe to deploy without hardcoding sensitive information. The file defines functions for creating and managing users, notes, note blocks, wishlists, folders, and note-folder mappings. Each function opens its own database connection, executes a query, and closes the connection cleanly using a `finally` block to prevent connection leaks. Passwords are never stored as plain text — Werkzeug's `generate_password_hash` and `check_password_hash` functions are used for secure password handling.

### `helper.py`
This file contains a single decorator function called `login_required`. It wraps any route that requires the user to be logged in and redirects unauthenticated users to the login page. This pattern keeps the authentication logic clean and reusable across all protected routes.

### `templates/layout.html`
The base HTML template that all other pages extend. It includes the navigation bar, flash message display, Bootstrap CSS and JS, Font Awesome icons, and links to the custom stylesheet and JavaScript files. The modal for public note previews is also defined here so it is available on every page.

### `templates/login.html` and `templates/register.html`
These templates render the login and registration forms. They extend the base layout and use Flask's form handling to submit credentials via POST requests. Flash messages inform the user of errors or success.

### `templates/notes.html`
The note creation page. It features a two-step composer — the user first enters a title, then builds content block by block. Each block consists of a headline and a description. The composer is entirely JavaScript-driven and sends the finished note to the backend as a JSON payload via a `fetch` POST request.

### `templates/profile.html`
The user profile page. It displays all notes the user has written, with click-to-preview modals for each one. It also shows the folder management system where users can create folders, assign notes to them, and remove notes from folders. Below that is the Saved Notes section which displays the user's wishlist fetched from the server. All three sections — My Notes, Folders, and Saved Notes — use JavaScript fetch calls to interact with the backend without reloading the page.

### `templates/public_notes.html`
The public Explore page visible to all visitors. It fetches all notes from the database and renders them in a responsive grid. Each card shows the note title, author, date, and a preview of the first two content blocks. Clicking a card opens a full reading modal. A real-time search bar filters notes by title or author name as the user types. Logged-in users can save notes to their wishlist by clicking the heart icon.

### `templates/edit_note.html`
The note editing page. It pre-fills all existing note data into editable input fields and allows users to modify the title, update existing blocks, and add new blocks before saving. The updated note replaces the old blocks entirely in the database to keep the data clean.

### `static/styles.css`
The main stylesheet for the entire application. It defines a warm amber and dark green color scheme, glassmorphism card effects, animated background orbs, folder tab styling, modal layouts, and responsive grid systems. No CSS framework beyond Bootstrap utilities is used.

### `static/notes.js`
A shared JavaScript file loaded on every page. It contains the event listeners for the note title and block headline inputs for keyboard shortcuts. It also contains null checks to prevent errors on pages where those input elements do not exist.

### `static/flash_script.js`
A small JavaScript file that automatically fades out and removes Flask flash messages after three seconds so they do not permanently occupy screen space.

---

## Design Decisions

**Block-based note structure:** Early in development I considered allowing freeform text notes, but decided on a structured block format instead. This forces users to organize their writing into labelled sections, which makes notes significantly more readable for other community members browsing the Explore page.

**Vanilla JavaScript only:** I deliberately chose not to use React, Vue, or any JavaScript framework. This was a conscious decision to deeply understand how the DOM works, how to manage state manually, and how to communicate with a Flask backend using the Fetch API. Every modal, tab system, and live filter was built without a library.

**Separate cursor for block queries:** MySQL cursors cannot be reused inside a loop while a previous result set is still open. I solved this by opening a second cursor (`cur2`) for block queries inside each loop iteration. This was an important lesson in how database connections and cursor state work in practice.

**Server-side session management:** Rather than storing user identity in localStorage or a cookie that could be tampered with, all authentication state is stored in Flask's server-side session. The user ID is always read from the session on the server — never trusted from JavaScript.

**Environment variables for credentials:** All database credentials and the Flask secret key are stored in a `.env` file and loaded with `python-dotenv`. This means sensitive values are never committed to the GitHub repository and the same codebase works in both local development and production deployment without any code changes.

---

## Technologies Used

- **Python 3** — Backend language
- **Flask** — Web framework
- **MySQL** — Relational database
- **Jinja2** — HTML templating
- **Vanilla JavaScript** — Client-side interactivity
- **Bootstrap 5** — Layout utilities
- **Werkzeug** — Password hashing
- **python-dotenv** — Environment variable management
- **Gunicorn** — Production WSGI server
- **Render.com** — Cloud deployment platform
