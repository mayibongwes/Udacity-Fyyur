#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
from wsgiref import validate
from xmlrpc.client import Boolean
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, FlaskForm
from forms import *
from flask_migrate import Migrate
from models import db, Venue,Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  for venue in Venue.query.distinct(Venue.city):
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": []
    })

  for city in data:
    for venue in Venue.query.filter_by(city=city['city']).all():
      city['venues'].append({
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows": 0 # Mayi count upcoming shows
      })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  count = 0
  response = {
    "count": 0,
    "data": []
  }
  try:
      name = request.form.get('search_term')
      data = []
      for venue in Venue.query.filter(Venue.name.contains(name)).all(): # Mayi change this to be case insensitive
        data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": 0  #Mayi count upcoming shows
        })
        count = count + 1
      response['data'] = data
      response['count'] = count
  except:
      print("An error occured in the /venues/search call")
  # if an error occured an empty object will be returned
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = {}
  venue                = db.session.query(Venue).get(venue_id)
  past_shows           = db.session.query(Artist.name,Artist.image_link,Show).join(Venue).filter(Show.c.venue_id == venue_id).filter(Show.c.artist_id == Artist.id).filter(Show.c.start_time<=datetime.now()).all()
  upcoming_shows       = db.session.query(Artist.name,Artist.image_link,Show).join(Venue).filter(Show.c.venue_id == venue_id).filter(Show.c.artist_id == Artist.id).filter(Show.c.start_time>datetime.now()).all()

  if venue is not None:
    data = {
      "id": venue.id,
      "name":venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
    }
    for show in past_shows:
      data["past_shows"].append({
           "artist_id": show['artist_id'],
           "artist_name": show['name'],
           "artist_image_link": show['image_link'],
           "start_time": show['start_time'].isoformat()
      })
      data['past_shows_count'] = data['past_shows_count'] + 1
    for show in upcoming_shows:
      data['upcoming_shows'].append({
        "artist_id": show['artist_id'],
        "artist_name": show['name'],
        "artist_image_link": show['image_link'],
        "start_time": show['start_time'].isoformat()
      })
      data['upcoming_shows_count'] = data['upcoming_shows_count'] + 1

    return render_template('pages/show_venue.html', venue=data)
  else:
    return redirect(url_for('venues'))

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error=False
  try:
    if form.validate():
      data = {
        "name" : request.form.get('name'),
        "city" : request.form.get('city'),
        "state" : request.form.get('state'),
        "address" : request.form.get('address'),
        "phone" : request.form.get('phone'),
        "genres" : request.form.getlist('genres'),
        "facebook" : request.form.get('facebook_link'),
        "image" : request.form.get('image_link'),
        "website" : request.form.get('website_link'),
        "lookingfortalent" : True if request.form.get('seeking_talent') else False,
        "SeekingDesc" : request.form.get('seeking_description')
      }

      venue = Venue(name=data['name'],
                    city=data['city'],
                    state=data['state'],
                    address=data['address'],
                    phone=data['phone'],
                    genres=data['genres'],
                    facebook_link=data['facebook'],
                    image_link=data['image'],
                    website_link=data['website'],
                    seeking_talent=data['lookingfortalent'],
                    seeking_description=data['SeekingDesc']
                  )
      db.session.add(venue)
      db.session.commit()
    else:
      # if form validation is false, we want to go into the except block.
      raise Exception("Form validation error occured!")
  except:
    error=True
    for field, message in form.errors.items():
      flash(field + ' : ' + str(message[0]), 'alert-danger')
    db.session.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  if error:
    return render_template('forms/new_venue.html', form=form)

  flash('Venue ' + request.form['name'] + ' was successfully listed!','alert-success')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = db.session.query(Venue).get(venue_id)
    shows = db.session.query(Show).join(Venue).filter(Show.c.venue_id == venue.id).all()

    # first delete shows related to venue
    for show in shows:
      db.session.delete(show)

    # Then once venue is not linked to any show, delete venue
    db.session.delete(venue)

    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    flash('Venue ' + venue_id + ' was successfully deleted!', 'alert-success')
    return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  for artist in Artist.query.all():
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  count = 0
  response = {
    "count": 0,
    "data": []
  }
  try:
    name = request.form.get('search_term')
    data = []
    for artist in Artist.query.filter(Artist.name.contains(name)).all():
      upcoming_shows = db.session.query(Show).join(Artist).filter(Show.c.artist_id == artist.id).filter(Show.c.start_time>=datetime.now()).count()
      print(upcoming_shows)
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": upcoming_shows
      })
      count = count + 1
    response['data'] = data
    response['count'] = count
  except:
      print("An error occured in the /venues/search call")

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  data = {}
  artist = db.session.query(Artist).get(artist_id)
  past_shows           = db.session.query(Venue.name,Venue.image_link,Show).join(Artist).filter(Show.c.artist_id == artist_id).filter(Show.c.venue_id == Venue.id).filter(Show.c.start_time<=datetime.now()).all()
  upcoming_shows       = db.session.query(Venue.name,Venue.image_link,Show).join(Artist).filter(Show.c.artist_id == artist_id).filter(Show.c.venue_id == Venue.id).filter(Show.c.start_time>datetime.now()).all()
  
  if artist is not None:
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venues,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
    }
    for show in past_shows:
      data["past_shows"].append({
           "venue_id": show['artist_id'],
           "venue_name": show['name'],
           "venue_image_link": show['image_link'],
           "start_time": show['start_time'].isoformat()
      })
      data['past_shows_count']= data['past_shows_count'] + 1
    for show in upcoming_shows:
      data['upcoming_shows'].append({
        "venue_id": show['artist_id'],
        "venue_name": show['name'],
        "venue_image_link": show['image_link'],
        "start_time": show['start_time'].isoformat()
      })
      data['upcoming_shows_count'] = data['upcoming_shows_count'] + 1

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = {}
  # query data from database and store it in a variable
  data = db.session.query(Artist).get(artist_id)

  #check if this is a valid object before workin with it
  if data is not None:
    artist = {
      "id": data.id,
      "name": data.name,
      "city": data.city,
      "state": data.state,
      "phone": data.phone,
      "website_link": data.website_link,
      "facebook_link": data.facebook_link,
      "seeking_venue": data.seeking_venues,
      "seeking_description": data.seeking_description,
      "image_link": data.image_link
    }

    form.genres.data = data.genres
    form.seeking_venue.data = data.seeking_venues
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = db.session.query(Artist).get(artist_id)
  error = False
  # only attemp to to edit the artist of artist record exists on database and form validation passed
  if artist is not None and form.validate():
    try:
      data = {
        "name" : request.form.get('name'),
        "city" : request.form.get('city'),
        "state" : request.form.get('state'),
        "address" : request.form.get('address'),
        "phone" : request.form.get('phone'),
        "genres" : request.form.getlist('genres'),
        "facebook" : request.form.get('facebook_link'),
        "image" : request.form.get('image_link'),
        "website_link" : request.form.get('website_link'),
        "seeking_venue" : True if request.form.get('seeking_venue') else False,
        "SeekingDesc" : request.form.get('seeking_description')
      }
    
      artist.name=data['name']
      artist.city=data['city']
      artist.state=data['state']
      artist.address=data['address']
      artist.phone=data['phone']
      artist.genres=data['genres']
      artist.facebook_link=data['facebook']
      artist.image_link=data['image']
      artist.website_link=data['website_link']
      artist.seeking_venue=data['seeking_venue']
      artist.seeking_description=data['SeekingDesc']

      db.session.commit()
    except:
      error=True
      flash('An error occurred. Artist ' + request.form['name']+ ' could not be edited.', 'alert-warning')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    error=True
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be edited.', 'alert-warning')
    for field, message in form.errors.items():
      flash(field + ' : ' + str(message[0]), 'alert-danger')

  if error:
    artist = db.session.query(Artist).get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  flash('Artist ' + request.form['name'] + ' was successfully Edited!', 'alert-success')  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = {}
  # query data from database and store it in a variable
  data = db.session.query(Venue).get(venue_id)

  #check if this is a valid object before workin with it
  if data is not None:
    venue = {
      "id": data.id,
      "name": data.name,
      "address": data.address,
      "city": data.city,
      "state": data.state,
      "phone": data.phone,
      "website": data.website_link,
      "facebook_link": data.facebook_link,
      "website_link": data.website_link,
      "seeking_description": data.seeking_description,
      "image_link": data.image_link
    }
    form.genres.data = data.genres
    form.seeking_talent.data = data.seeking_talent

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = db.session.query(Venue).get(venue_id)
  error = False

  if venue is not None and form.validate():
    try:
      data = {
        "name" : request.form.get('name'),
        "city" : request.form.get('city'),
        "state" : request.form.get('state'),
        "address" : request.form.get('address'),
        "phone" : request.form.get('phone'),
        "genres" : request.form.getlist('genres'),
        "facebook" : request.form.get('facebook_link'),
        "image" : request.form.get('image_link'),
        "website" : request.form.get('website_link'),
        "lookingfortalent" : True if request.form.get('seeking_talent') else False,
        "SeekingDesc" : request.form.get('seeking_description')
      }
    
      venue.name=data['name']
      venue.city=data['city']
      venue.state=data['state']
      venue.address=data['address']
      venue.phone=data['phone']
      venue.genres=data['genres']
      venue.facebook_link=data['facebook']
      venue.image_link=data['image']
      venue.website_link=data['website']
      venue.seeking_talent=data['lookingfortalent']
      venue.seeking_description=data['SeekingDesc']

      db.session.commit()
    except:
      error=True
      flash('An error occurred. Venue ' + request.form['name']+ ' could not be edited.', 'alert-warning')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    error=True
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be edited.', 'alert-warning')
    for field, message in form.errors.items():
      flash(field + ' : ' + str(message[0]), 'alert-danger')

  if error:
    venue = db.session.query(Venue).get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  flash('Venue ' + request.form['name'] + ' was successfully Edited!', 'alert-success')      
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  error=False
  data = {}
  try:
    if form.validate():
      data = {
        "name" : request.form.get('name'),
        "city" : request.form.get('city'),
        "state" : request.form.get('state'),
        "phone" : request.form.get('phone'),
        "genres" : request.form.getlist('genres'),
        "facebook" : request.form.get('facebook_link'),
        "image" : request.form.get('image_link'),
        "website" : request.form.get('website_link'),
        "lookingforvenues" : True if request.form.get('seeking_venue') else False,
        "SeekingDesc" : request.form.get('seeking_description')
      }

      artist = Artist(name=data['name'],
                      city=data['city'],
                      state=data['state'],
                      phone=data['phone'],
                      genres=data['genres'],
                      facebook_link=data['facebook'],
                      image_link=data['image'],
                      website_link=data['website'],
                      seeking_venues=data['lookingforvenues'],
                      seeking_description=data['SeekingDesc']
                  ) 
      db.session.add(artist)
      db.session.commit()
    else:
      # if form validation is false, we want to go into the except block.
      raise Exception("Form validation error occured!")
  except:
    error=True
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.', 'alert-danger')
    for field, message in form.errors.items():
      flash(field + ' : ' + str(message[0]), 'alert-danger')
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    return render_template('forms/new_artist.html', form=form)

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!', 'alert-success')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  shows = db.session.query(Artist.name,Artist.image_link,Show).join(Artist).filter(Show.c.artist_id == Artist.id).order_by(Show.c.start_time.desc()).all()
  for show in shows:
    venue = db.session.query(Venue).get(show['venue_id'])
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": show['artist_id'],
      "artist_name": show['name'],
      "artist_image_link": show['image_link'],
      "start_time": show['start_time'].isoformat()
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error=False
  try:
    artist_id  = request.form.get('artist_id')
    venue_id   = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    statement = Show.insert().values(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.execute(statement)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!', 'alert-success')
  else:
    flash('An error occurred. Show could not be listed.', 'alert-danger')
  # on successful db insert, flash success

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
