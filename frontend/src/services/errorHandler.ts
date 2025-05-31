import { AxiosError } from 'axios';

export class ApiError extends Error {
  status?: number;
  code?: string;

  constructor(message: string, status?: number, code?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

export const handleApiError = (error: unknown): never => {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const code = error.code;
    const errorData = error.response?.data || {};
    const message =
      (typeof errorData.error === 'string' && errorData.error) ||
      errorData.message ||
      errorData.detail ||
      (Array.isArray(errorData.errors) && errorData.errors[0]?.message) ||
      error.message;

    switch (status) {
      case 400:
        throw new ApiError('Bad request. Please check your input.', status, code);
      case 401:
        throw new ApiError('Unauthorized access. Please check your login status.', status, code);
      case 403:
        throw new ApiError('Access forbidden. You do not have sufficient permissions.', status, code);
      case 404:
        throw new ApiError('The requested resource was not found.', status, code);
      case 413:
        throw new ApiError('Uploaded file is too large.', status, code);
      case 429:
        throw new ApiError('Too many requests. Please try again later.', status, code);
      case 500:
        throw new ApiError('Internal server error. Please try again later.', status, code);
    }

    if (status && status >= 400 && status < 500) {
      throw new ApiError(`Client error: ${message}`, status, code);
    } else if (status && status >= 500) {
      throw new ApiError(`Server error: ${message}`, status, code);
    }

    if (error.code === 'ECONNABORTED') {
      throw new ApiError('Request timed out. Please check your network connection.', undefined, error.code);
    }
    if (error.code === 'ERR_NETWORK') {
      throw new ApiError('Network error. Please check your connection.', undefined, error.code);
    }
  }

  if (error instanceof Error) {
    throw new ApiError(error.message);
  }

  throw new ApiError('An unknown error occurred.');
};
