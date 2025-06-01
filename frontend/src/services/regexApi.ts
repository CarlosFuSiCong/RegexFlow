import api from './axiosInstance';
import { handleApiError } from './errorHandler';
import {
  PreviewDataResponse,
  GenerateTasksRequest,
  GenerateTasksResponse,
  PreviewReplaceRequest,
  PreviewReplaceResponse,
  ReplaceTasksRequest,
  ReplaceTasksResponse,
} from '../types/api';

export const previewData = async (
  page: number = 1,
  pageSize: number = 50
): Promise<PreviewDataResponse> => {
  try {
    const response = await api.get<PreviewDataResponse>('/preview_data', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const generateRegexTasks = async (
  data: GenerateTasksRequest
): Promise<GenerateTasksResponse> => {
  try {
    const response = await api.post<GenerateTasksResponse>('/generate_tasks', data);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const previewReplace = async (
  data: PreviewReplaceRequest
): Promise<PreviewReplaceResponse> => {
  try {
    const response = await api.post<PreviewReplaceResponse>('/preview_replace', data);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const replaceTasks = async (
  data: ReplaceTasksRequest
): Promise<ReplaceTasksResponse> => {
  try {
    const response = await api.post<ReplaceTasksResponse>('/replace', data);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};
