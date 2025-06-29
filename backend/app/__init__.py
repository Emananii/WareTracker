from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from .models import db

from .routes.suppliers import suppliers_bp
from .routes.purchases import purchases_bp
from .routes.products import product_bp
from .routes.purchase_items import purchase_item_bp
from .routes.categories import category_bp
from .routes.stock_transfers import stock_transfer_bp
from .routes.stock_transfer_items import stock_transfer_item_bp
from .routes.business_locations import business_location_bp
from .routes.dashboard import dashboard_bp

from flasgger import Swagger

import os

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SWAGGER'] = {
        'title': 'Warehouse Tracker API',
        'uiversion': 3,
        'specs_route': '/apidocs',
        'openapi': '3.0.2',
        'specs': [
            {
                'endpoint': 'apispec_1',
                'route': '/apispec_1.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ]
    }
    Swagger(app)

    #Environment-aware DB config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///warehouse.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/*": {"origins": [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://waretracker.netlify.app/"
    ]}})

    
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(purchase_item_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(stock_transfer_bp)
    app.register_blueprint(stock_transfer_item_bp)
    app.register_blueprint(business_location_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        return {
            "message": "Warehouse Tracker API is running.",
            "docs": "/apidocs"
        }

    return app
