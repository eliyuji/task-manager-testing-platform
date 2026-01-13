"""Main application entry point."""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config.config import get_config
from app.utils.database import db


def create_app(config_name='development'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})
    
    # Register blueprints
    from app.routes import auth, tasks, projects, test_results
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(tasks.bp, url_prefix='/api/tasks')
    app.register_blueprint(projects.bp, url_prefix='/api/projects')
    app.register_blueprint(test_results.bp, url_prefix='/api/test-results')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint for load balancer."""
        return jsonify({
            'status': 'healthy',
            'app': app.config['APP_NAME'],
            'environment': app.config.get('ENVIRONMENT', 'development')
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )