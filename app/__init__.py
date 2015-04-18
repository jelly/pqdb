import sqlite3

from flask import Flask, g, render_template, redirect, flash, request, url_for

app = Flask(__name__)
app.config.from_object('config')

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('../schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def show_quotes():
    db = get_db()
    cur = db.execute('select author, text, ts from quotes order by id desc')
    quotes = cur.fetchall()
    return render_template('index.html', quotes=quotes)

@app.route('/add', methods=['POST', 'GET'])
def add_quote():
    if request.method == 'POST':
        db = get_db()
        # XSS http://flask.pocoo.org/docs/0.10/security/#cross-site-scripting-xss
        db.execute('insert into quotes (text, author) values (?, ?)', (request.form['text'], request.form['author']))
        db.commit()
        #flash('New quote has been added succsefully
        return redirect(url_for('show_quotes'))
    else:
        return render_template('add.html')
