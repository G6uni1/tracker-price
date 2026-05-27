import api from './api';

export interface TrackedProduct {
  id: string;
  url: string;
  store: string;
  product_name: string | null;
  target_price: number | null;
  is_active: boolean;
  created_at: string;
}

export interface PricePoint {
  id: string;
  product_id: string;
  price: number | null;
  currency: string;
  availability: boolean;
  collected_at: string;
}

export const getMyProducts = () => api.get<TrackedProduct[]>('/products/');

export const addProduct = (data: { url: string; store: string; target_price?: number }) =>
  api.post<TrackedProduct>('/products/', data);

export const getProductHistory = (productId: string, days = 30) =>
  api.get<PricePoint[]>(`/history/${productId}?days=${days}`);