const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  static getAuthHeaders(token) {
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
  }

  static async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'API request failed');
    }
    return response.json();
  }

  // Auth endpoints
  static async login(credentials) {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(credentials)
    });
    return this.handleResponse(response);
  }

  static async register(userData) {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(userData)
    });
    return this.handleResponse(response);
  }

  // Cocktail endpoints
  static async getCocktails() {
    const response = await fetch(`${API_BASE_URL}/cocktails`);
    return this.handleResponse(response);
  }

  static async getCocktail(id) {
    const response = await fetch(`${API_BASE_URL}/cocktails/${id}`);
    return this.handleResponse(response);
  }

  static async createCocktail(cocktailData, token) {
    const response = await fetch(`${API_BASE_URL}/cocktails`, {
      method: 'POST',
      headers: this.getAuthHeaders(token),
      body: JSON.stringify(cocktailData)
    });
    return this.handleResponse(response);
  }

  static async updateCocktail(id, cocktailData, token) {
    const response = await fetch(`${API_BASE_URL}/cocktails/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(token),
      body: JSON.stringify(cocktailData)
    });
    return this.handleResponse(response);
  }

  static async deleteCocktail(id, token) {
    const response = await fetch(`${API_BASE_URL}/cocktails/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(token)
    });
    return this.handleResponse(response);
  }

  // Review endpoints
  static async addReview(cocktailId, reviewData, token) {
    const response = await fetch(`${API_BASE_URL}/cocktails/${cocktailId}/reviews`, {
      method: 'POST',
      headers: this.getAuthHeaders(token),
      body: JSON.stringify(reviewData)
    });
    return this.handleResponse(response);
  }

  static async deleteReview(reviewId, token) {
    const response = await fetch(`${API_BASE_URL}/reviews/${reviewId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(token)
    });
    return this.handleResponse(response);
  }

  // Search endpoint
  static async searchCocktails(query) {
    const response = await fetch(`${API_BASE_URL}/cocktails/search?q=${query}`);
    return this.handleResponse(response);
  }
}

export default ApiService;