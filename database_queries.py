select_user = """
SELECT user_id, first_name, last_name, email, password FROM users WHERE email = :email
"""

insert_token = """
INSERT INTO tokens (token, user_id) VALUES (:token, :user_id)
"""

select_token = """
SELECT token FROM tokens WHERE user_id = ?
"""

delete_token_for_user = """
DELETE FROM tokens where user_id = ?
"""

insert_user = """
INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)
"""
