from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

Show = db.Table(
	'Show',
	db.Model.metadata,
	db.Column('start_time', db.DateTime, primary_key = True),
  db.Column('venue_id',   db.Integer, db.ForeignKey('Venue.id'),  primary_key=True),
  db.Column('artist_id',  db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
) 

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Artist', secondary=Show, backref=db.backref('shows', lazy=True))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))