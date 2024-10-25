import React from 'react';
import { useAuth } from '../../context/AuthContext';
import Alert from '../Alert/Alert';

function ReviewList({ reviews, onReviewDeleted }) {
  const { user, token } = useAuth();
  const [error, setError] = React.useState('');

  const handleDelete = async (reviewId) => {
    if (!token) {
      setError('You must be logged in to delete a review');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this review?')) return;

    try {
      const response = await fetch(`http://localhost:5000/api/reviews/${reviewId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete review');
      if (onReviewDeleted) onReviewDeleted();
    } catch (err) {
      setError(err.message);
    }
  };

  if (!reviews.length) {
    return <p className="no-reviews">No reviews yet. Be the first to review!</p>;
  }

  return (
    <div className="review-list">
      {error && <Alert type="error" message={error} onClose={() => setError('')} />}

      {reviews.map(review => (
        <div key={review.id} className="review-card">
          <div className="review-header">
            <div className="review-info">
              <span className="review-author">{review.user}</span>
              <div className="rating">
                {[...Array(5)].map((_, i) => (
                  <span
                    key={i}
                    className={`star ${i < review.rating ? 'active' : ''}`}
                  >
                    ★
                  </span>
                ))}
              </div>
            </div>
            {user && user.id === review.user_id && (
              <button
                className="btn btn-danger"
                onClick={() => handleDelete(review.id)}
              >
                Delete
              </button>
            )}
          </div>
          <p className="review-content">{review.content}</p>
          <span className="review-date">
            {new Date(review.created_at).toLocaleDateString()}
          </span>
        </div>
      ))}
    </div>
  );
}

export default ReviewList;