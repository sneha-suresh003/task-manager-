from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# DB setup
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        role TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        status TEXT,
        assigned_to TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_db()
        conn.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                     (name,email,password,role))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                            (email,password)).fetchone()
        conn.close()

        if user:
            session["user"] = user["name"]
            session["role"] = user["role"]
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":
        title = request.form["title"]
        assigned_to = request.form["assigned_to"]

        conn.execute("INSERT INTO tasks (title,status,assigned_to) VALUES (?,?,?)",
                     (title,"Pending",assigned_to))
        conn.commit()

    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    return render_template("dashboard.html", tasks=tasks,
                           user=session["user"],
                           role=session["role"])

@app.route("/update/<int:id>")
def update(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET status='Done' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)