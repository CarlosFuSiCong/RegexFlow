import api from './axiosInstance';
import { handleApiError } from './errorHandler';
import { UploadResponse } from '../types/api';
import type { PreviewDataResponse } from "@/types/api";

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const downloadFile = async (filename?: string): Promise<Blob> => {
  try {
    const response = await api.get<Blob>('/download', {
      params: { filename },
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const previewData = async (
  page: number = 1,
  pageSize: number = 50
): Promise<PreviewDataResponse> => {
  try {
    const response = await api.get<PreviewDataResponse>("/preview_data", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};