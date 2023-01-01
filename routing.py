
# Actions in authentication area
LOGIN_ACTION = "login"
LOGOUT_ACTION = "logout"

# Actions in user management area
USER_API_AREA = "/user"
CHANGE_PASSWORD_ACTION = "change_password"

# Actions in admin area
ADMIN_API_AREA = "/admin"
UPDATE_MASTER_ACTION = "update_master"
LIST_USERS_ACTION = "list_users"
ADD_USER_ACTION = "add_user"

# Relative paths
ROOT_ENDPOINT ="/"
STATIC_ENDPOINT = "/static"
FAVICON_REQUEST = "/favicon.ico"

ROOT_ACTION = "list_tarps"

LOGIN_ENDPOINT = "/" + LOGIN_ACTION
LOGOUT_ENDPOINT = "/" + LOGOUT_ACTION

CHANGE_PASSWORD_ENDPOINT = USER_API_AREA + "/" + CHANGE_PASSWORD_ACTION

UPDATE_MASTER_ENDPOINT = ADMIN_API_AREA + "/" + UPDATE_MASTER_ACTION
LIST_USERS_ENDPOINT = ADMIN_API_AREA + "/" + LIST_USERS_ACTION
ADD_USER_ENDPOINT = ADMIN_API_AREA + "/" + ADD_USER_ACTION

# API route names
AUTH_API_NAME = "authentication_api"
AUTH_LOGIN = AUTH_API_NAME + "." + LOGIN_ACTION
AUTH_LOGOUT = AUTH_API_NAME + "." + LOGOUT_ACTION

USER_API_NAME = "user_api"
USER_CHANGE_PASSWORD = USER_API_NAME + "." + CHANGE_PASSWORD_ACTION

ADMIN_API_NAME = "admin_api"
ADMIN_UPDATE_MASTER = ADMIN_API_NAME + "." + UPDATE_MASTER_ACTION
ADMIN_ADD_USER = ADMIN_API_NAME + "." + ADD_USER_ACTION

class RoutingHelper:
	def __init__(self):
		self.ROOT_ENDPOINT = ROOT_ENDPOINT
		self.STATIC_ENDPOINT = STATIC_ENDPOINT
		self.LOGIN_ENDPOINT = LOGIN_ENDPOINT
		self.LOGOUT_ENDPOINT = LOGOUT_ENDPOINT
		self.CHANGE_PASSWORD_ENDPOINT = CHANGE_PASSWORD_ENDPOINT
		self.UPDATE_MASTER_ENDPOINT = UPDATE_MASTER_ENDPOINT
		self.LIST_USERS_ENDPOINT = LIST_USERS_ENDPOINT
		self.ADD_USER_ENDPOINT = ADD_USER_ENDPOINT

ROUTING = RoutingHelper()