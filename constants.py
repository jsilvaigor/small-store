import os

database_name = "api.db"
jwt_secret = os.environ.get("JWT_SECRET", "sup3rs3cr3t")
jwt_expire_hours = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))
