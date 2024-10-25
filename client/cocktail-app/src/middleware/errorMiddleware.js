export const handleApiError = async (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error
      const data = await error.response.json();
      return {
        success: false,
        error: data.error || 'Server error occurred',
        status: error.response.status
      };
    } else if (error.request) {
      // Request made but no response
      return {
        success: false,
        error: 'No response from server. Please check your connection.',
        status: 0
      };
    } else {
      // Request setup error
      return {
        success: false,
        error: error.message || 'An unexpected error occurred',
        status: 500
      };
    }
  };
  
  export const checkAuth = (token) => {
    if (!token) {
      throw new Error('Authentication required');
    }
  };