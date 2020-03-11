from app import create_app
app = create_app(proxy_fix = False, secret_key = "not secret")
print(app.url_map)
