from flask import Flask, request, render_template, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "mysecretkey"


# Connect to database
def get_db():
    conn = sqlite3.connect("database.db")
    return conn


# Create users table
def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return redirect("/register")


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered!"


    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            session["name"] = user[1]
            session["email"] = user[2]
            return redirect("/dashboard")

        else:
            return "Invalid email or password!"


    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "name" in session:
        return render_template(
            "dashboard.html",
            name=session["name"]
        )

    return redirect("/login")

# Change Password
@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (session["email"], old_password)
        ).fetchone()

        if user:

            conn.execute(
                "UPDATE users SET password = ? WHERE email = ?",
                (new_password, session["email"])
            )

            conn.commit()
            conn.close()

            return "Password changed successfully! <br><br><a href='/dashboard'>Go to Dashboard</a>"

        else:
            conn.close()
            return "Old password is incorrect!"

    return render_template("change_password.html")


# Logout


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)