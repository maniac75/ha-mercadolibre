"""Constants for the Mercado Libre integration."""

DOMAIN = "mercadolibre_tracking"
API_URL = "https://api.mercadolibre.com"
AUTHORIZE_URL = "https://auth.mercadolibre.cl/authorization"
TOKEN_URL = API_URL + "/oauth/token"
MAX_ORDERS = 200
PAGE_SIZE = 50
TERMINAL_STATUSES = frozenset({"delivered", "cancelled", "not_delivered"})
ACTIVE_STATUSES = frozenset({"pending", "handling", "ready_to_ship", "shipped"})
