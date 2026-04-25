<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let book = null;
	let loading = true;
	let error = '';
	let quantity = 1;

	async function loadBook() {
		loading = true;
		error = '';
		try {
			book = await api.getBook($page.params.id);
		} catch (e) {
			error = e.message || '加载图书失败';
		} finally {
			loading = false;
		}
	}

	async function addToCart() {
		if (book.stock < quantity) {
			alert(`库存不足，当前库存: ${book.stock}`);
			return;
		}
		try {
			await api.addToCart(book.id, quantity);
			alert('已添加到购物车');
		} catch (e) {
			alert('添加失败: ' + e.message);
		}
	}

	onMount(() => {
		loadBook();
	});
</script>

{#if loading}
	<div class="loading">加载中...</div>
{:else if error}
	<div class="error">
		<p>{error}</p>
		<a href="/" class="back-link">返回首页</a>
	</div>
{:else}
	<div class="book-detail">
		<div class="breadcrumb">
			<a href="/">首页</a>
			<span>›</span>
			<span>{book.title}</span>
		</div>

		<div class="book-content">
			<div class="book-cover-large">
				{#if book.cover_url}
					<img src={book.cover_url} alt={book.title} />
				{:else}
					<div class="no-cover-large">📖</div>
				{/if}
			</div>

			<div class="book-info-large">
				<h1>{book.title}</h1>
				<div class="book-meta">
					<p><span>作者:</span> {book.author}</p>
					{#if book.isbn}
						<p><span>ISBN:</span> {book.isbn}</p>
					{/if}
					{#if book.category_name}
						<p><span>分类:</span> <span class="category-tag">{book.category_name}</span></p>
					{/if}
					<p><span>库存:</span> <span class={book.stock > 0 ? 'in-stock' : 'out-of-stock'}>
						{book.stock > 0 ? `${book.stock} 件` : '缺货'}
					</span></p>
				</div>

				<div class="price-section">
					<span class="price-label">价格:</span>
					<span class="price-value">¥{book.price}</span>
				</div>

				<div class="action-section">
					<div class="quantity-control">
						<label>数量:</label>
						<div class="quantity-buttons">
							<button
								class="qty-btn"
								on:click={() => quantity = Math.max(1, quantity - 1)}
								disabled={quantity <= 1}
							>−</button>
							<input type="number" bind:value={quantity} min="1" max={book.stock} />
							<button
								class="qty-btn"
								on:click={() => quantity = Math.min(book.stock, quantity + 1)}
								disabled={quantity >= book.stock}
							>+</button>
						</div>
					</div>

					<button
						class="add-cart-btn-large"
						on:click={addToCart}
						disabled={book.stock <= 0}
					>
						加入购物车
					</button>
				</div>

				{#if book.description}
					<div class="description-section">
						<h3>内容简介</h3>
						<p>{book.description}</p>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	.loading,
	.error {
		text-align: center;
		padding: 100px 20px;
		font-size: 18px;
		color: #666;
	}

	.error {
		color: #ff6b6b;
	}

	.back-link {
		display: inline-block;
		margin-top: 20px;
		color: #667eea;
		text-decoration: none;
	}

	.back-link:hover {
		text-decoration: underline;
	}

	.breadcrumb {
		margin-bottom: 30px;
		font-size: 14px;
		color: #666;
	}

	.breadcrumb a {
		color: #667eea;
		text-decoration: none;
	}

	.breadcrumb a:hover {
		text-decoration: underline;
	}

	.breadcrumb span {
		margin: 0 8px;
	}

	.book-content {
		display: flex;
		gap: 40px;
		flex-wrap: wrap;
	}

	.book-cover-large {
		width: 300px;
		height: 420px;
		background: #f0f0f0;
		border-radius: 10px;
		overflow: hidden;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
	}

	.book-cover-large img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.no-cover-large {
		font-size: 100px;
		color: #ccc;
	}

	.book-info-large {
		flex: 1;
		min-width: 300px;
	}

	.book-info-large h1 {
		margin: 0 0 20px 0;
		font-size: 28px;
		color: #333;
	}

	.book-meta {
		margin-bottom: 30px;
	}

	.book-meta p {
		margin: 10px 0;
		font-size: 15px;
		color: #555;
	}

	.book-meta span:first-child {
		font-weight: 500;
		color: #333;
		margin-right: 10px;
	}

	.category-tag {
		background: #e8f0fe;
		color: #667eea;
		padding: 4px 10px;
		border-radius: 4px;
		font-size: 13px;
	}

	.in-stock {
		color: #27ae60;
		font-weight: 500;
	}

	.out-of-stock {
		color: #ff6b6b;
		font-weight: 500;
	}

	.price-section {
		display: flex;
		align-items: center;
		margin-bottom: 30px;
		padding: 20px;
		background: #f8f9fa;
		border-radius: 10px;
	}

	.price-label {
		font-size: 16px;
		color: #666;
		margin-right: 15px;
	}

	.price-value {
		font-size: 32px;
		font-weight: bold;
		color: #ff6b6b;
	}

	.action-section {
		display: flex;
		align-items: center;
		gap: 20px;
		flex-wrap: wrap;
		margin-bottom: 30px;
	}

	.quantity-control {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.quantity-control label {
		font-weight: 500;
		color: #555;
	}

	.quantity-buttons {
		display: flex;
		align-items: center;
		border: 1px solid #ddd;
		border-radius: 5px;
		overflow: hidden;
	}

	.qty-btn {
		width: 36px;
		height: 36px;
		background: #f8f9fa;
		border: none;
		font-size: 18px;
		cursor: pointer;
		transition: background 0.2s;
	}

	.qty-btn:hover:not(:disabled) {
		background: #e9ecef;
	}

	.qty-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.quantity-buttons input {
		width: 50px;
		height: 36px;
		text-align: center;
		border: none;
		font-size: 16px;
		-moz-appearance: textfield;
	}

	.quantity-buttons input::-webkit-outer-spin-button,
	.quantity-buttons input::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	.add-cart-btn-large {
		padding: 15px 40px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 5px;
		font-size: 16px;
		font-weight: 500;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.add-cart-btn-large:hover:not(:disabled) {
		opacity: 0.9;
	}

	.add-cart-btn-large:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	.description-section {
		margin-top: 40px;
		padding-top: 30px;
		border-top: 1px solid #eee;
	}

	.description-section h3 {
		margin: 0 0 15px 0;
		font-size: 18px;
		color: #333;
	}

	.description-section p {
		margin: 0;
		line-height: 1.8;
		color: #555;
	}
</style>
