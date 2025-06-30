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

    # Environment-aware DB config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///warehouse.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)

        # Only create tables if 'products' (or any core table) doesn't exist
        if not inspector.has_table("products"):
            db.create_all()
            print("✅ Database tables created.")
        else:
            print("ℹ️ Tables already exist. Skipping creation.")

    # CORS settings
    CORS(app, origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://waretracker.netlify.app"
    ])

    # Register blueprints
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
