import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import CocktailCard from './CocktailCard';
import Alert from '../Alert/Alert';

function CocktailList() {
  const [cocktails, setCocktails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchCocktails = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/cocktails');
        if (!response.ok) throw new Error('Failed to fetch cocktails');
        
        const data = await response.json();
        setCocktails(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCocktails();
  }, []);

  const filteredCocktails = cocktails.filter(cocktail =>
    cocktail.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="list-header">
        <h1>Cocktails Collection</h1>
        <div className="search-container">
          <input
            type="text"
            className="form-input"
            placeholder="Search cocktails..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {error && <Alert type="error" message={error} />}

      <div className="cocktail-grid">
        {filteredCocktails.map(cocktail => (
          <Link 
            key={cocktail.id} 
            to={`/cocktails/${cocktail.id}`}
            className="cocktail-link"
          >
            <CocktailCard cocktail={cocktail} />
          </Link>
        ))}
      </div>

      {filteredCocktails.length === 0 && !error && (
        <p className="no-results">
          No cocktails found matching "{searchTerm}"
        </p>
      )}
    </div>
  );
}

export default CocktailList;