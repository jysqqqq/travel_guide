import axiosInstance from '../lib/axios';

// 后端 API 基础 URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 工具函数：获取完整的图片 URL
export const getFullImageUrl = (url: string) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${API_BASE_URL}${url}`;
};

// 类型定义
export interface Destination {
  id: number;
  title: string;
  description: string;
  cover_image: {
    id: number;
    title: string;
    url: string;
  };
  location: string;
  province: string;
  country: string;
  category: string;
  views_count: number;
  rating: number;
  best_season: string;
}

export interface Attraction {
  id: number;
  name: string;
  description: string;
  image: string;
  location: string;
  destination: number;
  // 添加其他必要字段
}

export interface Itinerary {
  id: number;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  is_public: boolean;
  // 添加其他必要字段
}

// API服务
export const api = {
  // 认证相关
  auth: {
    login: async (username: string, password: string) => {
      const response = await axiosInstance.post('/auth/token/', { username, password });
      return response.data;
    },
    register: async (userData: { username: string; password: string; email: string }) => {
      const response = await axiosInstance.post('/auth/register/', userData);
      return response.data;
    },
    getUserInfo: async () => {
      const response = await axiosInstance.get('/auth/user/');
      return response.data;
    },
  },

  // 目的地相关
  destinations: {
    getAll: async () => {
      const response = await axiosInstance.get<Destination[]>('/destinations/');
      return response.data;
    },
    getById: async (id: number) => {
      const response = await axiosInstance.get<Destination>(`/destinations/${id}/`);
      return response.data;
    },
    getPopular: async () => {
      const response = await axiosInstance.get<Destination[]>('/destinations/popular/');
      return response.data;
    },
    getAttractions: async (id: number) => {
      const response = await axiosInstance.get<Attraction[]>(`/destinations/${id}/attractions/`);
      return response.data;
    },
  },

  // 景点相关
  attractions: {
    getAll: async () => {
      const response = await axiosInstance.get<Attraction[]>('/attractions/');
      return response.data;
    },
    getById: async (id: number) => {
      const response = await axiosInstance.get<Attraction>(`/attractions/${id}/`);
      return response.data;
    },
  },

  // 行程相关
  itineraries: {
    getAll: async () => {
      const response = await axiosInstance.get<Itinerary[]>('/itineraries/');
      return response.data;
    },
    getById: async (id: number) => {
      const response = await axiosInstance.get<Itinerary>(`/itineraries/${id}/`);
      return response.data;
    },
    create: async (data: Partial<Itinerary>) => {
      const response = await axiosInstance.post('/itineraries/', data);
      return response.data;
    },
    update: async (id: number, data: Partial<Itinerary>) => {
      const response = await axiosInstance.put(`/itineraries/${id}/`, data);
      return response.data;
    },
    delete: async (id: number) => {
      await axiosInstance.delete(`/itineraries/${id}/`);
    },
  },

  // 收藏相关
  favorites: {
    getAll: async () => {
      const response = await axiosInstance.get('/favorites/');
      return response.data;
    },
    add: async (destinationId: number) => {
      const response = await axiosInstance.post('/favorites/', { destination: destinationId });
      return response.data;
    },
    remove: async (id: number) => {
      await axiosInstance.delete(`/favorites/${id}/`);
    },
  },

  // 测试
  test: {
    get: async () => {
      const response = await axiosInstance.get('/test/');
      return response.data;
    },
  },
}; 