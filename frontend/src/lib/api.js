const API_BASE = '/api';

async function request(endpoint, options = {}) {
	const url = `${API_BASE}${endpoint}`;
	const response = await fetch(url, {
		...options,
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		},
		credentials: 'include'
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ error: '请求失败' }));
		throw new Error(error.error || `HTTP ${response.status}`);
	}

	if (response.status === 204) {
		return null;
	}

	return response.json();
}

export const api = {
	getCategories: () => request('/categories/'),
	getCategory: (id) => request(`/categories/${id}/`),
	createCategory: (data) => request('/categories/', { method: 'POST', body: JSON.stringify(data) }),
	updateCategory: (id, data) => request(`/categories/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
	deleteCategory: (id) => request(`/categories/${id}/`, { method: 'DELETE' }),

	getBooks: (params = {}) => {
		const searchParams = new URLSearchParams();
		Object.entries(params).forEach(([key, value]) => {
			if (value) searchParams.append(key, value);
		});
		const query = searchParams.toString();
		return request(`/books/${query ? `?${query}` : ''}`);
	},

	getBook: (id) => request(`/books/${id}/`),

	createBook: (data) => request('/books/', { method: 'POST', body: JSON.stringify(data) }),

	updateBook: (id, data) => request(`/books/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),

	deleteBook: (id) => request(`/books/${id}/`, { method: 'DELETE' }),

	getCart: () => request('/cart/current/'),

	addToCart: (bookId, quantity = 1) =>
		request('/cart/add/', {
			method: 'POST',
			body: JSON.stringify({ book_id: bookId, quantity })
		}),

	updateCartItem: (itemId, quantity) =>
		request(`/cart/item/${itemId}/`, {
			method: 'PUT',
			body: JSON.stringify({ quantity })
		}),

	removeFromCart: (itemId) => request(`/cart/item/${itemId}/`, { method: 'DELETE' }),

	clearCart: () => request('/cart/clear/', { method: 'DELETE' }),

	getOrders: () => request('/orders/'),

	getOrder: (id) => request(`/orders/${id}/`),

	getMyOrders: () => request('/orders/my/'),

	createOrder: (data) =>
		request('/orders/create/', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	updateOrderStatus: (id, status) =>
		request(`/orders/${id}/status/`, {
			method: 'PUT',
			body: JSON.stringify({ status })
		})
};
