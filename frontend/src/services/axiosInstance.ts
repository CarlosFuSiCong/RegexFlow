import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

let csrfFetched = false;

api.interceptors.request.use(
  async (config) => {
    try {
      // Only fetch CSRF cookie once, if not already present
      if (!csrfFetched && !document.cookie.includes('csrftoken')) {
        await axios.get('/api/csrf-token/');
        csrfFetched = true;
      }

      // Read the token from the cookie
      const csrfToken = document.cookie
        .split('; ')
        .find((row) => row.startsWith('csrftoken='))
        ?.split('=')[1];

      if (csrfToken && config.headers) {
        config.headers['X-CSRFToken'] = csrfToken;
      }

      return config;
    } catch (error) {
      return Promise.reject(error);
    }
  },
  (error) => Promise.reject(error)
);

export default api;
