<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let cart = null;
	let loading = true;
	let error = '';
	let submitting = false;

	let shipping_address = '';
	let contact_name = '';
	let contact_phone = '';

	async function loadCart() {
		loading = true;
		error = '';
		try {
			cart = await api.getCart();
			if (!cart.items || cart.items.length === 0) {
				goto('/cart');
			}
		} catch (e) {
			error = e.message || '加载购物车失败';
		} finally {
			loading = false;
		}
	}

	async function submitOrder() {
		if (!shipping_address.trim()) {
			alert('请输入收货地址');
			return;
		}
		if (!contact_name.trim()) {
			alert('请输入联系人姓名');
			return;
		}
		if (!contact_phone.trim()) {
			alert('请输入联系电话');
			return;
		}

		submitting = true;
		try {
			const order = await api.createOrder({
				shipping_address: shipping_address.trim(),
				contact_name: contact_name.trim(),
				contact_phone: contact_phone.trim()
			});
			alert('订单创建成功！');
			goto(`/orders`);
		} catch (e) {
			alert('下单失败: ' + e.message);
		} finally {
			submitting = false;
		}
	}

	onMount(() => {
		loadCart();
	});
</script>

<div class="page-header">
	<h1>📝 确认订单</h1>
</div>

{#if loading}
	<div class="loading">加载中...</div>
{:else if error}
	<div class="error">{error}</div>
{:else}
	<div class="checkout-content">
		<div class="checkout-form">
			<h3>收货信息</h3>
			<div class="form-group">
				<label>收件人姓名 *</label>
				<input
					type="text"
					bind:value={contact_name}
					placeholder="请输入收件人姓名"
					disabled={submitting}
				/>
			</div>
			<div class="form-group">
				<label>联系电话 *</label>
				<input
					type="text"
					bind:value={contact_phone}
					placeholder="请输入联系电话"
					disabled={submitting}
				/>
			</div>
			<div class="form-group">
				<label>收货地址 *</label>
				<textarea
					bind:value={shipping_address}
					placeholder="请输入详细收货地址"
					rows="3"
					disabled={submitting}
				/>
			</div>
		</div>

		<div class="checkout-summary">
			<h3>订单商品</h3>
			<div class="order-items">
				{#each cart.items as item}
					<div class="order-item">
						<div class="item-info">
							<span class="item-name">{item.book_title}</span>
							<span class="item-qty">x {item.quantity}</span>
						</div>
						<span class="item-price">¥{item.subtotal}</span>
					</div>
				{/each}
			</div>

			<div class="summary-row">
				<span>商品数量</span>
				<span>{cart.total_items} 件</span>
			</div>

			<div class="summary-row total">
				<span>应付金额</span>
				<span class="total-price">¥{cart.total_price}</span>
			</div>

			<button class="submit-btn" on:click={submitOrder} disabled={submitting}>
				{submitting ? '提交中...' : '确认下单'}
			</button>

			<a href="/cart" class="back-link">返回购物车</a>
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

	.checkout-content {
		display: flex;
		gap: 30px;
		flex-wrap: wrap;
	}

	.checkout-form {
		flex: 1;
		min-width: 300px;
		background: white;
		padding: 25px;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
	}

	.checkout-form h3,
	.checkout-summary h3 {
		margin: 0 0 20px 0;
		font-size: 18px;
		color: #333;
		border-bottom: 1px solid #eee;
		padding-bottom: 15px;
	}

	.form-group {
		margin-bottom: 20px;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: 500;
		color: #555;
		font-size: 14px;
	}

	.form-group input,
	.form-group textarea {
		width: 100%;
		padding: 12px 15px;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		box-sizing: border-box;
	}

	.form-group input:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #667eea;
	}

	.form-group input:disabled,
	.form-group textarea:disabled {
		background: #f8f9fa;
	}

	.checkout-summary {
		width: 350px;
		background: white;
		padding: 25px;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		height: fit-content;
		position: sticky;
		top: 20px;
	}

	.order-items {
		margin-bottom: 20px;
		max-height: 300px;
		overflow-y: auto;
	}

	.order-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px 0;
		border-bottom: 1px solid #f0f0f0;
	}

	.order-item:last-child {
		border-bottom: none;
	}

	.item-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.item-name {
		font-size: 14px;
		color: #333;
	}

	.item-qty {
		font-size: 12px;
		color: #888;
	}

	.item-price {
		font-size: 14px;
		font-weight: 500;
		color: #333;
	}

	.summary-row {
		display: flex;
		justify-content: space-between;
		margin-bottom: 12px;
		font-size: 14px;
		color: #666;
	}

	.summary-row.total {
		margin-top: 15px;
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

	.submit-btn {
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

	.submit-btn:hover:not(:disabled) {
		opacity: 0.9;
	}

	.submit-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.back-link {
		display: block;
		text-align: center;
		color: #667eea;
		text-decoration: none;
		font-size: 14px;
	}

	.back-link:hover {
		text-decoration: underline;
	}
</style>
