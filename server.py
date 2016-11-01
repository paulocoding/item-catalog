from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# db setup
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# app setup
app = Flask(__name__)
app.secret_key = 'secretive_k3y'

# client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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


def is_user_logged():
    return 'username' in login_session


def current_user():
    return login_session.get('user_id')


# Routes
# Show Home page
@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).order_by(Category.name).all()
    items = session.query(Item).order_by(Item.name).all()
    return render_template('catalog.html', categories=categories, items=items, logged=is_user_logged())

# Login
@app.route('/login')
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# gconnect
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_id = getUserID(data['email'])
    if not user_id:
        # new user
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

@app.route('/clearSession')
def clearSession():
    login_session.clear()
    return "Session cleared"

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    # debug code
    # print 'In gdisconnect access token is %s', access_token
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # debug code
    # print 'User name is: '
    # print login_session.get('username')
    # print 'user-id : %s' % login_session['gplus_id']
    # print 'email : %s' % login_session['email']
    # print 'picture : %s' % login_session['picture']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # debug code
    # print 'result is '
    # print result
    if result['status'] == '200':
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
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Categories CRUD
# New Category
@app.route('/catalog/category/new', methods=['GET', 'POST'])
def newCategory():
    # checking if user is logged in:
    if not is_user_logged():
        return redirect(url_for('showLogin'))
    if request.method == 'GET':
        return render_template('new_category.html')
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_category = Category(name=name, description=description, user_id=login_session['user_id'])
        session.add(new_category)
        session.commit()
        flash('New Category created: %s' % name)
        return redirect(url_for('showCatalog'))

# Show Category
@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        items = session.query(Item).filter_by(category_id=selected_category.id).order_by(Item.name).all()
        return render_template('category.html', category=selected_category, items=items, user_id=current_user(), logged=is_user_logged())
    return render_template('404.html')

# Edit Category
@app.route('/catalog/<string:category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    # checking if user is logged in:
    if not is_user_logged():
        return redirect(url_for('showLogin'))
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        # checking if current user is the author:
        if current_user() != selected_category.user_id:
            return redirect(url_for('showCategory', category_name=category_name))
        if request.method == 'GET':
            return render_template('edit_category.html', category=selected_category)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            selected_category.name = name
            selected_category.description = description
            session.add(selected_category)
            session.commit()
            flash('%s Category edited!' % name)
            return redirect(url_for('showCategory', category_name=name))
    return render_template('404.html')

# Delete Category
@app.route('/catalog/<string:category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    # checking if user is logged in:
    if not is_user_logged():
        return redirect(url_for('showLogin'))
    selected_category = session.query(Category).filter_by(name=category_name).first()
    if selected_category:
        # checking if current user is the author:
        if current_user() != selected_category.user_id:
            return redirect(url_for('showCategory', category_name=category_name))
        if request.method == 'GET':
            return render_template('delete_category.html', category=selected_category)
        if request.method == 'POST':
            session.delete(selected_category)
            session.commit()
            flash('%s Category deleted!' % selected_category.name)
            return redirect(url_for('showCatalog'))
    return render_template('404.html')


# Items CRUD
# New Item
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    # checking if user is logged in:
    if not is_user_logged():
        return redirect(url_for('showLogin'))
    if request.method == 'GET':
        categories = session.query(Category).order_by(Category.name).all()
        return render_template('new_item.html', categories=categories)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category_id = request.form['category']
        quantity = request.form['quantity']
        new_item = Item(name=name,
                        description=description,
                        quantity=quantity,
                        category_id=category_id,
                        user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('New Item created: %s' % name)
        return redirect(url_for('showItem', category_name=new_item.category.name, item_name=name))

# Show Item
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    selected_category = session.query(Category).filter_by(name=category_name).first()
    selected_item = session.query(Item).filter_by(name=item_name).first()
    if selected_category and selected_item:
        return render_template('item.html', category=selected_category, item=selected_item, user_id=current_user())
    return render_template('404.html')

# Edit Item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    # checking if user is logged in:
    if not is_user_logged():
        return redirect(url_for('showLogin'))
    categories = session.query(Category).order_by(Category.name).all()
    selected_item = session.query(Item).filter_by(name=item_name).first()
    if selected_item:
        # checking if current user is the author:
        if current_user() != selected_item.user_id:
            return redirect(url_for('showItem', category_name=category_name, item_name=item_name))
        if request.method == 'GET':
            return render_template('edit_item.html', categories=categories, item=selected_item)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category_id = request.form['category']
            quantity = request.form['quantity']
            selected_item.name = name
            selected_item.description = description
            selected_item.category_id = category_id
            selected_item.quantity = quantity
            session.add(selected_item)
            flash('%s Item edited!' % name)
            session.commit()
            return redirect(url_for('showItem', category_name=selected_item.category.name, item_name=name))
    return render_template('404.html')

# Delete Item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    # checking if user is logged in:
    if not is_user_logged():
        return redirect(url_for('showLogin'))
    selected_category = session.query(Category).filter_by(name=category_name).first()
    selected_item = session.query(Item).filter_by(name=item_name).first()
    if selected_category and selected_item:
        # checking if current user is the author:
        if current_user() != selected_item.user_id:
            return redirect(url_for('showItem', category_name=category_name, item_name=item_name))
        if request.method == 'GET':
            return render_template('delete_item.html', category=selected_category, item=selected_item)
        if request.method == 'POST':
            session.delete(selected_item)
            session.commit()
            flash('%s Item deleted!' % item_name)
            return redirect(url_for('showCatalog'))
    return render_template('404.html')


# JSON endpoints

# All items JSON
@app.route('/catalog/JSON')
def showItemsJSON():
    all_items = session.query(Item).all()
    return jsonify({'catalog': [item.serialize for item in all_items]})

# Categories JSON
@app.route('/catalog/category/JSON')
def showCategoriesJSON():
    all_categories = session.query(Category).all()
    return jsonify({'Categories': [cat.serialize for cat in all_categories]})

# Category JSON
@app.route('/catalog/<string:category_name>/JSON')
def showCategoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    if category:
        items = session.query(Item).filter_by(category_id=category.id).all()
        return jsonify({category.name: [item.serialize for item in items]})

# Item JSON
@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def showItemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).first()
    item = session.query(Item).filter_by(name=item_name).first()
    if category and item:
        return jsonify({'Item': item.serialize})


# Run app if run as script:
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
