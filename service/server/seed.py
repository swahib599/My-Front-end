# seed.py
import logging
from datetime import datetime
from models import db, User, Cocktail, Ingredient, CocktailIngredient, Review
from flask import Flask
from config import Config
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_data(app):
    try:
        logger.info("Starting the seeding process...")

        # Clear existing data in the correct order
        logger.info("Clearing existing data...")
        Review.query.delete()
        CocktailIngredient.query.delete()
        Cocktail.query.delete()
        Ingredient.query.delete()
        User.query.delete()
        
        db.session.commit()
        logger.info("Existing data cleared successfully!")

        # Create test users
        logger.info("Creating test users...")
        users = [
            {
                "username": "cocktail_lover",
                "email": "cocktail@example.com",
                "password": "mixology123"
            },
            {
                "username": "bar_enthusiast",
                "email": "bar@example.com",
                "password": "cheers456"
            },
            {
                "username": "drink_master",
                "email": "master@example.com",
                "password": "spirits789"
            }
        ]

        created_users = []
        for user_data in users:
            user = User(
                username=user_data["username"],
                email=user_data["email"]
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            created_users.append(user)

        db.session.commit()
        logger.info("Test users created successfully!")

        cocktails = [
            {
                "id": 1,
                "name": "Classic Mojito",
                "image": "https://images.unsplash.com/photo-1551538827-9c037cb4f32a",
                "directions": "Muddle mint leaves with sugar and lime juice. Add rum and fill glass with crushed ice. Top with club soda and garnish with mint sprig.",
                "glass_type": "Highball",
                "ingredients": [
                    "2 oz White rum",
                    "1 oz Fresh lime juice",
                    "0.75 oz Simple syrup",
                    "6-8 Fresh mint leaves",
                    "2 oz Club soda",
                    "1 Mint sprig for garnish"
                ]
            },
            {
                "id": 2,
                "name": "Espresso Martini",
                "image": "https://images.unsplash.com/photo-1545438102-799c3991ffb2",
                "directions": "Shake vodka, coffee liqueur, and fresh espresso with ice. Strain into chilled martini glass. Garnish with coffee beans.",
                "glass_type": "Martini",
                "ingredients": [
                    "2 oz Vodka",
                    "1 oz Coffee liqueur",
                    "1 oz Fresh espresso",
                    "0.5 oz Simple syrup",
                    "3 Coffee beans for garnish"
                ]
            },
            {
                "id": 3,
                "name": "Negroni",
                "image": "https://images.unsplash.com/photo-1570598912132-0ba1dc952b7d",
                "directions": "Stir gin, Campari, and sweet vermouth with ice. Strain into rocks glass over large ice cube. Garnish with orange peel.",
                "glass_type": "Rocks",
                "ingredients": [
                    "1 oz Gin",
                    "1 oz Campari",
                    "1 oz Sweet vermouth",
                    "1 Orange peel for garnish"
                ]
            },
            {
                "id": 4,
                "name": "Passion Fruit Margarita",
                "image": "https://images.unsplash.com/photo-1556855810-ac404aa91e85",
                "directions": "Shake tequila, passion fruit puree, lime juice, and triple sec with ice. Strain into salt-rimmed glass. Garnish with lime wheel.",
                "glass_type": "Margarita",
                "ingredients": [
                    "2 oz Tequila",
                    "1 oz Passion fruit puree",
                    "0.75 oz Fresh lime juice",
                    "0.5 oz Triple sec",
                    "Salt for rim",
                    "1 Lime wheel for garnish"
                ]
            },
            {
                "id": 5,
                "name": "Old Fashioned",
                "image": "https://images.unsplash.com/photo-1470337458703-46ad1756a187",
                "directions": "Muddle sugar cube with bitters and splash of water. Add bourbon and stir with ice. Garnish with orange peel and cherry.",
                "glass_type": "Rocks",
                "ingredients": [
                    "2 oz Bourbon",
                    "1 Sugar cube",
                    "2-3 dashes Angostura bitters",
                    "1 Orange peel",
                    "1 Maraschino cherry"
                ]
            },
            {
                "id": 6,
                "name": "French 75",
                "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc",
                "directions": "Shake gin, lemon juice, and simple syrup with ice. Strain into champagne flute and top with champagne. Garnish with lemon twist.",
                "glass_type": "Champagne Flute",
                "ingredients": [
                    "1.5 oz Gin",
                    "0.75 oz Fresh lemon juice",
                    "0.5 oz Simple syrup",
                    "3 oz Champagne",
                    "1 Lemon twist for garnish"
                ]
            },
            {
                "id": 7,
                "name": "Piña Colada",
                "image": "https://images.unsplash.com/photo-1582633987110-6b4ca43e9a49",
                "directions": "Blend rum, coconut cream, pineapple juice, and ice until smooth. Pour into glass and garnish with pineapple wedge and cherry.",
                "glass_type": "Hurricane",
                "ingredients": [
                    "2 oz White rum",
                    "2 oz Coconut cream",
                    "2 oz Pineapple juice",
                    "1.5 cups Crushed ice",
                    "1 Pineapple wedge",
                    "1 Maraschino cherry"
                ]
            },
            {
                "id": 8,
                "name": "Moscow Mule",
                "image": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b",
                "directions": "Combine vodka and lime juice in copper mug with ice. Top with ginger beer and garnish with lime wheel and mint sprig.",
                "glass_type": "Copper Mug",
                "ingredients": [
                    "2 oz Vodka",
                    "0.5 oz Fresh lime juice",
                    "4 oz Ginger beer",
                    "1 Lime wheel",
                    "1 Mint sprig"
                ]
            },
            {
                "id": 9,
                "name": "Cosmopolitan",
                "image": "https://images.unsplash.com/photo-1560512823-829485b8bf24",
                "directions": "Shake vodka, cranberry juice, lime juice, and triple sec with ice. Strain into martini glass and garnish with lime wheel.",
                "glass_type": "Martini",
                "ingredients": [
                    "1.5 oz Citrus vodka",
                    "1 oz Cranberry juice",
                    "0.5 oz Fresh lime juice",
                    "0.5 oz Triple sec",
                    "1 Lime wheel for garnish"
                ]
            },
            {
                "id": 10,
                "name": "Mai Tai",
                "image": "https://images.unsplash.com/photo-1549746423-e5fe9cafded8",
                "directions": "Shake rums, orange curacao, orgeat, and lime juice with ice. Strain into glass filled with crushed ice. Float dark rum on top.",
                "glass_type": "Rocks",
                "ingredients": [
                    "2 oz White rum",
                    "0.5 oz Orange curacao",
                    "0.5 oz Orgeat syrup",
                    "1 oz Fresh lime juice",
                    "0.5 oz Dark rum float",
                    "1 Mint sprig for garnish"
                ]
            },
            {
                "id": 11,
                "name": "Aviation",
                "image": "https://images.unsplash.com/photo-1527761939622-9119e4eec134",
                "directions": "Shake gin, maraschino liqueur, creme de violette, and lemon juice with ice. Strain into cocktail glass. Garnish with cherry.",
                "glass_type": "Coupe",
                "ingredients": [
                    "2 oz Gin",
                    "0.5 oz Maraschino liqueur",
                    "0.25 oz Creme de violette",
                    "0.75 oz Fresh lemon juice",
                    "1 Maraschino cherry for garnish"
                ]
            },
            {
                "id": 12,
                "name": "Whiskey Sour",
                "image": "https://images.unsplash.com/photo-1514362453360-8f2671dd9802",
                "directions": "Shake whiskey, lemon juice, simple syrup, and optional egg white with ice. Strain into rocks glass over ice. Garnish with orange slice and cherry.",
                "glass_type": "Rocks",
                "ingredients": [
                    "2 oz Bourbon",
                    "1 oz Fresh lemon juice",
                    "0.75 oz Simple syrup",
                    "1 Egg white (optional)",
                    "1 Orange slice",
                    "1 Maraschino cherry"
                ]
            },
            {
                "id": 13,
                "name": "Gin Basil Smash",
                "image": "https://images.unsplash.com/photo-1558950334-8d04704332f8",
                "directions": "Muddle basil leaves with simple syrup. Add gin and lemon juice, shake with ice. Double strain into rocks glass over ice. Garnish with basil leaf.",
                "glass_type": "Rocks",
                "ingredients": [
                    "2 oz Gin",
                    "1 oz Fresh lemon juice",
                    "0.75 oz Simple syrup",
                    "8-10 Fresh basil leaves",
                    "1 Basil leaf for garnish"
                ]
            }
        ]

        # Create ingredients
        logger.info("Creating ingredients...")
        ingredient_dict = {}
        for cocktail_data in cocktails:
            for ingredient_str in cocktail_data['ingredients']:
                parts = ingredient_str.split(' ', 1)
                name = parts[1] if len(parts) > 1 else parts[0]
                
                if name not in ingredient_dict:
                    ingredient = Ingredient(name=name)
                    db.session.add(ingredient)
                    ingredient_dict[name] = ingredient

        db.session.commit()
        logger.info("Ingredients created successfully!")

        # Create cocktails and their relationships
        logger.info("Creating cocktails and relationships...")
        created_cocktails = {}
        for cocktail_data in cocktails:
            cocktail = Cocktail(
                id=cocktail_data['id'],
                name=cocktail_data['name'],
                image_url=cocktail_data['image'],
                instructions=cocktail_data['directions'],
                glass_type=cocktail_data['glass_type']
            )
            db.session.add(cocktail)
            created_cocktails[cocktail_data['id']] = cocktail

            for ingredient_str in cocktail_data['ingredients']:
                parts = ingredient_str.split(' ', 1)
                amount = parts[0] if len(parts) > 1 else ''
                name = parts[1] if len(parts) > 1 else parts[0]
                
                ingredient = ingredient_dict[name]
                
                cocktail_ingredient = CocktailIngredient(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    amount=amount
                )
                db.session.add(cocktail_ingredient)

        db.session.commit()
        logger.info("Cocktails and relationships created successfully!")

        # Add sample reviews
        logger.info("Creating sample reviews...")
        sample_reviews = [
            {
                "cocktail_id": 1,
                "content": "Perfect summer drink! The mint makes it so refreshing.",
                "rating": 5,
                "user_id": created_users[0].id
            },
            {
                "cocktail_id": 2,
                "content": "Best espresso martini I've ever made at home. Perfect balance!",
                "rating": 5,
                "user_id": created_users[1].id
            },
            {
                "cocktail_id": 3,
                "content": "A classic for a reason. Perfect balance of bitter and sweet.",
                "rating": 4,
                "user_id": created_users[2].id
            },
            {
                "cocktail_id": 4,
                "content": "The passion fruit adds an amazing tropical twist!",
                "rating": 5,
                "user_id": created_users[0].id
            },
            {
                "cocktail_id": 5,
                "content": "You can't go wrong with a well-made Old Fashioned.",
                "rating": 5,
                "user_id": created_users[1].id
            }
        ]

        for review_data in sample_reviews:
            review = Review(
                content=review_data["content"],
                rating=review_data["rating"],
                user_id=review_data["user_id"],
                cocktail_id=review_data["cocktail_id"],
                created_at=datetime.utcnow()
            )
            db.session.add(review)

        db.session.commit()
        logger.info("Sample reviews created successfully!")

        logger.info("Database seeding completed successfully!")
        logger.info("Test user credentials created:")
        for user in users:
            logger.info(f"Username: {user['username']}, Password: {user['password']}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while seeding data: {str(e)}")
        raise e

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_data(app)