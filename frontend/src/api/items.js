import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Fetch all items
export const getItems = () => API.get('/items');

// Fetch single item
export const getItem = (name) => API.get(`/items/${name}`);

// Create new item
export const createItem = (data) => API.post('/items', data);

// Update item
export const updateItem = (name, data) => API.put(`/items/${name}`, data);

// Delete item
export const deleteItem = (name) => API.delete(`/items/${name}`);
