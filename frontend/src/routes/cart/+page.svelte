<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let cart = null;
	let loading = true;
	let error = '';

	async function loadCart() {
		loading = true;
		error = '';
		try {
			cart = await api.getCart();
		} catch (e) {
			error = e.message || '加载购物车失败';
		} finally {
			loading = false;
		}
	}

	async function updateQuantity(item, newQuantity) {
		if (newQuantity < 1) return;
		if (newQuantity > item.book_stock) {
			alert(`库存不足，当前库存: ${item.book_stock}`);
			return;
		}

		try {
			cart = await api.updateCartItem(item.id, newQuantity);
		} catch (e) {
			alert('更新失败: ' + e.message);
		}
	}

	async function removeItem(item) {
		if (!confirm('确定要删除此商品吗？')) return;

		try {
			cart = await api.removeFromCart(item.id);
		} catch (e) {
			alert('删除失败: ' + e.message);
		}
	}

	function goToCheckout() {
		goto('/checkout');
	}

	onMount(() => {
		loadCart();
	});
</script>

<div class="page-header">
	<h1>🛒 购物车</h1>
</div>

{#if loading}
	<div class="loading">加载中...</div>
{:else if error}
	<div class="error">{error}</div>
{:else if !cart.items || cart.items.length === 0}
	<div class="empty-cart">
		<div class="empty-icon">🛒</div>
		<h2>购物车是空的</h2>
		<p>快去挑选喜欢的图书吧！</p>
		<a href="/" class="continue-btn">继续购物</a>
	</div>
{:else}
	<div class="cart-content">
		<div class="cart-items">
			{#each cart.items as item}
				<div class="cart-item">
					<div class="item-cover">
						{#if item.book_cover}
							<img src={item.book_cover} alt={item.book_title} />
						{:else}
							<div class="no-cover">📖</div>
						{/if}
					</div>

					<div class="item-info">
						<h3 class="item-title" on:click={() => goto(`/book/${item.book_id}`)}>
							{item.book_title}
						</h3>
						<p class="item-author">作者: {item.book_author}</p>
						<p class="item-price">单价: ¥{item.book_price}</p>
					</div>

					<div class="item-quantity">
						<div class="quantity-buttons">
							<button
								class="qty-btn"
								on:click={() => updateQuantity(item, item.quantity - 1)}
								disabled={item.quantity <= 1}
							>−</button>
							<span class="qty-value">{item.quantity}</span>
							<button
								class="qty-btn"
								on:click={() => updateQuantity(item, item.quantity + 1)}
								disabled={item.quantity >= item.book_stock}
							>+</button>
						</div>
						<p class="stock-info">库存: {item.book_stock}</p>
					</div>

					<div class="item-subtotal">
						<span class="subtotal-label">小计</span>
						<span class="subtotal-value">¥{item.subtotal}</span>
					</div>

					<div class="item-actions">
						<button class="remove-btn" on:click={() => removeItem(item)}>删除</button>
					</div>
				</div>
			{/each}
		</div>

		<div class="cart-summary">
			<h3>订单摘要</h3>
			<div class="summary-row">
				<span>商品数量</span>
				<span>{cart.total_items} 件</span>
			</div>
			<div class="summary-row total">
				<span>总计</span>
				<span class="total-price">¥{cart.total_price}</span>
			</div>
			<button class="checkout-btn" on:click={goToCheckout}>去结算</button>
			<a href="/" class="continue-shopping">继续购物</a>
		</div>
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

	.empty-cart {
		text-align: center;
		padding: 80px 20px;
	}

	.empty-icon {
		font-size: 80px;
		margin-bottom: 20px;
	}

	.empty-cart h2 {
		margin: 0 0 10px 0;
		color: #333;
	}

	.empty-cart p {
		margin: 0 0 30px 0;
		color: #666;
	}

	.continue-btn {
		display: inline-block;
		padding: 12px 30px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		text-decoration: none;
		border-radius: 5px;
		font-weight: 500;
	}

	.cart-content {
		display: flex;
		gap: 30px;
		flex-wrap: wrap;
	}

	.cart-items {
		flex: 1;
		min-width: 300px;
	}

	.cart-item {
		display: flex;
		align-items: center;
		background: white;
		padding: 20px;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		margin-bottom: 15px;
		gap: 20px;
		flex-wrap: wrap;
	}

	.item-cover {
		width: 80px;
		height: 110px;
		background: #f0f0f0;
		border-radius: 5px;
		overflow: hidden;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.item-cover img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.no-cover {
		font-size: 30px;
		color: #ccc;
	}

	.item-info {
		flex: 1;
		min-width: 150px;
	}

	.item-title {
		margin: 0 0 8px 0;
		font-size: 16px;
		color: #333;
		cursor: pointer;
	}

	.item-title:hover {
		color: #667eea;
	}

	.item-author {
		margin: 0 0 5px 0;
		font-size: 13px;
		color: #666;
	}

	.item-price {
		margin: 0;
		font-size: 14px;
		color: #555;
	}

	.item-quantity {
		text-align: center;
	}

	.quantity-buttons {
		display: flex;
		align-items: center;
		border: 1px solid #ddd;
		border-radius: 5px;
		overflow: hidden;
	}

	.qty-btn {
		width: 32px;
		height: 32px;
		background: #f8f9fa;
		border: none;
		font-size: 16px;
		cursor: pointer;
	}

	.qty-btn:hover:not(:disabled) {
		background: #e9ecef;
	}

	.qty-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.qty-value {
		width: 40px;
		text-align: center;
		font-size: 14px;
		font-weight: 500;
	}

	.stock-info {
		margin: 8px 0 0 0;
		font-size: 12px;
		color: #888;
	}

	.item-subtotal {
		text-align: center;
		min-width: 100px;
	}

	.subtotal-label {
		display: block;
		font-size: 12px;
		color: #888;
		margin-bottom: 5px;
	}

	.subtotal-value {
		font-size: 18px;
		font-weight: bold;
		color: #ff6b6b;
	}

	.item-actions {
		flex-shrink: 0;
	}

	.remove-btn {
		padding: 8px 16px;
		background: #fff;
		color: #ff6b6b;
		border: 1px solid #ff6b6b;
		border-radius: 5px;
		cursor: pointer;
		font-size: 13px;
	}

	.remove-btn:hover {
		background: #fff5f5;
	}

	.cart-summary {
		width: 300px;
		background: white;
		padding: 25px;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		height: fit-content;
		position: sticky;
		top: 20px;
	}

	.cart-summary h3 {
		margin: 0 0 20px 0;
		font-size: 18px;
		color: #333;
		border-bottom: 1px solid #eee;
		padding-bottom: 15px;
	}

	.summary-row {
		display: flex;
		justify-content: space-between;
		margin-bottom: 15px;
		font-size: 14px;
		color: #666;
	}

	.summary-row.total {
		margin-top: 20px;
		padding-top: 15px;
		border-top: 1px solid #eee;
		font-size: 16px;
		font-weight: 500;
		color: #333;
	}

	.total-price {
		font-size: 24px;
		color: #ff6b6b;
		font-weight: bold;
	}

	.checkout-btn {
		width: 100%;
		padding: 15px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 5px;
		font-size: 16px;
		font-weight: 500;
		cursor: pointer;
		margin: 20px 0 15px;
	}

	.checkout-btn:hover {
		opacity: 0.9;
	}

	.continue-shopping {
		display: block;
		text-align: center;
		color: #667eea;
		text-decoration: none;
		font-size: 14px;
	}

	.continue-shopping:hover {
		text-decoration: underline;
	}
</style>
