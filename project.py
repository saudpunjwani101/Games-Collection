from flask import Flask, render_template, request, url_for, redirect, flash
from flask import session as login_session
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask.ext.bcrypt import Bcrypt
from werkzeug import secure_filename
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.sql import func
import sys
import os
from sqlalchemy.orm import sessionmaker
from games_database import Base, Console, Game, User, UserPhoto, GamePhoto


#Connecting to the database using session
engine = create_engine('sqlite:///gamescollection.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#naming flask app
app = Flask(__name__)
bcrypt = Bcrypt(app) #initializing the bycrpt object

#setting and configure the flask-uploads
photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST']='static/uploaded' #destination for uploaded user photos
configure_uploads(app, photos)


#route for login
@app.route('/login', methods=['Get', 'Post'])
def login():
	if request.method=='POST':
		username = request.form['username'].lower()
		user_password = request.form['password']
		
		#checking the login credencials
		user = session.query(User).filter_by(username=username).first()
	
		if user is None:
			flash('Username or password is invalid')
			return redirect(url_for('login'))

		if bcrypt.check_password_hash(user.password, user_password): #compare hash passwords
			login_session['username'] = request.form['username']
			return redirect(url_for('Consoles'))
	
	else:
		return render_template('login.html')

#logout route 
@app.route('/logout')
def logout():
		login_session.pop('username', None)
		return redirect(url_for('login'))


#Root route and Registration route
@app.route('/')
@app.route('/registration', methods=['Get', 'Post'])
def registration():
	if request.method=='POST':
		username = request.form['username'].lower()
		user_password = request.form['password']
		confirm_pass = request.form['confirm']

		#Querying whether the user already exists in the database
		user = session.query(User).filter_by(username=username).first()
		
		#Registration Form validation
		if user is None:
			if int(len(username))<3:
				flash("username must be greater than 3 characters")
				return redirect(url_for('registration'))

			if (' ' in username)==True:
				flash("Spaces are not allowed in usernames")
				return redirect(url_for('registration'))
			
			if user_password!=confirm_pass:
				flash("passwords do not match")
				return redirect(url_for('registration'))
			
			if int(len(user_password))<6 and int(len(user_password))<6:
				flash("password must be greater than 6 characters")
				return redirect(url_for('registration'))

			#Adding the user to the database and hashing the password			
			user = User(username=username,
						password=bcrypt.generate_password_hash(user_password))

			session.add(user)
			session.commit()
			return redirect(url_for('Consoles'))
		else:
			flash("Username already taken!")
			return redirect(url_for('registration'))
	else:
		return render_template('registration.html')

#route for user image upload
@app.route('/uploadphoto', methods=['GET', 'POST'])
def uploadUserImage():

	if request.method=='POST' and 'photo' in request.files:
		filename = photos.save(request.files['photo'])
		rec = UserPhoto(filename=filename, user_name=login_session['username'])
		session.add(rec)
		session.commit()
		flash('photo uploaded')
		return redirect(url_for('Consoles'))

	return render_template('upload.html')


#Main page route
@app.route('/consoles')
def Consoles():
	if 'username' not in login_session:
		flash("login required")
		return redirect(url_for('login'))

	consoles = session.query(Console).filter_by(user_name=login_session['username'])
	

	#Querying the photo by username
	if session.query(UserPhoto).order_by(UserPhoto.id).first():
		photoo = session.query(UserPhoto).order_by(UserPhoto.id.desc()).first()
		if not photoo:
			print "Photo not found!"
		url = photos.url(photoo.filename)
		print "photo found!" + url
		return render_template('consoles.html', url=url, 
												photo=photoo, 
												consoles=consoles, 
												login=login_session)

	return render_template('consoles.html', consoles=consoles, 
											login=login_session)
	
#route for creating a new console
@app.route('/newconsole', methods=['Get', 'Post'])
def newConsole():
	if 'username' not in login_session:
		return redirect(url_for('login'))

	if request.method=='POST':
		name = request.form['name']
		company = request.form['company']

		#Validation
		if not name:
			flash("Console must have a name")
			return redirect(url_for('newConsole'))

		if not company:
			flash("Console must have a company name")
			return redirect(url_for('newConsole'))

		#if all clear, add the console to the database
		else: 
			newOne = Console(name=name,
							company=company,
							user_name=login_session['username'])
			session.add(newOne)
			session.commit()
			return redirect(url_for('Consoles'))
	else: 
		return render_template('newconsole.html')

#route for deleting a console
@app.route('/deleteconsole/<int:console_id>/delete/', methods=['GET', 'POST'])
def deleteConsole(console_id):

	#Querying the console by it's id
	deleteOne = session.query(Console).filter_by(id=console_id).first()
	if request.method=='POST':
		session.delete(deleteOne)
		session.commit()
 		return redirect(url_for('Consoles'))
	
	else:
		return render_template('deleteconsole.html', i=deleteOne)

#Game list route
@app.route('/games/<int:console_id>/')
def Games(console_id):
	if 'username' not in login_session:
		flash("Login in required!")
		return redirect(url_for('login'))

	#Querying games with respect to their consoles
	console = session.query(Console).filter_by(id=console_id).one()
	games = session.query(Game).filter_by(console_id=console_id)

	return render_template('games.html', console=console, 
										games=games, 
										console_id=console_id,
										login=login_session)


#Creating new game route
@app.route('/newgame/<int:console_id>/new/', methods=['GET', 'POST'])
def newGame(console_id):

	if request.method=='POST':
		name=request.form['name']
		description=request.form['name']
		developed_by=request.form['developed_by']
		released_year=request.form['released_year']
		ratings=request.form['ratings']
		
		#Validation
		if not name:
			flash("Game must have name")
			return redirect(url_for('newGame', console_id=console_id))

		if not description:
			flash("Enter some description about the game")
			return redirect(url_for('newGame', console_id=console_id))

		if not ratings:
			flash("Give a game rating")

		#if all clear add the game to the database
		newOne = Game(name=request.form['name'], 
				description=request.form['description'],
				developed_by=request.form['developed_by'],
				released_year=request.form['released_year'],
				ratings=request.form['ratings'],
				console_id=console_id,
				user_name=login_session['username'])
		
		session.add(newOne)
		session.commit()	
		return redirect(url_for('Games', console_id=console_id, game_id=newOne.id))


	return render_template('newgame.html', console_id=console_id)


#details of game route
@app.route('/editgame/<int:console_id>/<int:game_id>/edit/')
def editGame(console_id, game_id):
	
	editOne = session.query(Game).filter_by(id=game_id).one()

	if session.query(GamePhoto).order_by(GamePhoto.id).first():
		photoo = session.query(GamePhoto).order_by(GamePhoto.id.desc()).first()
		if not photoo:
			print "Photo not found!"
		url = photos.url(photoo.filename)
		print "photo found!" + url
		return render_template('editgame.html', url=url, 
												photo=photoo,
												game_id=game_id,
												i=editOne,
												console_id=console_id)

	return render_template('editgame.html', console_id=console_id,
											game_id=game_id,
											i = editOne)


#route for uploading game poster
@app.route('/uploadgameimage/<int:console_id>/<int:game_id>/', methods=['GET', 'POST'])
def uploadGameImage(console_id, game_id):
	if request.method=='POST' and 'photo' in request.files:
		filename = photos.save(request.files['photo'])
		rec = GamePhoto(filename=filename, console_id=console_id, game_id=game_id)
		session.add(rec)
		session.commit()
		return redirect(url_for('editGame', console_id=console_id,
												game_id=game_id))

	return render_template('uploadgameimage.html', console_id=console_id,
														game_id=game_id)

#Deleting human route
@app.route('/deletegame/<int:console_id>/<int:game_id>/delete/', methods=['GET','POST'])
def deleteGame(console_id, game_id):
	deleteOne = session.query(Game).filter_by(id=game_id).one()
	if request.method=='POST':
		session.delete(deleteOne)
		session.commit()
		return redirect(url_for('Games', console_id=console_id))
	
	else: 
		return render_template('deletegame.html', i = deleteOne)

if __name__ == '__main__':
	app.debug = True
	app.secret_key = "asnnfnepnaoifnwienfijmsnsnonon"
	app.run(host = '0.0.0.0', port=8080)
