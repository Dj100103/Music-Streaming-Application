import os
import base64
from io import BytesIO
from flask import Flask, redirect, render_template, request, url_for, Response, session
from flask_sqlalchemy import SQLAlchemy

curr_dir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(curr_dir, "db.db")
db = SQLAlchemy(app)
db.init_app(app)
app.secret_key = '123'
app.app_context().push()

class admin(db.Model):
    __tablename__='admin'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String, nullable=False)
    password=db.Column(db.String, nullable=False)

class user(db.Model):
    __tablename__="user"
    user_id=db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False)
    # one to one relationship with creator
    creator = db.relationship('creator', backref='users', uselist=False)

class creator(db.Model):
    __tablename__='creator'
    creator_id=db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    name=db.Column(db.String, nullable=False, unique=True)
    # One-to-Many relationship with Albums
    albums = db.relationship('albums', backref='creators', lazy=True)
    # one to many relationship with creator
    songs = db.relationship('songs', backref='creators', lazy=True)

song_albums = db.Table('song_albums',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('album_id', db.Integer, db.ForeignKey('albums.id'), primary_key=True)
)

song_playlists = db.Table('song_playlists',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
)

class songs(db.Model):
    __tablename__='songs'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    file=db.Column(db.LargeBinary(), nullable=False)
    song_name=db.Column(db.String, nullable=False)
    song_lyrics=db.Column(db.String, nullable=True)
    genre=db.Column(db.String, nullable=False)
    song_writer_id = db.Column(db.Integer, db.ForeignKey('creator.creator_id'))
    albums = db.relationship('albums', secondary=song_albums, backref=db.backref('song', lazy='dynamic'))
    ratings = db.relationship('SongRating', backref='song', cascade='all, delete-orphan')
    playlist=db.relationship('playlists', secondary=song_playlists, backref=db.backref('song', lazy='dynamic'))

class SongRating(db.Model):
    __tablename__ = 'song_ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Assuming a User model exists
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)  # Assuming a Song model exists
    rating = db.Column(db.Integer, nullable=False)

class albums(db.Model):
    __tablename__='albums'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_name=db.Column(db.String, nullable=False)
    album_creator=db.Column(db.Integer, db.ForeignKey('creator.creator_id'), nullable=False)
    # songs = db.relationship('songs', backref='albums', lazy=True)

class playlists(db.Model):
    __tablename__='playlists'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_name=db.Column(db.String, nullable=False)
    playlist_creator=db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

db.create_all()

def creator_ratings(cre_id):
    songss=songs.query.filter_by(song_writer_id=cre_id).all()
    # print(songss)
    l=[]
    for x in songss:
        l.append(x.id)
    # print(l)
    ratings=SongRating.query.filter(SongRating.song_id.in_(l)).all()
    # print(ratings)
    tot=0
    for x in ratings:
        tot+=x.rating
    return(tot/len(ratings))

def avg_ratings_song(song_id):
    songa=songs.query.get(int(song_id))
    print(songa.ratings)
    if len(songa.ratings)>0:
        tot=0
        for x in songa.ratings:
            tot+=x.rating
        return(tot/len(songa.ratings))
    return 0


def create_album_with_selected_songs(selected_song_ids, title, creator_id):
    # Fetch the selected songs based on their IDs
    selected_songs = songs.query.filter(songs.id.in_(selected_song_ids)).all()

    # Create a new album
    new_album = albums(album_name=title, album_creator=creator_id)  # Replace creator_id with the appropriate creator's ID
    print(type(new_album.song))
    # Associate selected songs with the new album
    new_album.song.extend(selected_songs)

    # Add the album to the database session
    db.session.add(new_album)

    # Commit changes to the database
    db.session.commit()

def create_playlist_with_selected_songs(selected_song_ids, title, user_id):
    # Fetch the selected songs based on their IDs
    selected_songs = songs.query.filter(songs.id.in_(selected_song_ids)).all()

    # Create a new album
    new_playlist = playlists(playlist_name=title, playlist_creator=user_id)  # Replace creator_id with the appropriate creator's ID
    print(type(new_playlist.song))
    # Associate selected songs with the new album
    new_playlist.song.extend(selected_songs)

    # Add the album to the database session
    db.session.add(new_playlist)

    # Commit changes to the database
    db.session.commit()

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="GET":
        return render_template('register.html', type='user')
    elif request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        user1=user(username=username, password=password)
        try:
            db.session.add(user1)
            db.session.commit()
            return redirect(url_for('login', type='user'))
        except:
            return render_template('usere.html')



@app.route("/login/<type>", methods=["GET", "POST"])
def login(type):
    if type=="admin":
        if request.method=="GET":
            return render_template('login.html')
    elif type == "user":
        if request.method == "GET":
            session.clear()
            return render_template('userlog.html', password_="apple")
        elif request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            try:
                users = user.query.filter_by(username=username).one()
                if users and users.password == password:
                    session['user_id'] = users.user_id  # Store user_id in the session
                    return redirect(url_for('homepage'))
                else:
                    return render_template('userlog.html', password_='wrong')
            except:
                return render_template('register.html', nuf="True")
                
@app.route("/homepage", methods=["GET"])
def homepage():
    if request.method=="GET":
        if 'user_id' in session:
            user_id = session['user_id']
            users = user.query.get(user_id)
            try:
                cre_id=creator.query.filter_by(user_id=int(user_id)).one()
                if cre_id:
                    session['cre_id']=cre_id.creator_id
                # print(cre_id)
                cre_id=session['cre_id']
                if_creator=True
                songss=songs.query.all()
                user_playlists=playlists.query.filter_by(playlist_creator=user_id).all()
                # print(songss)
                return render_template('loghome.html', user_id=int(user_id), is_creator=if_creator, songs=songss, username=users.username, cre_id=cre_id, playlist=user_playlists)
            except:
                songss=songs.query.all()
                user_playlists=playlists.query.filter_by(playlist_creator=user_id).all()
                return render_template('loghome.html', user_id=int(user_id), is_creator=False, songs=songss, username=users.username, playlist=user_playlists)
        else:
            return redirect(url_for('login', type='user'))

@app.route("/creator", methods=["GET", "POST"])
def creator1():
    if 'user_id' in session:
        if request.method=="GET":
            return render_template('register.html', type="creator", nuf="False")
        elif request.method=="POST":
            try:
                user_id=session['user_id']
                name=request.form.get('creator_name')
                cre=creator(user_id=user_id, name=name)
                db.session.add(cre)
                db.session.commit()
                crea=creator.query.filter_by(user_id=user_id).one()
                session['cre_id']=crea.creator_id
            except:
                crea=creator.query.filter_by(user_id=user_id).one()
                session['cre_id']=crea.creator_id
            return redirect(url_for('creator_account'))
            # return render_template('loghome.html', user_id=user_id, is_creator=True)        
    else:
        return redirect(url_for('login', type='user'))

@app.route("/creator_account", methods=["GET", "POST"])
def creator_account():
    if 'user_id' and 'cre_id' in session:
        if request.method=="GET":
            print(session['user_id'], session['cre_id'])
            try:
                user_id=session['user_id']
                cre_id=session['cre_id']
                songss=songs.query.filter_by(song_writer_id=cre_id).all()
                print(songss)
                try:
                    total_rating=creator_ratings(cre_id)
                    print(total_rating)
                except:
                    total_rating=0
                try:
                    albumss=albums.query.filter_by(album_creator=cre_id).all()
                    print(albumss)
                except:
                    albumss=[]
                return render_template('creatorpage.html', user_id=user_id, songs=songss, albums=albumss, cre_id=cre_id, total_songs=len(songss), total_albums=len(albumss), total_ratings=total_rating)
            except:
                return render_template('creatorpage.html', user_id=user_id, cre_id=cre_id, total_songs=0, total_albums=0, total_ratings=0)
    else:
        return redirect(url_for('login', type='user'))

@app.route("/addsong", methods=["GET", "POST"])
def song():
    if 'cre_id' in session:
        if request.method=="GET":
            return render_template('addsong.html', cre_id=session['cre_id'])
        elif request.method=="POST":
            file=request.files['file']
            song_name=request.form.get('song_name')
            song_writer_id=int(session['cre_id'])
            user=creator.query.filter_by(creator_id=session['cre_id']).all()
            user_id=session['user_id']
            song_lyrics=request.form.get('song_lyrics')
            genre=request.form.get('genre')
            accepted_mimetypes=['audio/mpeg', 'audio/wav', 'audio/ogg']
            if file.mimetype in accepted_mimetypes:
                song1=songs(file=file.read(), song_name=song_name, song_lyrics=song_lyrics, genre=genre, song_writer_id=song_writer_id)
                db.session.add(song1)
                db.session.commit()
                songss=songs.query.filter_by(song_writer_id=session['cre_id']).all()
                print(songss)
                try:
                    alby=albums.query.all()
                    for x in alby:
                        song_album=song_albums(song_id=x.song_id, album_id=x.id)
                        db.session.add(song_album)
                        db.session.commit()
                except:
                    pass
                return redirect(url_for('creator_account'))
            else:
                return('<p>upload song file only</p>')
    else:
        return redirect(url_for('login', type='user'))
    

@app.route("/listen_to/<song_id>/<type>/<id>/<way>", methods=["GET"])
def song_(song_id, type, id, way):
    if 'user_id' and 'cre_id' in session:
        if request.method=="GET":
            music = songs.query.get(song_id)
            cre_id=music.song_writer_id
            user_id=int(id)
            music_data = base64.b64encode(music.file).decode('utf-8')
            try:
                playlist_id=session['playlist_id']
                return render_template('listen.html', music_data=music_data, music_name=music.song_name, music_lyrics=music.song_lyrics, writer=music.song_writer_id, user_id=user_id, music1=music.id, listener=type, average_rating=avg_ratings_song(song_id), way=way, playlist_id=playlist_id)
            except:
                return render_template('listen.html', music_data=music_data, music_name=music.song_name, music_lyrics=music.song_lyrics, writer=music.song_writer_id, user_id=user_id, music1=music.id, listener=type, average_rating=avg_ratings_song(song_id), way=way)
    else:
        return redirect(url_for('login', type='user'))

@app.route("/create_album", methods=["GET", "POST"])
def album():
    if 'user_id' and 'cre_id' in session:
        if request.method=="GET":
            cre_id=session['cre_id']
            songss=songs.query.filter_by(song_writer_id=cre_id).all()
            return render_template("create_album.html", songs=songss)
        elif request.method=="POST":
            cre_id=session['cre_id']
            creators=creator.query.filter_by(creator_id=cre_id).one()
            son=request.form.getlist('song_name')
            album_name=request.form.get('album_name')
            create_album_with_selected_songs(son,album_name,cre_id)
            return redirect(url_for('creator_account'))
    else:
        return redirect(url_for('login', type='user'))

@app.route("/create_playlist", methods=["GET", "POST"])
def playlist_():
    if 'user_id' and 'cre_id' in session:
        if request.method=="GET":
            songss=songs.query.all()
            return render_template("create_playlist.html", songs=songss)
        elif request.method=="POST":
            user_id=session['user_id']
            # users=user.query.filter_by(user_id=user_id).one()
            son=request.form.getlist('song_name')
            playlist_name=request.form.get('album_name')
            create_playlist_with_selected_songs(son,playlist_name,int(user_id))
            return redirect(url_for('homepage'))
    else:
        return redirect(url_for('login', type='user'))

@app.route("/songs_of/<type>/<id>", methods=["GET"])
def songs_of(type, id):
    if 'user_id' and 'cre_id' in session:
        if type=='writer':
            creator_id=int(id)
            cre=creator.query.filter_by(creator_id=creator_id).all()
            songss=cre[0].songs
            print(songss)
            return render_template('wap.html', type='writer', songs=songss, user_id=session['user_id'])
        elif type=="album":
            songs_of_album = songs.query.filter(songs.albums.any(id=id)).all()
            print(songs_of_album)
            return render_template('wap.html', type=type, songs=songs_of_album)
        elif type=="playlist":
            songs_of_playlist = songs.query.filter(songs.playlist.any(id=id)).all()
            print(songs_of_playlist)
            session['playlist_id']=id
            return render_template('wap.html', type=type, songs=songs_of_playlist, user_id=session['user_id'])
    else:
        return redirect(url_for('login', type='user'))

@app.route("/update/<type>/<id>", methods=["GET", "POST", "DELETE"])
def update_song(type, id):
    if 'user_id' and 'cre_id' in session:
        if request.method=="GET":
            if type=="song":
                song=songs.query.filter_by(id=id).one()
                return render_template('update.html', song=song, type='songa')
            elif type=="album":
                album=albums.query.get(id)
                songsa=songs.query.filter_by(song_writer_id=album.album_creator).all()
                songs_of_album = songs.query.filter(songs.albums.any(id=id)).all()
                return render_template('update.html', album=album, type='album', songs_of_album=songs_of_album, songs=songsa)
            elif type=="playlist":
                playlist=playlists.query.get(id)
                songsa=songs.query.all()
                songs_of_playlist = songs.query.filter(songs.playlist.any(id=id)).all()
                return render_template('update.html', playlist=playlist, type='playlist', songs_of_playlist=songs_of_playlist, songs=songsa)  
        elif request.method=="POST":
            if type=="song":
                song=songs.query.filter_by(id=id).one()
                song.song_name=request.form.get("song_name")
                song.song_lyrics=request.form.get("lyrics")
                song.genre=request.form.get("genre")
                db.session.commit()
                creators=creator.query.filter_by(creator_id=song.song_writer_id).one()
                return redirect(url_for('creator_account'))
            elif type=="album":
                album=albums.query.get(id)
                songs_of_new_album = request.form.getlist('song_name')
                album.album_name=request.form.get('album_name')
                if album:
                    ex_songs_of_album = album.song.all()
                    for song in ex_songs_of_album:
                        if song.id not in songs_of_new_album:
                            album.song.remove(song)
                    for song_id in songs_of_new_album:
                        existing_song = songs.query.filter_by(id=song_id).first()
                        if existing_song not in album.song:
                            album.song.append(existing_song)
                    db.session.commit()
                    cre_id=album.album_creator
                    creators=creator.query.get(cre_id)
                    return redirect(url_for('creator_account'))
            elif type=="playlist":
                playlist=playlists.query.get(id)
                print(playlist)
                songs_of_new_playlist = request.form.getlist('song_name')
                playlist.playlist_name=request.form.get('playlist_name')
                if playlist:
                    ex_songs_of_playlist = playlist.song.all()
                    for song in ex_songs_of_playlist:
                        if song.id not in songs_of_new_playlist:
                            playlist.song.remove(song)
                    for song_id in songs_of_new_playlist:
                        existing_song = songs.query.filter_by(id=song_id).first()
                        if existing_song not in playlist.song:
                            playlist.song.append(existing_song)
                    db.session.commit()
                    user_id=playlist.playlist_creator
                    return redirect(url_for('homepage'))
    else:
        return redirect(url_for('login', type='user'))               
            
@app.route("/delete/<type>/<id>", methods=["GET"])
def delete(type, id):
    if 'user_id' and 'cre_id' in session:
        if request.method=="GET":
            if type=="song":
                song=songs.query.get(id)
                cre_id=song.song_writer_id
                db.session.delete(song)
                db.session.commit()
                creators=creator.query.filter_by(creator_id=cre_id).one()
                return redirect(url_for('creator_account'))
            elif type=="album":
                album=albums.query.get(id)
                cre_id=album.album_creator
                creators=creator.query.get(cre_id)
                if album:
                    db.session.delete(album)
                    db.session.commit()
                    return redirect(url_for('creator_account'))
            elif type=="playlist":
                playlist=playlists.query.get(id)
                user_id=playlist.playlist_creator
                if playlist:
                    db.session.delete(playlist)
                    db.session.commit()
                    return redirect(url_for('homepage'))
    else:
        return redirect(url_for('login', type='user'))

@app.route("/rate_song/<song_id>/<rating>/<way>", methods=["GET"])
def rate_song(song_id, rating, way):
    if 'user_id' and 'cre_id' in session:
        if request.method=="GET":
            user_id=session['user_id']
            song=songs.query.get(song_id)
            users=user.query.get(user_id)
            existing_rating = SongRating.query.filter_by(song_id=song_id, user_id=user_id).first()
            if existing_rating:
                # Update the existing rating
                existing_rating.rating = int(rating)
                db.session.commit()
                # return ('rating_updated')
                return redirect(url_for('song_', song_id=song_id, type='user', id=user_id, way=way))
            else:
                # Create a new rating
                new_rating = SongRating(user_id=user_id, song_id=song_id, rating=int(rating))
                db.session.add(new_rating)
                db.session.commit()
                return redirect(url_for('song_', song_id=song_id, type='user', id=user_id, way=way))
    else:
        return redirect(url_for('login', type='user'))
    
@app.route("/add_to_album/<song_id>", methods=["GET", "POST"])
def add_to_album(song_id):
    if request.method=="GET":
        try:
            albumss=albums.query.filter_by(album_creator=session['cre_id']).all()
        except:
            albumss=[]
        return render_template('add_to_album.html', albums=albumss)
    elif request.method=="POST":
        cre_id=session['cre_id']
        ans=request.form.get('album_name')
        print(ans)
        print(type(ans))
        try:
            album=albums.query.get(int(ans))
            l=[album]
            print(len(l))
            if len(l)==1:
                try:
                    ex_songs_of_album = album.song.all()
                    existing_song = songs.query.get(song_id)
                    print(existing_song, ex_songs_of_album)
                    if existing_song in ex_songs_of_album:
                        print('done')
                        return redirect(url_for('song_', song_id=song_id, type='creator', id=cre_id, way='c'))
                except:
                    existing_song = songs.query.get(song_id)
                    album.song.append(existing_song)
                    db.session.commit()
                    print('done')
                    return redirect(url_for('song_', song_id, 'creator', cre_id, 'c'))
        except:
            return redirect(url_for('album'))

@app.route("/adm", methods=["GET", "POST"])
def admins():
    if request.method=="GET":
        return render_template("admin.html", login='yes')
    elif request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        try:
            admin1=admin.query.filter_by(username=username).all()
            try:
                admin1=admin1.query.filter_by(password=password).one()
                songss=songs.query.all()
                albumss=albums.query.all()
                song_rating=SongRating.query.all()
                creators=creator.query.all()
                return render_template('admin.html', login='no', songs=songss, albums=albumss, song_rating=song_rating, creators=creators)
            except:
                return render_template('admin.html', login='wrong')
        except:
            return render_template('admin.html',login='nuf')

      



