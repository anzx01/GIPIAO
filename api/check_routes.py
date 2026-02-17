from main import app
print('Routes:')
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f'  {route.path} [{route.methods}]')