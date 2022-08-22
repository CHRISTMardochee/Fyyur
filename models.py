from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# venue_items = db.Table('venue_items',
#     db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
#     db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
# )

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    # genres= db.relationship('Genre', secondary=venue_items,backref=db.backref('venues', lazy=True))
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    website_link = db.Column(db.String(120),nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="venues",lazy=True)


    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, shows: {self.shows} seeking_talent: {self.seeking_talent}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# class Genre(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(), nullable=False)

# artist_items = db.Table('artist_items',
#     db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
#     db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
# )

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    # genres= db.relationship('Genre', secondary=artist_items,backref=db.backref('artists', lazy=True))
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    website_link = db.Column(db.String(120),nullable=False)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="artists",lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, shows: {self.shows} seeking_venue: {self.seeking_venue}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Show ID: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id} start_time: {self.start_time}>'