# /app/mod-auth/auth.py

"""
Authentication handlers for the restaurant menu application.
"""

from flask import make_response
from flask import flash
from flask import redirect
from flask import url_for

import json
import httplib2
import requests

from .userhandlers import *


# Load Google OAuth client information.
CLIENT_ID = json.loads(
    open('secrets/client_secrets.json', 'r').read())['web']['client_id']


def fbauth(request, login_session):
    """
    Takes request object and login session as input.
    Exchanges the short term
    access token for the long term access token. Uses that
    token to access user information.
    Outputs a response object, either error or success.
    """

    # Validate state token.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token and app information.
    access_token = request.data
    print "access token received %s" % access_token
    app_id = json.loads(open('fb_client_secrets.json',
                             'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json',
                                 'r').read())['web']['app_secret']

    # Exchange token and client info long-term token
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=' +
           'fb_exchange_token&client_id=' +
           '%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Extract token from result
    token = result.split(',')[0].split(':')[1].replace('"', '')

    # Use token to get user info from API
    userinfo_url = ('https://graph.facebook.com/v2.8/me?access_token=' +
                    '%s&fields=name,id,email' % token)
    result = h.request(userinfo_url, 'GET')[1]
    data = json.loads(result)

    # Get user picture from Facebook
    pic_url = ('https://graph.facebook.com/v2.8/' +
               '%s/picture?redirect=0&height=200&width=200' % data["id"])
    result = h.request(pic_url, 'GET')[1]
    pic_data = json.loads(result)

    # Store everything in the login session.
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['picture'] = pic_data["data"]["url"]

    # Check if user is currently in database
    user_id = getUserID(login_session['email'])

    # If user is not in database, add user.
    if user_id is None:
        user_id = createUser(login_session)

    # Store user id in login session.
    login_session['user_id'] = user_id

    # Send response to ajax
    response = make_response(json.dumps('Login successful'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


def gauth(request, login_session):
    """
    Takes request object and login session as inputs
    Validates state token and exchanges access token for
    user information.
    Outputs an error if one occurs, or a successful login mesage.
    """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    id_token = request.data
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=%s'
           % id_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store gplus id from result
    gplus_id = result['sub']

    # Verify valid access token
    if result['aud'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Access token is good. Check if user is already logged in.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Login successful. Store access token for later use.
    login_session['access_token'] = id_token

    # Store user information in login_session.
    login_session['provider'] = 'google'
    login_session['gplus_id'] = result['sub']
    login_session['username'] = result['given_name']
    login_session['picture'] = result['picture']
    login_session['email'] = result['email']

    # Check if user is currently in database
    user_id = getUserID(login_session['email'])

    # If user is not in database, add user.
    if user_id is None:
        user_id = createUser(login_session)

    # Store user id in login session.
    login_session['user_id'] = user_id

    # Send response to ajax
    response = make_response(json.dumps('Login successful'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


def clearSession(login_session):
    """
    Takes no inputs.
    Checks which provider user is logged in with and processes
    disconnection accordingly.
    Clears user info from login_session.
    Returns a redirect response object and flash message
    """

    # Check that user is actually logged in
    if 'provider' in login_session:
        # Check for google login, disconnect from google if true
        if login_session['provider'] == 'google':
            gDisconnect(login_session)
            del login_session['gplus_id']

        # Check for facebook login, disconnect from facebook if true
        if login_session['provider'] == 'facebook':
            fbDisconnect(login_session)
            del login_session['facebook_id']

        # Clear user info from login_session
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash("You have successfully been logged out.")

        # Redirect user to landing page.
        return redirect(url_for('showRestaurants'))

    # User is not logged in -- redirect to landing page.
    else:
        flash("Logout failed -- you weren't logged in.")
        return redirect(url_for('showRestaurants'))


def fbDisconnect(login_session):
    """
    Takes no inputs
    Revokes Facebook access token
    Returns a response object on success
    """

    # Send access token revocation to Facebook
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    # Return a response object
    response = make_response(json.dumps('Successfully disconnected'), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


def gDisconnect(login_session):
    """
    Takes no inputs
    Checks if user was logged in with google and throws an error if not
    Returns a response object
    """

    # Check if user is actually connected
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user is not logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Sends the OK to ajax, triggering disconnection on client-side javascript.
    response = make_response(json.dumps('Successfully disconnected'), 200)
    response.headers['Content-Type'] = 'application/json'

    return response
