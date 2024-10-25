import React from 'react';

function Alert({ type = 'info', message, onClose }) {
  if (!message) return null;

  return (
    <div className={`alert alert-${type}`}>
      <div className="alert-content">
        <span>{message}</span>
        {onClose && (
          <button onClick={onClose} className="alert-close">
            ×
          </button>
        )}
      </div>
    </div>
  );
}

export default Alert;