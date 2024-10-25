import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Alert from '../Alert/Alert';

function CocktailDetail() {
  const [cocktail, setCocktail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const { id } = useParams();
  const { user, token } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    glass_type: '',
    instructions: '',
    image_url: '',
    ingredients: [{ name: '', amount: '' }]
  });

  const fetchCocktail = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/cocktails/${id}`);
      if (!response.ok) throw new Error('Failed to fetch cocktail');
      
      const data = await response.json();
      setCocktail(data);
      setFormData({
        name: data.name,
        glass_type: data.glass_type,
        instructions: data.instructions,
        image_url: data.image_url,
        ingredients: data.ingredients.map(ing => ({
          name: ing.name,
          amount: ing.amount
        }))
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCocktail();
  }, [fetchCocktail]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleIngredientChange = (index, field, value) => {
    setFormData(prev => {
      const newIngredients = [...prev.ingredients];
      newIngredients[index] = {
        ...newIngredients[index],
        [field]: value
      };
      return { ...prev, ingredients: newIngredients };
    });
  };

  const addIngredient = () => {
    setFormData(prev => ({
      ...prev,
      ingredients: [...prev.ingredients, { name: '', amount: '' }]
    }));
  };

  const removeIngredient = (index) => {
    if (formData.ingredients.length <= 1) return;
    setFormData(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      setError('You must be logged in to perform this action');
      return;
    }

    try {
      const url = id === 'new' 
        ? 'http://localhost:5000/api/cocktails'
        : `http://localhost:5000/api/cocktails/${id}`;
      
      const method = id === 'new' ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Failed to save cocktail');

      const data = await response.json();
      if (id === 'new') {
        navigate(`/cocktails/${data.id}`);
      } else {
        setIsEditing(false);
        await fetchCocktail();
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!token) {
      setError('You must be logged in to perform this action');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this cocktail?')) return;

    try {
      const response = await fetch(`http://localhost:5000/api/cocktails/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete cocktail');
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="cocktail-detail">
      {error && <Alert type="error" message={error} onClose={() => setError('')} />}

      {isEditing ? (
        <form onSubmit={handleSubmit} className="cocktail-form">
          <h2>{id === 'new' ? 'Create New Cocktail' : 'Edit Cocktail'}</h2>

          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label>Glass Type</label>
            <input
              type="text"
              name="glass_type"
              value={formData.glass_type}
              onChange={handleInputChange}
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label>Image URL</label>
            <input
              type="url"
              name="image_url"
              value={formData.image_url}
              onChange={handleInputChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Instructions</label>
            <textarea
              name="instructions"
              value={formData.instructions}
              onChange={handleInputChange}
              className="form-input"
              rows="4"
              required
            />
          </div>

          <div className="ingredients-section">
            <label>Ingredients</label>
            {formData.ingredients.map((ing, index) => (
              <div key={index} className="ingredient-row">
                <input
                  type="text"
                  placeholder="Amount"
                  value={ing.amount}
                  onChange={(e) => handleIngredientChange(index, 'amount', e.target.value)}
                  className="form-input"
                />
                <input
                  type="text"
                  placeholder="Ingredient"
                  value={ing.name}
                  onChange={(e) => handleIngredientChange(index, 'name', e.target.value)}
                  className="form-input"
                />
                <button
                  type="button"
                  onClick={() => removeIngredient(index)}
                  className="btn btn-danger"
                  disabled={formData.ingredients.length <= 1}
                >
                  Remove
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={addIngredient}
              className="btn btn-secondary"
            >
              Add Ingredient
            </button>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              {id === 'new' ? 'Create Cocktail' : 'Save Changes'}
            </button>
            {id !== 'new' && (
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      ) : (
        <div className="cocktail-view">
          <div className="cocktail-header">
            <img
              src={cocktail?.image_url}
              alt={cocktail?.name}
              className="cocktail-detail-image"
              onError={(e) => {
                e.target.src = '/default-cocktail.jpg';
              }}
            />
            <div className="cocktail-info">
              <h1>{cocktail?.name}</h1>
              <p className="glass-type">{cocktail?.glass_type}</p>
            </div>
          </div>

          <div className="ingredients-section">
            <h2>Ingredients</h2>
            <ul>
              {cocktail?.ingredients.map((ing, index) => (
                <li key={index} className="ingredient-item">
                  <span className="ingredient-amount">{ing.amount}</span>
                  <span className="ingredient-name">{ing.name}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="instructions">
            <h2>Instructions</h2>
            <p>{cocktail?.instructions}</p>
          </div>

          {user && (
            <div className="action-buttons">
              <button
                onClick={() => setIsEditing(true)}
                className="btn btn-primary"
              >
                Edit Cocktail
              </button>
              <button
                onClick={handleDelete}
                className="btn btn-danger"
              >
                Delete Cocktail
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CocktailDetail;