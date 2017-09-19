# /app/mod-auth/userhandlers.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User
from database_setup import Base


engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# User Helper functions:
def createUser(login_session):
    """
    Takes login_session (dict) as input
    Uses information in the login_session to add a new user to the
    User database.
    Gets newly added user from the database.
    Outputs the user ID
    """

    # Create new user based on login sesssion information
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()

    # Gets newly added user from the database
    user = session.query(User).filter_by(email=login_session['email']).one()

    # Returns user ID
    return user.id


def getUserInfo(user_id):
    """
    Takes user ID (int) as input
    Gets user by ID
    Outputs user object
    """

    # Get user by ID and return
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    Takes user email (str) as input.
    If user is in the database, outputs user id.
    If not, outputs None.
    """

    try:
        # Get user from database by email and return user id
        user = session.query(User).filter_by(
            email=email).one()
        return user.id
    except:
        # User not found. Return none.
        return None
