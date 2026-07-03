from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from .auth import login_required
from .db import get_db

bp = Blueprint('music', __name__)

@bp.route('/')
def index():
    db = get_db()
    songs = db.execute(
        'SELECT s.id, title, artist, album, genre, created, author_id, username'
        ' FROM song s JOIN user u ON s.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('music/index.html', songs=songs)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        album = request.form['album']
        genre = request.form['genre']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO song (title, artist, album, genre, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, artist, album, genre, g.user['id'])
            )
            db.commit()
            return redirect(url_for('music.index'))

    return render_template('music/create.html')

def get_song(id, check_author=True):
    song = get_db().execute(
        'SELECT s.id, title, artist, album, genre, created, author_id, username'
        ' FROM song s JOIN user u ON s.author_id = u.id'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()

    if song is None:
        abort(404, f"Song id {id} doesn't exist.")

    if check_author and song['author_id'] != g.user['id']:
        abort(403)

    return song

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    song = get_song(id)

    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        album = request.form['album']
        genre = request.form['genre']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE song SET title = ?, artist = ?, album = ?, genre = ?'
                ' WHERE id = ?',
                (title, artist, album, genre, id)
            )
            db.commit()
            return redirect(url_for('music.index'))

    return render_template('music/update.html', song=song)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_song(id)
    db = get_db()
    db.execute('DELETE FROM song WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('music.index'))