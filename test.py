from werkzeug.security import generate_password_hash

hash = generate_password_hash("good")
print(hash)
