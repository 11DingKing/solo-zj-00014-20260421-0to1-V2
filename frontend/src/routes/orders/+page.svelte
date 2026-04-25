<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let orders = [];
	let loading = true;
	let error = '';

	async function loadOrders() {
		loading = true;
		error = '';
		try {
			orders = await api.getMyOrders();
		} catch (e) {
			error = e.message || '加载订单失败';
		} finally {
			loading = false;
		}
	}

	function getStatusClass(status) {
		switch (status) {
			case 'pending': return 'status-pending';
			case 'paid': return 'status-paid';
			case 'shipped': return 'status-shipped';
			case 'completed': return 'status-completed';
			default: return '';
		}
	}

	onMount(() => {
		loadOrders();
	});
</script>

<div class="page-header">
	<h1>📋 我的订单</h1>
</div>

{#if loading}
	<div class="loading">加载中...</div>
{:else if error}
	<div class="error">{error}</div>
{:else if orders.length === 0}
	<div class="empty">
		<div class="empty-icon">📋</div>
		<h2>暂无订单</h2>
		<p>快去下单吧！</p>
		<a href="/" class="go-shopping">去购物</a>
	</div>
{:else}
	<div class="orders-list">
		{#each orders as order}
			<div class="order-card">
				<div class="order-header">
					<div class="order-id">
						<span class="label">订单号:</span>
						<span class="value">{order.order_number}</span>
					</div>
					<span class="order-status {getStatusClass(order.status)}">
						{order.status_display}
					</span>
				</div>
				<div class="order-info">
					<div class="info-row">
						<span class="label">收货人:</span>
						<span>{order.contact_name}</span>
					</div>
					<div class="info-row">
						<span class="label">联系电话:</span>
						<span>{order.contact_phone}</span>
					</div>
					<div class="info-row">
						<span class="label">收货地址:</span>
						<span>{order.shipping_address}</span>
					</div>
					<div class="info-row">
						<span class="label">下单时间:</span>
						<span>{order.created_at}</span>
					</div>
				</div>
				<div class="order-footer">
					<span class="order-amount">订单金额: <span class="amount">¥{order.total_amount}</span></span>
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

	.loading,
	.error,
	.empty {
		text-align: center;
		padding: 100px 20px;
		font-size: 18px;
		color: #666;
	}

	.error {
		color: #ff6b6b;
	}

	.empty-icon {
		font-size: 80px;
		margin-bottom: 20px;
	}

	.empty h2 {
		margin: 0 0 10px 0;
		color: #333;
	}

	.empty p {
		margin: 0 0 30px 0;
		color: #666;
	}

	.go-shopping {
		display: inline-block;
		padding: 12px 30px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		text-decoration: none;
		border-radius: 5px;
		font-weight: 500;
	}

	.orders-list {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.order-card {
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		overflow: hidden;
	}

	.order-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px 25px;
		background: #f8f9fa;
		border-bottom: 1px solid #eee;
		flex-wrap: wrap;
		gap: 10px;
	}

	.order-id .label {
		font-size: 14px;
		color: #666;
		margin-right: 5px;
	}

	.order-id .value {
		font-size: 14px;
		color: #333;
		font-weight: 500;
	}

	.order-status {
		padding: 6px 15px;
		border-radius: 20px;
		font-size: 13px;
		font-weight: 500;
	}

	.status-pending {
		background: #fff3cd;
		color: #856404;
	}

	.status-paid {
		background: #d4edda;
		color: #155724;
	}

	.status-shipped {
		background: #cce5ff;
		color: #004085;
	}

	.status-completed {
		background: #e2e3e5;
		color: #383d41;
	}

	.order-info {
		padding: 20px 25px;
	}

	.info-row {
		margin-bottom: 10px;
		font-size: 14px;
		display: flex;
		gap: 5px;
	}

	.info-row:last-child {
		margin-bottom: 0;
	}

	.info-row .label {
		color: #666;
		flex-shrink: 0;
	}

	.order-footer {
		padding: 15px 25px;
		background: #fafafa;
		border-top: 1px solid #eee;
		display: flex;
		justify-content: flex-end;
		align-items: center;
	}

	.order-amount {
		font-size: 14px;
		color: #666;
	}

	.amount {
		font-size: 20px;
		font-weight: bold;
		color: #ff6b6b;
		margin-left: 5px;
	}
</style>
