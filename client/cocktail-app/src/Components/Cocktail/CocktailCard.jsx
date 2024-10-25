import React from 'react';

function CocktailCard({ cocktail }) {
  const defaultImage = 'https://via.placeholder.com/300x200?text=Cocktail';

  return (
    <div className="cocktail-card">
      <div className="cocktail-image-container">
        <img
          src={cocktail.image_url || defaultImage}
          alt={cocktail.name}
          className="cocktail-image"
          onError={(e) => {
            e.target.src = defaultImage;
          }}
        />
      </div>
      
      <div className="cocktail-content">
        <h3 className="cocktail-title">{cocktail.name}</h3>
        <p className="cocktail-type">{cocktail.glass_type}</p>
        
        <div className="ingredient-tags">
          {cocktail.ingredients.slice(0, 3).map((ing, index) => (
            <span key={index} className="ingredient-tag">
              {ing.name}
            </span>
          ))}
          {cocktail.ingredients.length > 3 && (
            <span className="ingredient-tag">
              +{cocktail.ingredients.length - 3} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default CocktailCard;