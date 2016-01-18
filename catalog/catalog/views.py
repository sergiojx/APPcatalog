import sys
from catalog import app, csrf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from sqlalchemy.sql import select
import urlparse
# library for XML content dispatching
from dicttoxml import dicttoxml

from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
# This works like a dictionary. We can store values in it for the longevity of
# a user's session with our server
from flask import session as login_session
# Used for creating pseudo-random string. This will identify each session.
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# from datetime import datetime,date
import datetime
import catalogdbi as dbi
import forms

# required for decorators
from functools import wraps

# optain cliente_id from web structure
CLIENT_ID = json.loads(open('/var/www/catalog/client_secret.json', 'r').read())['web']['client_id']


# Decorator for credetial checkup when gdesconnect is conjured
def credentialCheckUp(something):
    @wraps(something)
    def wrap(*args, **kwargs):
        credentials = login_session.get('credentials')
        if credentials is None:
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return something(*args, **kwargs)
    return wrap


# Decorator for credetial and userid match checkup when item handling
# function is conjured up
def credentialUserMathcCheckUp(something):
    @wraps(something)
    def wrap(*args, **kwargs):
        credentials = login_session.get('credentials')
        user_id = kwargs['user_id']
        if credentials is None:
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            if user_id != login_session['user_id']:
                response = make_response(
                    json.dumps("Request User ID does not "
                               "match with current user."), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
        return something(*args, **kwargs)
    return wrap


@app.route('/', methods=['GET'])
@app.route('/index/', methods=['GET'])
@app.route('/home/', methods=['GET'])
def index():
    if request.method == 'GET':
        # Optain a catalog list and a last 10 added item list
        catLst = dbi.getAllCategory()
        recentItemLst = dbi.getRecetItems(10)
        username = None
        useremail = None
        userid = None
        # Check for current logrd user
        credentials = login_session.get('credentials')
        if credentials is not None:
            username = login_session['username']
            useremail = login_session['email']
            userid = login_session['user_id']
        return render_template('nonloghome.html',
                               catLst=catLst,
                               recentItemLst=recentItemLst,
                               username=username,
                               useremail=useremail,
                               userid=userid)
                         

# optain recent added items


@app.route('/recent/item/JSON/')
def recentItemJSON():
    recentItemLst = dbi.getRecetItems(10)
    return jsonify(resentItems=[i.serialize for i in recentItemLst])

# Create a state token to prevent request forgery.
# Store it in the session for later validation.


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" %login_session['state']
    return render_template('login.html', STATE=state)

'''
This implementation works with:
     pip install werkzeug==0.8.3
     pip install flask==0.9
     pip install Flask-Login==0.1.3

Go to the GoogleDevConsole> API & Auth> Credentials>Select
your app> Authorized Redirect URIs and add the following
URIS: http://localhost:8000/login and http://localhost:8000/gconnect.
You may have to change the port number depending on the
port number you have set your app to run on.
'''


@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        print "Request Sate: " + request.args.get('state')
        print "session State: " + login_session['state']
        print "STATE DOES NOT MATCH!!!!!"
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code(client one time code)
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # credentials:Google response
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        # something went wrong
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # credentials were optained from Google
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # this is a valid token for use
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

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    # login_session['credentials'] = credentials
    '''
        just access_token is stored in order to prevent
        <oauth2client.client.OAuth2Credentials object at 0x103c827d0>
        is not JSON serializable
        error
    '''
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it does not creata a new one

    user_id = dbi.getUserID(login_session['email'])
    if not user_id:
        user_id = dbi.createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
@credentialCheckUp
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    # access_token = credentials.access_token
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    try:
        result = h.request(url, 'GET')[0]
    except:
        # something went wrong
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(
            json.dumps("No Inthernet conection. User's session "
                       "has been initialiazed"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        '''
          response = make_response(json.dumps("Successfully "
                                              "disconnected."),
                                              200)
          response.headers['Content-Type'] = 'application/json'
          return response
        '''
        return redirect(url_for('index'))
    else:
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Get associated category item JSON list
@app.route('/category/<int:category_id>/itemlst/JSON/', methods=['GET'])
def catyItemLst(category_id):
    itemLst = dbi.getItemLstByCategoryId(category_id)
    return jsonify(categoryItemLst=[i.serialize for i in itemLst])


# return specific Item information page
@app.route('/item/<int:item_id>/info/', methods=['GET'])
def getItemInfo(item_id):
    if request.method == 'GET':
        # Optain a catalog list and a last 10 added item list
        item = dbi.getItemById(item_id)
        username = None
        useremail = None
        userid = None
        # Check for current logrd user
        credentials = login_session.get('credentials')
        if credentials is not None:
            username = login_session['username']
            useremail = login_session['email']
            userid = login_session['user_id']
        '''
          currently loged user id and item's user id are passed.
          This way conditional render of Delete and Edit options
          are performed.
        '''
        return render_template('iteminfo.html',
                               item=item,
                               username=username,
                               useremail=useremail,
                               userid=userid)


# New Item
@app.route('/newitem/<int:user_id>/', methods=['GET', 'POST'])
@credentialUserMathcCheckUp
def newItem(user_id):
    credentials = login_session.get('credentials')
    if request.method == 'GET':
        categorylst = dbi.getAllCategory()
        categorySelect_choices = [
            (int(
                category.id), str(
                category.name)) for category in categorylst]
        newItemFrm = forms.NewItem(request.form)
        newItemFrm.categorySelect.choices = categorySelect_choices
        newItemFrm.categorySelect.choices.insert(0, ("0", "None"))
        newItemFrm.user_id = user_id
        return render_template(
            'newitem.html',
            newItemForm=newItemFrm,
            username=login_session['username'])
    else:
        # SelectField  choices have to be filled in with current select list
        # before validating!!!
        categorylst = dbi.getAllCategory()
        categorySelect_choices = [
            (int(
                category.id), str(
                category.name)) for category in categorylst]
        newItemFrm = forms.NewItem(request.form)
        newItemFrm.categorySelect.choices = categorySelect_choices
        newItemFrm.categorySelect.choices.insert(0, ("0", "None"))
        if newItemFrm.validate():
            print "New Item Validation OK"
            iuser = dbi.getUserById(user_id)
            icaty = dbi.getCategoryById(request.form['categorySelect'])
            creation = datetime.date.today()
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           imageurl=request.form['imageurl'],
                           cuser=iuser,
                           creation=creation,
                           category=icaty)
            dbi.addNewItem(newItem)
            flash("Item has been added!!!")
            # print 'name'
            # print request.form['name']
            # print 'description'
            # print request.form['description']
            print 'imageurl'
            print request.form['imageurl']
            print 'categorySelect'
            print request.form['categorySelect']
        else:
            print "New Item Validation Failed"
            print 'name'
            print newItemFrm.name.errors
            print 'description'
            print newItemFrm.description.errors
            print 'imageurl'
            print newItemFrm.imageurl.errors
            print 'categorySelect'
            print newItemFrm.categorySelect.errors
            flash("Something has gone wrong with submitted data")
        return redirect(url_for('index'))


# Delete Item
@app.route('/delitem/<int:user_id>/<int:item_id>/', methods=['POST'])
@credentialUserMathcCheckUp
def deleteItem(user_id, item_id):
    credentials = login_session.get('credentials')
    delItem = dbi.getItemById(item_id)
    if delItem.user_id != user_id:
        response = make_response(
            json.dumps("Requested Item does not belong to current user."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    dbi.removeItemById(item_id)
    flash("Item has been removed!!!")
    return redirect(url_for('index'))

'''
 Edit Item:
 It is verified that login_session.get holds a valid user data.
 It is verified that request user id matches current logged user id
 It is verified that item's user id matches request's user id
'''


@app.route('/edititem/<int:user_id>/<int:item_id>/', methods=['GET', 'POST'])
@credentialUserMathcCheckUp
def editItem(user_id, item_id):
    credentials = login_session.get('credentials')
    oldItem = dbi.getItemById(item_id)
    if oldItem.user_id != user_id:
        response = make_response(
            json.dumps("Requested Item does not belong to current user."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if request.method == 'GET':
        categorylst = dbi.getAllCategory()
        categorySelect_choices = [
            (int(
                category.id), str(
                category.name)) for category in categorylst]
        oldItemFrm = forms.NewItem(request.form)
        oldItemFrm.name.data = oldItem.name
        oldItemFrm.description.data = oldItem.description
        oldItemFrm.imageurl.data = oldItem.imageurl
        oldItemFrm.categorySelect.choices = categorySelect_choices
        oldItemFrm.categorySelect.choices.insert(0, ("0", "None"))
        oldItemFrm.categorySelect.data = oldItem.category_id
        oldItemFrm.user_id = user_id
        return render_template(
            'edititem.html',
            newItemForm=oldItemFrm,
            username=login_session['username'],
            oldItem=oldItem)
    else:
        # SelectField  choices have to be filled in with current select list
        # before validating!!!
        categorylst = dbi.getAllCategory()
        categorySelect_choices = [
            (int(
                category.id), str(
                category.name)) for category in categorylst]
        newItemFrm = forms.NewItem(request.form)
        newItemFrm.categorySelect.choices = categorySelect_choices
        newItemFrm.categorySelect.choices.insert(0, ("0", "None"))
        if newItemFrm.validate():
            print "Edited Item Validation OK"

            dbi.updateItemById(item_id=item_id,
                               new_name=request.form['name'],
                               new_description=request.form['description'],
                               new_imgURL=request.form['imageurl'],
                               new_category_id=request.form['categorySelect'])

            flash("Item has been edited!!!")
        else:
            print "Edited Item Validation Failed"
            flash("Something has gone wrong with submitted data")
        return redirect(url_for('index'))


# Catalog JSON list enpoint
@app.route('/catalog/JSON/', methods=['GET'])
def catalogJSON():
    categorylst = dbi.getAllCategory()
    return jsonify(Category=[i.serialize for i in categorylst])

# Catalog XML list endpoint


@app.route('/catalog/XML/', methods=['GET'])
def catalogXML():
    categorylst = dbi.getAllCategory()
    dicjson = [i.serialize for i in categorylst]
    dicjsonStr = json.dumps(dicjson)
    xml = dicttoxml(json.loads(dicjsonStr), custom_root='EmbeddedWorldCatalog')
    response = make_response(xml, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response


# New Category. Not yet implemented
@app.route('/newcategory/<int:user_id>/', methods=['GET', 'POST'])
def newCategory(user_id):
    return redirect(url_for('index'))

