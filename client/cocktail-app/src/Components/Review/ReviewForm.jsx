import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import Alert from '../Alert/Alert';

function ReviewForm({ cocktailId, onReviewAdded }) {
  const [review, setReview] = useState({
    content: '',
    rating: 5
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      setError('You must be logged in to submit a review');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/cocktails/${cocktailId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(review)
      });

      if (!response.ok) throw new Error('Failed to submit review');

      setReview({ content: '', rating: 5 });
      if (onReviewAdded) onReviewAdded();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="review-form">
      {error && <Alert type="error" message={error} onClose={() => setError('')} />}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Rating</label>
          <div className="rating">
            {[5, 4, 3, 2, 1].map(num => (
              <button
                key={num}
                type="button"
                className={`star ${review.rating >= num ? 'active' : ''}`}
                onClick={() => setReview(prev => ({ ...prev, rating: num }))}
              >
                ★
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Your Review</label>
          <textarea
            className="form-input"
            value={review.content}
            onChange={(e) => setReview(prev => ({ ...prev, content: e.target.value }))}
            rows="4"
            required
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Submitting...' : 'Submit Review'}
        </button>
      </form>
    </div>
  );
}

export default ReviewForm;