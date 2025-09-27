import os
from flask import Flask
from routes import routes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
screens_dir = os.path.abspath(os.path.join(BASE_DIR, '..', 'Screens'))

app = Flask(__name__, template_folder=screens_dir)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'habibuniversity')
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)
