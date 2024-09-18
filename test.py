from werkzeug.security import generate_password_hash, check_password_hash

pwh = generate_password_hash("123")
check = check_password_hash(pwh, "123")
print(len(pwh))