# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Cocktail, Ingredient, CocktailIngredient, Review
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
from werkzeug.exceptions import HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS with specific origins
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Error handlers
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        logger.error(f"HTTP error occurred: {error}")
        response = {
            "error": str(error.description),
            "status_code": error.code
        }
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        logger.error(f"Unexpected error occurred: {error}")
        response = {
            "error": "An unexpected error occurred",
            "status_code": 500
        }
        return jsonify(response), 500

    # Health check and home route
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Cocktail API", "status": "online"})

    @app.route('/api/health-check')
    def health_check():
        try:
            db.session.execute('SELECT 1')
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 503

    # User CRUD Operations
    @app.route('/api/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            required_fields = ['username', 'email', 'password']
            
            # Validate required fields
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400

            # Check existing username
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already exists'}), 400
                
            # Check existing email
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists'}), 400
            
            user = User(
                username=data['username'],
                email=data['email'].lower()
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {user.username}")
            return jsonify({
                'message': 'User created successfully',
                'user_id': user.id
            }), 201

        except Exception as e:
            logger.error(f"Registration error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Registration failed'}), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            
            if not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username and password are required'}), 400

            user = User.query.filter_by(username=data['username']).first()
            
            if user and user.check_password(data['password']):
                access_token = create_access_token(
                    identity=user.id,
                    expires_delta=timedelta(hours=24)
                )
                
                logger.info(f"User logged in: {user.username}")
                return jsonify({
                    'token': access_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                }), 200
                
            return jsonify({'error': 'Invalid credentials'}), 401

        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({'error': 'Login failed'}), 500

    @app.route('/api/user/profile', methods=['GET'])
    @jwt_required()
    def get_user_profile():
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get_or_404(current_user_id)
            return jsonify({
                'username': user.username,
                'email': user.email,
                'reviews': [{
                    'id': review.id,
                    'cocktail_name': review.cocktail.name,
                    'content': review.content,
                    'rating': review.rating,
                    'created_at': review.created_at.isoformat()
                } for review in user.reviews]
            })
        except Exception as e:
            logger.error(f"Profile retrieval error: {e}")
            return jsonify({'error': 'Failed to retrieve profile'}), 500

    @app.route('/api/user/profile', methods=['PUT'])
    @jwt_required()
    def update_user_profile():
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get_or_404(current_user_id)
            data = request.get_json()

            if 'username' in data and data['username'] != user.username:
                if User.query.filter_by(username=data['username']).first():
                    return jsonify({'error': 'Username already exists'}), 400
                user.username = data['username']

            if 'email' in data and data['email'] != user.email:
                if User.query.filter_by(email=data['email']).first():
                    return jsonify({'error': 'Email already exists'}), 400
                user.email = data['email']

            if 'password' in data:
                user.set_password(data['password'])

            db.session.commit()
            logger.info(f"Profile updated for user: {user.username}")
            return jsonify({'message': 'Profile updated successfully'})
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to update profile'}), 500

    @app.route('/api/user/profile', methods=['DELETE'])
    @jwt_required()
    def delete_user_profile():
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get_or_404(current_user_id)
            
            # Delete all user's reviews first
            Review.query.filter_by(user_id=current_user_id).delete()
            
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"User account deleted: {user.username}")
            return jsonify({'message': 'User account deleted successfully'})
        except Exception as e:
            logger.error(f"Account deletion error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to delete account'}), 500

    # Cocktail CRUD Operations
    @app.route('/api/cocktails', methods=['GET'])
    def get_cocktails():
        try:
            cocktails = Cocktail.query.all()
            return jsonify([{
                'id': c.id,
                'name': c.name,
                'image_url': c.image_url,
                'instructions': c.instructions,
                'glass_type': c.glass_type,
                'ingredients': [{
                    'name': ci.ingredient.name,
                    'amount': ci.amount
                } for ci in c.ingredients]
            } for c in cocktails])
        except Exception as e:
            logger.error(f"Error fetching cocktails: {e}")
            return jsonify({'error': 'Failed to fetch cocktails'}), 500

    @app.route('/api/cocktails', methods=['POST'])
    @jwt_required()
    def create_cocktail():
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'instructions', 'glass_type', 'ingredients']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Create new cocktail
            cocktail = Cocktail(
                name=data['name'],
                image_url=data.get('image_url', ''),
                instructions=data['instructions'],
                glass_type=data['glass_type']
            )
            db.session.add(cocktail)
            db.session.flush()

            # Add ingredients
            for ingredient_data in data['ingredients']:
                if not ingredient_data.get('name'):
                    return jsonify({'error': 'Ingredient name is required'}), 400
                
                ingredient = Ingredient.query.filter_by(name=ingredient_data['name']).first()
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_data['name'])
                    db.session.add(ingredient)
                    db.session.flush()

                cocktail_ingredient = CocktailIngredient(
                    cocktail_id=cocktail.id,
                    ingredient_id=ingredient.id,
                    amount=ingredient_data.get('amount', '')
                )
                db.session.add(cocktail_ingredient)

            db.session.commit()
            logger.info(f"New cocktail created: {cocktail.name}")
            return jsonify({
                'message': 'Cocktail created successfully',
                'id': cocktail.id
            }), 201
        except Exception as e:
            logger.error(f"Error creating cocktail: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to create cocktail'}), 500

    @app.route('/api/cocktails/<int:id>', methods=['GET'])
    def get_cocktail(id):
        try:
            cocktail = Cocktail.query.get_or_404(id)
            return jsonify({
                'id': cocktail.id,
                'name': cocktail.name,
                'image_url': cocktail.image_url,
                'instructions': cocktail.instructions,
                'glass_type': cocktail.glass_type,
                'ingredients': [{
                    'name': ci.ingredient.name,
                    'amount': ci.amount
                } for ci in cocktail.ingredients],
                'reviews': [{
                    'id': r.id,
                    'content': r.content,
                    'rating': r.rating,
                    'user': r.user.username,
                    'created_at': r.created_at.isoformat()
                } for r in cocktail.reviews]
            })
        except Exception as e:
            logger.error(f"Error fetching cocktail {id}: {e}")
            return jsonify({'error': 'Failed to fetch cocktail'}), 500

    @app.route('/api/cocktails/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_cocktail(id):
        try:
            cocktail = Cocktail.query.get_or_404(id)
            data = request.get_json()

            # Update cocktail information
            cocktail.name = data.get('name', cocktail.name)
            cocktail.image_url = data.get('image_url', cocktail.image_url)
            cocktail.instructions = data.get('instructions', cocktail.instructions)
            cocktail.glass_type = data.get('glass_type', cocktail.glass_type)

            # Update ingredients
            if 'ingredients' in data:
                CocktailIngredient.query.filter_by(cocktail_id=cocktail.id).delete()

                for ingredient_data in data['ingredients']:
                    ingredient = Ingredient.query.filter_by(name=ingredient_data['name']).first()
                    if not ingredient:
                        ingredient = Ingredient(name=ingredient_data['name'])
                        db.session.add(ingredient)
                        db.session.flush()

                    cocktail_ingredient = CocktailIngredient(
                        cocktail_id=cocktail.id,
                        ingredient_id=ingredient.id,
                        amount=ingredient_data.get('amount', '')
                    )
                    db.session.add(cocktail_ingredient)

            db.session.commit()
            logger.info(f"Cocktail updated: {cocktail.name}")
            return jsonify({'message': 'Cocktail updated successfully'})
        except Exception as e:
            logger.error(f"Error updating cocktail {id}: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to update cocktail'}), 500

    @app.route('/api/cocktails/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_cocktail(id):
        try:
            cocktail = Cocktail.query.get_or_404(id)
            
            Review.query.filter_by(cocktail_id=id).delete()
            CocktailIngredient.query.filter_by(cocktail_id=id).delete()
            db.session.delete(cocktail)
            db.session.commit()
            
            logger.info(f"Cocktail deleted: {cocktail.name}")
            return jsonify({'message': 'Cocktail deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting cocktail {id}: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to delete cocktail'}), 500

    # Review CRUD Operations
    @app.route('/api/cocktails/<int:cocktail_id>/reviews', methods=['POST'])
    @jwt_required()
    def create_review(cocktail_id):
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data.get('content') or 'rating' not in data:
                return jsonify({'error': 'Content and rating are required'}), 400
            
            review = Review(
                content=data['content'],
                rating=data['rating'],
                user_id=current_user_id,
                cocktail_id=cocktail_id
            )
            
            db.session.add(review)
            db.session.commit()
            
            return jsonify({
                'id': review.id,
                'content': review.content,
                'rating': review.rating,
                'user': review.user.username,
                'created_at': review.created_at.isoformat()
            }), 201
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to create review'}), 500

    @app.route('/api/reviews/<int:review_id>', methods=['PUT'])
    @jwt_required()
    def update_review(review_id):
        try:
            current_user_id = get_jwt
            current_user_id = get_jwt_identity()
            review = Review.query.get_or_404(review_id)
            
            if review.user_id != current_user_id:
                return jsonify({'error': 'Unauthorized'}), 403
                
            data = request.get_json()
            
            if 'content' in data:
                review.content = data['content']
            if 'rating' in data:
                review.rating = data['rating']
            
            db.session.commit()
            logger.info(f"Review updated: ID {review.id}")
            
            return jsonify({
                'id': review.id,
                'content': review.content,
                'rating': review.rating,
                'user': review.user.username,
                'created_at': review.created_at.isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating review {review_id}: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to update review'}), 500

    @app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
    @jwt_required()
    def delete_review(review_id):
        try:
            current_user_id = get_jwt_identity()
            review = Review.query.get_or_404(review_id)
            
            if review.user_id != current_user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            db.session.delete(review)
            db.session.commit()
            logger.info(f"Review deleted: ID {review_id}")
            
            return jsonify({'message': 'Review deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting review {review_id}: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to delete review'}), 500

    # New helper endpoint for token verification
    @app.route('/api/verify-token', methods=['POST'])
    @jwt_required()
    def verify_token():
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get_or_404(current_user_id)
            return jsonify({
                'valid': True,
                'user_id': user.id,
                'username': user.username
            })
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return jsonify({'valid': False}), 401

    # Search endpoints
    @app.route('/api/cocktails/search', methods=['GET'])
    def search_cocktails():
        try:
            query = request.args.get('q', '').lower()
            ingredient = request.args.get('ingredient', '').lower()
            
            cocktails_query = Cocktail.query
            
            if query:
                cocktails_query = cocktails_query.filter(
                    Cocktail.name.ilike(f'%{query}%')
                )
            
            if ingredient:
                cocktails_query = cocktails_query.join(
                    CocktailIngredient
                ).join(
                    Ingredient
                ).filter(
                    Ingredient.name.ilike(f'%{ingredient}%')
                )
            
            cocktails = cocktails_query.all()
            
            return jsonify([{
                'id': c.id,
                'name': c.name,
                'image_url': c.image_url,
                'glass_type': c.glass_type,
                'ingredients': [{
                    'name': ci.ingredient.name,
                    'amount': ci.amount
                } for ci in c.ingredients]
            } for c in cocktails])
        except Exception as e:
            logger.error(f"Search error: {e}")
            return jsonify({'error': 'Search failed'}), 500

    @app.route('/api/ingredients', methods=['GET'])
    def get_ingredients():
        try:
            ingredients = Ingredient.query.order_by(Ingredient.name).all()
            return jsonify([{
                'id': i.id,
                'name': i.name
            } for i in ingredients])
        except Exception as e:
            logger.error(f"Error fetching ingredients: {e}")
            return jsonify({'error': 'Failed to fetch ingredients'}), 500

    # Initialize the app context and create tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise e

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)