# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# app = Flask(__name__)
# app.config.from_object('config')
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# db = SQLAlchemy()

# #----------------------------------------------------------------------------#
# # Models.
# #----------------------------------------------------------------------------#

# # class Show(db.Model):
# #     __tablename__ = "Show"
# #     venue_id   = db.Column(db.Integer, db.ForeignKey('Venue.id'),  primary_key=True)
# #     artist_id  = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
# #     start_time = db.Column(db.DateTime(), nullable=False, primary_key=True)

# Show = db.Table(
# 	'Show',
# 	db.Model.metadata,
# 	db.Column('start_time', db.DateTime, primary_key = True),
#   db.Column('venue_id',   db.Integer, db.ForeignKey('Venue.id'),  primary_key=True),
#   db.Column('artist_id',  db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
# )    

# class Venue(db.Model):
#     __tablename__ = 'Venue'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     city = db.Column(db.String(120), nullable=False)
#     state = db.Column(db.String(120), nullable=False)
#     address = db.Column(db.String(120), nullable=False)
#     phone = db.Column(db.String(120), nullable=True)
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     genres = db.Column(db.String(120), nullable=False)
#     website_link = db.Column(db.String(120))
#     seeking_talent = db.Column(db.Boolean(), default=False)
#     seeking_description = db.Column(db.String(120))
#     shows = db.relationship('Artist', secondary=Show, backref=db.backref('shows', lazy=True))

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate
# # venue = Venue(name='Wine House', city='Pretoria', state='GP',address='107 Wine Street',phone='084 973 5307',image_link='https://thumbs.dreamstime.com/z/cooking-setting-fresh-potted-basil-spices-olive-oil-bottle-table-white-background-253556126.jpg', facebook_link='https://facebook.com/thando')

# class Artist(db.Model):
#     __tablename__ = 'Artist'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website_link = db.Column(db.String(120))
#     seeking_venues = db.Column(db.Boolean(), default=False)
#     seeking_description = db.Column(db.String(120))

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate

# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.