# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "$%az@imdlu1@)om@_dlt54m%4ho5r232h*go)x9%d*x5^mcw-c"

# Add your site's domain name(s) here. Disabled by default on localhost.
# ALLOWED_HOSTS = ["localhost"]

# Default email address used to send messages from the website.
DEFAULT_FROM_EMAIL = "swblog <info@localhost>"

# A list of people who get error notifications.
ADMINS = [
    ("Administrator", "admin@localhost"),
]

# A list in the same format as ADMINS that specifies who should get broken link
# (404) notifications when BrokenLinkEmailsMiddleware is enabled.
MANAGERS = ADMINS

# Email address used to send error messages to ADMINS.
SERVER_EMAIL = DEFAULT_FROM_EMAIL
