import httplib2
import json
import random
import string
import requests
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash
)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response


# Start to build a Flask application
app = Flask(__name__)

# Load client secrets information
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


# Connect to User Authorization
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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                    connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data.get('name', '')
    login_session['picture'] = data.get('picture', '')
    login_session['email'] = data.get('email', '')

    # See if a user exists, if it doesn't make a new one
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
    output += ' " style = "width: 300px; height: 300px; \
                border-radius: 150px;-webkit-border-radius: \
                150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])

    return output


# User Helper Function to create a new user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# User Helper Function to get the current user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# Direct to logout page
@app.route('/logout')
def showLogout():
    return redirect(url_for('gdisconnect'))


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():

    # Only disconnect a connected user.
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'

        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog information
@app.route('/catalog.json')
def CatalogJSON():
    catalogs = session.query(Catalog).all()
    items = session.query(Item).all()

    arr_dict = []
    for catalog in catalogs:
        dict = {}
        dict['id'] = catalog.id
        dict['name'] = catalog.name
        dict['Item'] = []

        for item in items:
            if catalog.id == item.catalog_id:
                dict_item = {}
                dict_item['cat_id'] = item.catalog_id
                dict_item['description'] = item.description
                dict_item['id'] = item.id
                dict_item['title'] = item.name

                dict['Item'].append(dict_item)

        arr_dict.append(dict)

    return jsonify(Catalogs=arr_dict)


# Show all current categories with the latest added items
@app.route('/')
def showCatalogs():

    # get categories
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))

    # get items
    items = session.query(Item).order_by(asc(Item.name))

    # show public page when the user is not logged in
    if 'username' not in login_session:
        return render_template('publicCatalogs.html', catalogs=catalogs,
                               items=items)

    return render_template('catalogs.html', catalogs=catalogs, items=items)


# Show items of selected category
@app.route('/catalog/<string:catalog_name>/items', methods=['GET', 'POST'])
def showItems(catalog_name):
    if 'username' not in login_session:
        return redirect('/login')

    # get the specified catalog
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()

    # get all items of the catalog
    items = session.query(Item).filter_by(catalog_id=catalog.id).all()

    return render_template('showitems.html', catalogs=catalogs, items=items)


# Show the description of selected item
@app.route('/catalog/<string:catalog_name>/<string:item_name>',
           methods=['GET', 'POST'])
def showItemDescription(catalog_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')

    # get the specified catalog
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()

    # get the specified item to show its information later
    item = session.query(Item).filter_by(name=item_name).one()

    return render_template('showitemdesc.html', catalog=catalog, item=item)


# Create a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')

    catalogs = session.query(Catalog).order_by(asc(Catalog.name))

    if request.method == 'POST':

        # get item infomration from the request form
        name = request.form['name']
        category = request.form['category']
        catalog = session.query(Catalog).filter_by(name=category).one()
        user_id = getUserID(login_session['email'])

        # create a new item according to the given information
        newItem = Item(name=name, description=request.form
                       ['description'], catalog_id=catalog.id, user_id=user_id)
        session.add(newItem)
        session.commit()

        # show create status to the page
        flash('New Item %s Successfully Created' % (newItem.name))

        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newItem.html', catalogs=catalogs)


# Edit a menu item
@app.route('/Catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')

    # get the item to be edited
    item_edite = session.query(Item).filter_by(name=item_name).one()

    # get the specified catalog
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    catalog = session.query(Catalog).filter_by(id=item_edite.catalog_id).one()

    # check whether the user has the authorization to make modification
    user_id = item_edite.user_id
    user_id_now = getUserID(login_session['email'])

    if user_id != user_id_now:
        flash("This Item Is Created By Another User \
              You Don't Have The Right To Modify.")
        return render_template('edititem.html', catalogs=catalogs,
                               item=item_edite)

    # update the specified item
    if request.method == 'POST':
        if request.form['name']:
            item_edite.name = request.form['name']
        if request.form['description']:
            item_edite.description = request.form['description']
        if request.form['category']:
            category = request.form['category']
            catalog = session.query(Catalog).filter_by(name=category).one()
            item_edite.catalog_id = catalog.id

        items = session.query(Item).order_by(asc(Item.name))
        session.add(item_edite)
        session.commit()
        flash('Item Successfully Edited')

        return render_template('catalogs.html', catalogs=catalogs, items=items)
    else:
        return render_template('edititem.html', catalogs=catalogs,
                               item=item_edite)


# Delete a menu item
@app.route('/Catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')

    # get the item to be deleted
    item_delete = session.query(Item).filter_by(name=item_name).one()

    # check whether the user has the authorization to make modification
    user_id = item_delete.user_id
    user_id_now = getUserID(login_session['email'])

    if user_id != user_id_now:
        flash("This Item Is Created By Another User. \
              You Don't Have The Right To Delete")
        return render_template('deleteItem.html', item=item_delete)

    # delete the specified item
    if request.method == 'POST':
        session.delete(item_delete)
        session.commit()
        flash('Menu Item Successfully Deleted')

        # get categories
        catalogs = session.query(Catalog).order_by(asc(Catalog.name))

        # get items
        items = session.query(Item).order_by(asc(Item.name))

        return render_template('catalogs.html', catalogs=catalogs, items=items)
    else:
        return render_template('deleteItem.html', item=item_delete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
