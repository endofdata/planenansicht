
# Actions in authentication area
LOGIN_ACTION = "login"
LOGOUT_ACTION = "logout"

# Actions in user management area
USER_API_AREA = "/user"
CHANGE_PASSWORD_ACTION = "change_password"
UPDATE_MASTER_ACTION = "update_master"

# Relative paths
ROOT_ENDPOINT ="/"
STATIC_ENDPOINT = "/static"
FAVICON_REQUEST = "/favicon.ico"

ROOT_ACTION = "list_tarps"

LOGIN_ENDPOINT = "/" + LOGIN_ACTION
LOGOUT_ENDPOINT = "/" + LOGOUT_ACTION
CHANGE_PASSWORD_ENDPOINT = USER_API_AREA + "/" + CHANGE_PASSWORD_ACTION
UPDATE_MASTER_ENDPOINT = USER_API_AREA + "/" + UPDATE_MASTER_ACTION

# API route names
AUTH_API_NAME = "authentication_api"
AUTH_LOGIN = AUTH_API_NAME + "." + LOGIN_ACTION
AUTH_LOGOUT = AUTH_API_NAME + "." + LOGOUT_ACTION

USER_API_NAME = "user_api"
USER_CHANGE_PASSWORD = USER_API_NAME + "." + CHANGE_PASSWORD_ACTION

class RoutingHelper:
	def __init__(self):
		self.ROOT_ENDPOINT = ROOT_ENDPOINT
		self.STATIC_ENDPOINT = STATIC_ENDPOINT
		self.LOGIN_ENDPOINT = LOGIN_ENDPOINT
		self.LOGOUT_ENDPOINT = LOGIN_ENDPOINT
		self.CHANGE_PASSWORD_ENDPOINT = CHANGE_PASSWORD_ENDPOINT

ROUTING = RoutingHelper()