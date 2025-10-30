"""Constantes de la aplicación"""

# Límites de paginación
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Límites de campos
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 100
MAX_FULL_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 255

MIN_POST_TITLE_LENGTH = 1
MAX_POST_TITLE_LENGTH = 200
MIN_POST_CONTENT_LENGTH = 1

MIN_COMMENT_CONTENT_LENGTH = 1
MAX_COMMENT_CONTENT_LENGTH = 1000

MAX_TAG_NAME_LENGTH = 50

# Mensajes de error comunes
ERROR_USER_NOT_FOUND = "User not found"
ERROR_POST_NOT_FOUND = "Post not found"
ERROR_COMMENT_NOT_FOUND = "Comment not found"
ERROR_TAG_NOT_FOUND = "Tag not found"
ERROR_UNAUTHORIZED = "Not authorized to perform this action"
ERROR_INVALID_CREDENTIALS = "Incorrect username or password"
ERROR_EMAIL_TAKEN = "Email already registered"
ERROR_USERNAME_TAKEN = "Username already taken"
ERROR_INVALID_TOKEN = "Could not validate credentials"

# Headers
HEADER_PROCESS_TIME = "X-Process-Time"
HEADER_WWW_AUTHENTICATE = "WWW-Authenticate"
