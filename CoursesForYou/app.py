from flask import Flask
from extensions import db
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        db.create_all()
        print("База данных и таблицы созданы!")
    app.run(debug=True)