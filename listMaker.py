from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from sqlalchemy import create_engine, asc, and_
from sqlalchemy.orm import sessionmaker
from database_setup2 import Base, User, ToDoList, Item

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import urllib2
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "List Maker App"

engine = create_engine('sqlite:///toDoListMaker2.db')
Base.metadata.bind = engine
# create session
DBSession = sessionmaker(bind=engine)
session = DBSession()
session.commit()


# login page
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    ## return "The current session state is %s" %login_session['state']
    return render_template('login.html', STATE = state)

# sign-in to app using google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    login_session['access_token'] = credentials.access_token

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_id = getUserID(login_session['email'])
    if not user_id:
    	user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None       

# Disconnect form google login 
@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] in ('200', '400'):
        print login_session
        del login_session['credentials']
        del login_session['state']
        del login_session['_flashes']
    	del login_session['access_token'] 
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
        return redirect('/login')
    else:
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# Check to see if user is logged in and if not, redirect to google login page
def checkLogin():
    if 'username' not in login_session:
        return redirect('/login')

# JSON endpoint for all lists per user
@app.route('/JSON')
def viewAllJSON():
    checkLogin()
    user_id = login_session['user_id']
    all_lists = session.query(ToDoList).filter_by(user_id=user_id).all()
    return jsonify(viewList=[i.serialize for i in all_lists])

# JSON endpoint for all lists per user
@app.route('/my-list/<int:list_id>/JSON')
def viewListJSON(list_id):
    checkLogin()
    user_id = login_session['user_id']
    all_lists = session.query(ToDoList).all()
    l = session.query(ToDoList).get(list_id)
    items = session.query(Item).filter_by(list_id = list_id)
    return jsonify(viewList=[i.serialize for i in all_lists],viewlistItems=[i.serialize for i in items])

# view all lists for user who is signed in
@app.route('/', methods=['GET','POST'])
def viewAll():
    checkLogin()
    user_id = login_session['user_id']
    all_lists = session.query(ToDoList).filter_by(user_id=user_id)
    return render_template('all_lists.html', all_lists = all_lists)

@app.route('/my-list/<int:list_id>/', methods=['GET','POST'])
def viewList(list_id):
    checkLogin()
    user_id = login_session['user_id']
    try:
        l = session.query(ToDoList).filter_by(id=list_id,user_id=user_id).one()
        items = session.query(Item).filter_by(list_id=list_id)
        return render_template('view_list.html', list_id = list_id, l = l, items = items)
    except:
        return render_template('list_not_found.html')

@app.route('/my-list/new/', methods=['GET','POST'])
def newList():
    checkLogin()
    if request.method=='POST':
    	newList = ToDoList(
    		title = request.form['title'],
    		description = request.form['description'],
    		user_id=login_session['user_id'])
    	session.add(newList)
    	session.commit()
    	return redirect(url_for('viewAll'))
    else:
    	return render_template('new_list.html')

@app.route('/my-list/<int:list_id>/edit/', methods=['GET','POST'])
def editList(list_id):
    checkLogin()
    user_id = login_session['user_id']
    try:
        l = session.query(ToDoList).filter_by(id=list_id,user_id=user_id).one()
        if request.method =='POST':
            l.title = request.form['title']
            l.description = request.form['description']
            session.add(l)
            session.commit()
            return redirect(url_for('viewList', list_id = list_id))
        else:
            return render_template('edit_list.html', l = l, list_id = list_id)
    except:
        return render_template('list_not_found.html')

@app.route('/my-list/<int:list_id>/delete/', methods=['GET','POST'])
def deleteList(list_id):
    checkLogin()
    user_id = login_session['user_id']
    try:
        l = session.query(ToDoList).filter_by(id=list_id,user_id=user_id).one()
        items = session.query(Item).filter_by(user_id=user_id, list_id=list_id).all() 
        if request.method=='POST':
            session.delete(l)
            for i in items:
                session.delete(i)
            session.commit()
            return redirect(url_for('viewAll', list_id = list_id))
        else:
        	return render_template('delete_list.html', list_id = list_id, l = l)
    except:
        return render_template('list_not_found.html')

@app.route('/my-list/<int:list_id>/new-item/', methods=['GET', 'POST'])
def newItem(list_id):
    checkLogin()
    user_id = login_session['user_id']
    try:
        l = session.query(ToDoList).filter_by(id=list_id,user_id=user_id).one()
        if request.method=='POST':
        	newItem = Item(name = request.form['name'],list_id=list_id,user_id=user_id)
        	session.add(newItem)
        	session.commit()
        	return redirect(url_for('viewList', list_id=list_id))
        else:
        	return render_template('new_item.html', list_id=list_id)
    except:
        return render_template('list_not_found.html')

@app.route('/my-list/<int:list_id>/item/<int:item_id>/edit-item/', methods=['GET','POST'])
def editItem(item_id, list_id):
    checkLogin()
    user_id = login_session['user_id']
    try:
        i = session.query(Item).filter_by(id=item_id,user_id=user_id, list_id=list_id).one()
        if request.method=='POST':
        	i.name = request.form['name']
        	session.add(i)
        	session.commit()
        	return redirect(url_for('viewList', list_id=list_id))
        else:
        	return render_template('edit_item.html', item_id=item_id, list_id=list_id, i=i)
    except:
        return render_template('list_not_found.html')

@app.route('/my-list/<int:list_id>/item/<int:item_id>/delete-item/', methods=['GET','POST'])
def deleteItem(item_id, list_id):
    checkLogin()
    user_id = login_session['user_id']
    try:
        i = session.query(Item).filter_by(id=item_id,user_id=user_id, list_id=list_id).one()
        if request.method=='POST':
        	session.delete(i)
        	return redirect(url_for('viewList', list_id=list_id))
        else:
        	return render_template('delete_item.html', list_id=list_id, item_id=item_id)
    except:
        return render_template('list_not_found.html')

if __name__ == '__main__':
	app.debug = True
	app.secret_key = 'LGNeRcJmj0xlhV1hKh1XVyXn'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.run(host = '0.0.0.0', port = 5000)