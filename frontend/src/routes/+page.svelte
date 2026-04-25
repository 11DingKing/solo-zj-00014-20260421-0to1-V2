<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let categories = [];
	let books = [];
	let loading = true;
	let error = '';

	let selectedCategory = '';
	let searchQuery = '';
	let sortBy = '';

	async function loadCategories() {
		try {
			categories = await api.getCategories();
		} catch (e) {
			console.error('加载分类失败:', e);
		}
	}

	async function loadBooks() {
		loading = true;
		error = '';
		try {
			const params = {};
			if (selectedCategory) params.category = selectedCategory;
			if (searchQuery) params.search = searchQuery;
			if (sortBy) params.ordering = sortBy;

			const result = await api.getBooks(params);
			books = result.results || result;
		} catch (e) {
			error = e.message || '加载图书失败';
		} finally {
			loading = false;
		}
	}

	function handleSearch() {
		loadBooks();
	}

	function handleCategoryChange() {
		loadBooks();
	}

	function handleSortChange() {
		loadBooks();
	}

	async function addToCart(book) {
		if (book.stock <= 0) {
			alert('库存不足');
			return;
		}
		try {
			await api.addToCart(book.id, 1);
			alert('已添加到购物车');
		} catch (e) {
			alert('添加失败: ' + e.message);
		}
	}

	onMount(() => {
		loadCategories();
		loadBooks();
	});
</script>

<div class="page-header">
	<h1>📚 图书列表</h1>
</div>

<div class="filters">
	<div class="filter-group">
		<input
			type="text"
			bind:value={searchQuery}
			placeholder="搜索书名或作者..."
			class="search-input"
			on:keydown={(e) => e.key === 'Enter' && handleSearch()}
		/>
		<button class="search-btn" on:click={handleSearch}>搜索</button>
	</div>

	<div class="filter-group">
		<label>分类:</label>
		<select bind:value={selectedCategory} on:change={handleCategoryChange}>
			<option value="">全部分类</option>
			{#each categories as category}
				<option value={category.id}>{category.name}</option>
			{/each}
		</select>
	</div>

	<div class="filter-group">
		<label>排序:</label>
		<select bind:value={sortBy} on:change={handleSortChange}>
			<option value="">默认排序</option>
			<option value="price_asc">价格从低到高</option>
			<option value="price_desc">价格从高到低</option>
		</select>
	</div>
</div>

{#if loading}
	<div class="loading">加载中...</div>
{:else if error}
	<div class="error">{error}</div>
{:else if books.length === 0}
	<div class="empty">暂无图书</div>
{:else}
	<div class="books-grid">
		{#each books as book}
			<div class="book-card">
				<div class="book-cover">
					{#if book.cover_url}
						<img src={book.cover_url} alt={book.title} />
					{:else}
						<div class="no-cover">📖</div>
					{/if}
				</div>
				<div class="book-info">
					<h3 class="book-title" on:click={() => goto(`/book/${book.id}`)}>{book.title}</h3>
					<p class="book-author">作者: {book.author}</p>
					{#if book.category_name}
						<span class="book-category">{book.category_name}</span>
					{/if}
					<div class="book-price-row">
						<span class="book-price">¥{book.price}</span>
						<span class="book-stock {book.stock > 0 ? '' : 'out-of-stock'}">
							{book.stock > 0 ? `库存: ${book.stock}` : '缺货'}
						</span>
					</div>
					<button
						class="add-cart-btn"
						on:click={() => addToCart(book)}
						disabled={book.stock <= 0}
					>
						加入购物车
					</button>
				</div>
			</div>
		{/each}
	</div>
{/if}

<style>
	.page-header {
		margin-bottom: 30px;
	}

	.page-header h1 {
		margin: 0;
		color: #333;
	}

	.filters {
		background: #f8f9fa;
		padding: 20px;
		border-radius: 10px;
		margin-bottom: 30px;
		display: flex;
		flex-wrap: wrap;
		gap: 20px;
		align-items: center;
	}

	.filter-group {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.filter-group label {
		font-weight: 500;
		color: #555;
	}

	.search-input {
		padding: 10px 15px;
		border: 1px solid #ddd;
		border-radius: 5px;
		width: 250px;
		font-size: 14px;
	}

	.search-input:focus {
		outline: none;
		border-color: #667eea;
	}

	.search-btn {
		padding: 10px 20px;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		font-size: 14px;
	}

	.search-btn:hover {
		background: #5a6fd8;
	}

	select {
		padding: 10px 15px;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		background: white;
		cursor: pointer;
	}

	select:focus {
		outline: none;
		border-color: #667eea;
	}

	.loading,
	.error,
	.empty {
		text-align: center;
		padding: 50px;
		font-size: 18px;
		color: #666;
	}

	.error {
		color: #ff6b6b;
	}

	.books-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
		gap: 25px;
	}

	.book-card {
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		overflow: hidden;
		transition: transform 0.3s ease, box-shadow 0.3s ease;
	}

	.book-card:hover {
		transform: translateY(-5px);
		box-shadow: 0 5px 20px rgba(0, 0, 0, 0.12);
	}

	.book-cover {
		height: 180px;
		background: #f0f0f0;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
	}

	.book-cover img {
		height: 100%;
		object-fit: cover;
	}

	.no-cover {
		font-size: 60px;
		color: #ccc;
	}

	.book-info {
		padding: 20px;
	}

	.book-title {
		margin: 0 0 10px 0;
		font-size: 16px;
		color: #333;
		cursor: pointer;
		transition: color 0.2s;
	}

	.book-title:hover {
		color: #667eea;
	}

	.book-author {
		margin: 0 0 10px 0;
		font-size: 14px;
		color: #666;
	}

	.book-category {
		display: inline-block;
		background: #e8f0fe;
		color: #667eea;
		padding: 4px 10px;
		border-radius: 4px;
		font-size: 12px;
		margin-bottom: 10px;
	}

	.book-price-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 15px;
	}

	.book-price {
		font-size: 20px;
		font-weight: bold;
		color: #ff6b6b;
	}

	.book-stock {
		font-size: 12px;
		color: #666;
	}

	.book-stock.out-of-stock {
		color: #ff6b6b;
	}

	.add-cart-btn {
		width: 100%;
		padding: 12px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		font-size: 14px;
		font-weight: 500;
		transition: opacity 0.2s;
	}

	.add-cart-btn:hover:not(:disabled) {
		opacity: 0.9;
	}

	.add-cart-btn:disabled {
		background: #ccc;
		cursor: not-allowed;
	}
</style>
