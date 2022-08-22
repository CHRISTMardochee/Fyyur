#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from doctest import FAIL_FAST
import json
import re
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import *

# TODO: connect to a local postgresql database

    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value) if isinstance(value, str) else value
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  areas,data = Venue.query.distinct(Venue.city).with_entities(Venue.city,Venue.state).all(),[]
  for area in areas:
      venues_data = []
      for venue in Venue.query.filter(Venue.city==area.city):
        data_venue = {"id": venue.id,"name": venue.name,"num_upcoming_shows": len(venue.shows)}
        venues_data.append(data_venue)
      datum = {"city":area.city,"state":area.state,"venues":venues_data}
      data.append(datum)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term,data=request.form.get('search_term', ''),[]
  items , items_count= Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all(), Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).count()
  for item in items:
    data_item={
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows":db.session.query(Show).join(Venue).filter(Show.venue_id==item.id).count()
    }
    data.append(data_item)
  response={
    "count": items_count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


def get_detail_show(item):
  artist = Artist.query.get(item.artist_id)
  venue = Venue.query.get(item.venue_id)
  return {
    "venue_id": item.venue_id,
    "venue_name": venue.name,
    "artist_id": item.artist_id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": item.start_time
  }
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    data = Venue.query.get(venue_id)
    data.past_shows =  map(lambda x:get_detail_show(x),db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()  )
    data.num_upcoming_shows = map(lambda x:get_detail_show(x),db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all())
    data.upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).count()
    data.past_shows_count = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).count()
    data.genres = eval(data.genres)
  except:
    return render_template('errors/404.html')
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error,phone,pattern = False,request.form['phone'],re.compile("\d{3}[-]\d{3}[-]\d{4}$")
  if not pattern.match(phone):
    flash('Phone should respect format xxx-xxx-xxxx')
    return render_template('pages/home.html')
  try:
      name,city,state,address,phone,genres = request.form['name'],request.form['city'],request.form['state'],request.form['address'],request.form['phone'],[]
      genres.append(request.form['genres'])
      facebook_link,image_link,website_link,seeking_talent,seeking_description = request.form['facebook_link'],request.form['image_link'],request.form['website_link'],True if request.form.get('seeking_talent') else False,request.form['seeking_description']
      venue = Venue(name=name,city=city,state=state,phone=phone,address=address,genres=str(genres),facebook_link=facebook_link,image_link=image_link,website_link=website_link,seeking_talent=seeking_talent,seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info)
  finally:
      db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET','DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error,name =False, ''
  try:
      item = Venue.query.get(venue_id)
      name = item.name
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
      error=True
  finally:
      db.session.close()
  if error:
    flash('An error occurred. Venue ' + name + ' could not be deleted.')
  else:
    flash('Venue ' + name + ' was successfully deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.with_entities(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term,data=request.form.get('search_term', ''),[]
  items , items_count= Artist.query.with_entities(Artist.id,Artist.name).filter(Artist.name.ilike('%'+search_term+'%')).all(), Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).count()
  for item in items:
    data_item={
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows":db.session.query(Show).join(Artist).filter(Show.venue_id==item.id).count()
    }
    data.append(data_item)
  response={
    "count": items_count,
    "data": data
  }
  # print("data search artists",data)
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

def get_detail_artist_show(item):
  artist = Artist.query.get(item.artist_id)
  venue = Venue.query.get(item.venue_id)
  return {
    "venue_id": item.venue_id,
    "venue_name": venue.name,
    "artist_id": item.artist_id,
    "artist_name": artist.name,
    "venue_image_link": venue.image_link,
    "start_time": item.start_time
  }
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  try:
    data = Artist.query.get(artist_id)
    data.past_shows =  map(lambda x:get_detail_artist_show(x),db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()  )
    data.num_upcoming_shows = map(lambda x:get_detail_artist_show(x),db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all())
    data.upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).count()
    data.past_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).count()
    data.genres = eval(data.genres)
  except:
    return render_template('errors/404.html')
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    form.name.data,form.city.data ,form.state.data,form.phone.data = artist.name,artist.city,artist.state,artist.phone
    form.genres.data,form.facebook_link.data ,form.image_link.data,form.website_link.data = ",".join(eval(artist.genres)),artist.facebook_link,artist.image_link,artist.website_link
    form.seeking_description.data = artist.seeking_description
    form.seeking_venue.data = artist.seeking_venue
  except:
    return render_template('errors/404.html')
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  try:
    artist = Artist.query.get(artist_id)
    
    name,city,state,phone,genres = request.form.get('name',artist.name),request.form.get('city',artist.city),request.form.get('state',artist.state),request.form.get('phone',artist.phone),[]
    facebook_link,image_link,website_link = request.form.get('facebook_link',artist.facebook_link),request.form.get('image_link',artist.image_link),request.form.get('website_link',artist.website_link)
    seeking_venue,seeking_description =True if request.form.get('seeking_venue') else False, request.form.get('seeking_description')
    genres.append(request.form.get('genres')) if request.form.get('genres') else genres
    
    artist.name=name
    artist.city=city
    artist.state=state
    artist.phone=phone
    artist.genres=str(genres) if len(genres)>0 else artist.genres
    artist.facebook_link=facebook_link
    artist.image_link=image_link
    artist.website_link=website_link
    artist.seeking_venue=seeking_venue
    artist.seeking_description=seeking_description
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    # flash('An error occurred. Artist ' + artist.name + ' could not be updated.')
    flash('An error occurred. Item could not be updated.')
  else:
    flash('Artist was successfully updated!')
  # print("ERROR", error)
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    form.name.data,form.city.data ,form.state.data,form.address.data,form.phone.data = venue.name,venue.city,venue.state,venue.address,venue.phone
    form.genres.data,form.facebook_link.data ,form.image_link.data,form.website_link.data = ",".join(eval(venue.genres)),venue.facebook_link,venue.image_link,venue.website_link
    form.seeking_description.data = venue.seeking_description
    form.seeking_talent.data = venue.seeking_talent
  except:
    flash('An error occurred. Item could not be edited.')
    return render_template('errors/404.html')
 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  try:
    venue = Venue.query.get(venue_id)
    
    name,city,state,phone,genres = request.form.get('name',venue.name),request.form.get('city',venue.city),request.form.get('state',venue.state),request.form.get('phone',venue.phone),[]
    facebook_link,image_link,website_link = request.form.get('facebook_link',venue.facebook_link),request.form.get('image_link',venue.image_link),request.form.get('website_link',venue.website_link)
    seeking_talent,seeking_description =True if  request.form.get('seeking_talent') else False,request.form.get('seeking_description',venue.seeking_description)
    address = request.form.get('address',venue.address)
    genres.append(request.form.get('genres')) if request.form.get('genres') else genres
    venue.name=name
    venue.city=city
    venue.state=state
    venue.state=address
    venue.phone=phone
    venue.genres=str(genres) if len(genres)>0 else venue.genres
    venue.facebook_link=facebook_link
    venue.image_link=image_link
    venue.website_link=website_link
    venue.seeking_talent=seeking_talent
    venue.seeking_description=seeking_description
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Item could not be updated.')
  else:
    flash('Venue was successfully updated!')
  
  print("error",error)

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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error,phone,pattern = False,request.form['phone'],re.compile("\d{3}[-]\d{3}[-]\d{4}$")
  if not pattern.match(phone):
    flash('Phone should respect format xxx-xxx-xxxx')
    return render_template('pages/home.html')
  try:
    name,city,state,phone,genres = request.form['name'],request.form['city'],request.form['state'],request.form['phone'],[]
    genres.append(request.form['genres'])
    facebook_link,image_link,website_link,seeking_venue,seeking_description = request.form['facebook_link'],request.form['image_link'],request.form['website_link'],True if request.form.get('seeking_venue') else False,request.form['seeking_description']
    artist = Artist(name=name,city=city,state=state,phone=phone,genres=str(genres),facebook_link=facebook_link,image_link=image_link,website_link=website_link,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info)
  finally:
      db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # print("error",error)
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = map(lambda x:get_detail_show(x), Show.query.all())
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
      artist_id,venue_id = request.form['artist_id'],request.form['venue_id']
      show = Show(artist_id=artist_id,venue_id=venue_id)
      db.session.add(show)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info)
  finally:
      db.session.close()
  if error:
    flash('An error occurred. Your show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
