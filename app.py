# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Cocktail, Ingredient, CocktailIngredient, Review
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)

    # Existing routes...
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Cocktail API"})

    @app.route('/api/health-check')
    def health_check():
        return jsonify({"status": "healthy"})

    # User CRUD Operations
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'token': access_token,
                'user_id': user.id,
                'username': user.username
            }), 200
            
        return jsonify({'error': 'Invalid credentials'}), 401

    @app.route('/api/user/profile', methods=['GET'])
    @jwt_required()
    def get_user_profile():
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

    @app.route('/api/user/profile', methods=['PUT'])
    @jwt_required()
    def update_user_profile():
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
        return jsonify({'message': 'Profile updated successfully'})

    @app.route('/api/user/profile', methods=['DELETE'])
    @jwt_required()
    def delete_user_profile():
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        # Delete all user's reviews first
        Review.query.filter_by(user_id=current_user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User account deleted successfully'})

    # Cocktail CRUD Operations
    @app.route('/api/cocktails', methods=['GET'])
    def get_cocktails():
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

    @app.route('/api/cocktails', methods=['POST'])
    @jwt_required()
    def create_cocktail():
        data = request.get_json()
        
        # Create new cocktail
        cocktail = Cocktail(
            name=data['name'],
            image_url=data['image_url'],
            instructions=data['instructions'],
            glass_type=data['glass_type']
        )
        db.session.add(cocktail)
        db.session.flush()  # Get the ID before committing

        # Add ingredients
        for ingredient_data in data['ingredients']:
            # Check if ingredient exists, if not create it
            ingredient = Ingredient.query.filter_by(name=ingredient_data['name']).first()
            if not ingredient:
                ingredient = Ingredient(name=ingredient_data['name'])
                db.session.add(ingredient)
                db.session.flush()

            # Create relationship
            cocktail_ingredient = CocktailIngredient(
                cocktail_id=cocktail.id,
                ingredient_id=ingredient.id,
                amount=ingredient_data['amount']
            )
            db.session.add(cocktail_ingredient)

        db.session.commit()
        return jsonify({'message': 'Cocktail created successfully', 'id': cocktail.id}), 201

    @app.route('/api/cocktails/<int:id>', methods=['GET'])
    def get_cocktail(id):
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

    @app.route('/api/cocktails/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_cocktail(id):
        cocktail = Cocktail.query.get_or_404(id)
        data = request.get_json()

        # Update basic cocktail information
        cocktail.name = data.get('name', cocktail.name)
        cocktail.image_url = data.get('image_url', cocktail.image_url)
        cocktail.instructions = data.get('instructions', cocktail.instructions)
        cocktail.glass_type = data.get('glass_type', cocktail.glass_type)

        # Update ingredients if provided
        if 'ingredients' in data:
            # Remove existing ingredients
            CocktailIngredient.query.filter_by(cocktail_id=cocktail.id).delete()

            # Add new ingredients
            for ingredient_data in data['ingredients']:
                ingredient = Ingredient.query.filter_by(name=ingredient_data['name']).first()
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_data['name'])
                    db.session.add(ingredient)
                    db.session.flush()

                cocktail_ingredient = CocktailIngredient(
                    cocktail_id=cocktail.id,
                    ingredient_id=ingredient.id,
                    amount=ingredient_data['amount']
                )
                db.session.add(cocktail_ingredient)

        db.session.commit()
        return jsonify({'message': 'Cocktail updated successfully'})

    @app.route('/api/cocktails/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_cocktail(id):
        cocktail = Cocktail.query.get_or_404(id)
        
        # Delete all reviews for this cocktail
        Review.query.filter_by(cocktail_id=id).delete()
        
        # Delete all ingredient relationships
        CocktailIngredient.query.filter_by(cocktail_id=id).delete()
        
        # Delete the cocktail
        db.session.delete(cocktail)
        db.session.commit()
        
        return jsonify({'message': 'Cocktail deleted successfully'})

    # Review CRUD Operations
    @app.route('/api/cocktails/<int:cocktail_id>/reviews', methods=['POST'])
    @jwt_required()
    def create_review(cocktail_id):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
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

    @app.route('/api/reviews/<int:review_id>', methods=['PUT'])
    @jwt_required()
    def update_review(review_id):
        current_user_id = get_jwt_identity()
        review = Review.query.get_or_404(review_id)
        
        if review.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        review.content = data.get('content', review.content)
        review.rating = data.get('rating', review.rating)
        
        db.session.commit()
        
        return jsonify({
            'id': review.id,
            'content': review.content,
            'rating': review.rating,
            'user': review.user.username,
            'created_at': review.created_at.isoformat()
        })

    @app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
    @jwt_required()
    def delete_review(review_id):
        current_user_id = get_jwt_identity()
        review = Review.query.get_or_404(review_id)
        
        if review.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({'message': 'Review deleted successfully'})

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)