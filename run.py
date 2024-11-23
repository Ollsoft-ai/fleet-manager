from livereload import Server
from app import create_app

app = create_app()

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('app/templates/')
    server.watch('app/static/')
    server.serve(port=80, host='0.0.0.0',debug=True) 