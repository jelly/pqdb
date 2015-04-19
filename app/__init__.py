import sqlite3
from math import ceil

from flask import Flask, g, render_template, redirect, flash, request, url_for

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']

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
@app.route('/<int:page>')
def show_quotes(page=1):
    db = get_db()
    page_size = app.config['PAGINATION']
    cur = db.execute('select count(*) as total from quotes')
    total = cur.fetchone()['total']
    pages = int(ceil(total / float(page_size)))

    if 0 < page <= pages:
        offset = (page-1) * page_size
    else:
        pages = offset = 0 # XXX: or just display last page?

    cur = db.execute('select author, text, ts from quotes order by id desc limit ?, ?', (offset ,page_size))
    quotes = cur.fetchall()
    return render_template('index.html', quotes=quotes, pages=pages, current=page)

@app.route('/add', methods=['POST', 'GET'])
def add_quote():
    if request.method == 'POST':
        db = get_db()
        # XSS http://flask.pocoo.org/docs/0.10/security/#cross-site-scripting-xss
        db.execute('insert into quotes (text, author) values (?, ?)', (request.form['text'], request.form['author']))
        db.commit()
        flash('New quote has been added succsefully')
        return redirect(url_for('show_quotes'))
    else:
        return render_template('add.html')

@app.route('/random')
def random_quote():
    db = get_db()
    cur = db.execute('select author, text, ts from quotes order by random() limit 1')
    quote =  cur.fetchone()
    print quote
    return render_template('random.html', quote=quote)
