import random
import string


def makeState(login_session):
	"""
	Takes a login_session as input.
	Generates a state token and saves it to the login session.
	Outputs a state token.
	"""
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
	login_session['state'] = state

	return state