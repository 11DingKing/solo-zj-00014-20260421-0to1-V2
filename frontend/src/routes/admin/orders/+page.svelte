<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	let orders = [];
	let loading = true;
	let error = '';
	let selectedOrder = null;

	async function loadOrders() {
		loading = true;
		error = '';
		try {
			orders = await api.getOrders();
		} catch (e) {
			error = e.message || '加载订单失败';
		} finally {
			loading = false;
		}
	}

	async function loadOrderDetail(order) {
		try {
			selectedOrder = await api.getOrder(order.id);
		} catch (e) {
			alert('加载订单详情失败: ' + e.message);
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

	async function updateStatus(order, newStatus) {
		if (!confirm(`确定要将订单状态更新为"${getStatusText(newStatus)}"吗？`)) return;

		try {
			await api.updateOrderStatus(order.id, newStatus);
			alert('状态更新成功');
			order.status = newStatus;
			if (selectedOrder && selectedOrder.id === order.id) {
				selectedOrder.status = newStatus;
			}
		} catch (e) {
			alert('更新失败: ' + e.message);
		}
	}

	function getStatusText(status) {
		switch (status) {
			case 'pending': return '待支付';
			case 'paid': return '已支付';
			case 'shipped': return '已发货';
			case 'completed': return '已完成';
			default: return status;
		}
	}

	function closeDetail() {
		selectedOrder = null;
	}

	onMount(() => {
		loadOrders();
	});
</script>

<div class="page-header">
	<h1>📋 订单管理</h1>
	<a href="/admin" class="btn-secondary">返回图书管理</a>
</div>

{#if loading}
	<div class="loading">加载中...</div>
{:else if error}
	<div class="error">{error}</div>
{:else if orders.length === 0}
	<div class="empty">暂无订单</div>
{:else}
	<div class="orders-table-container">
		<table class="orders-table">
			<thead>
				<tr>
					<th>订单号</th>
					<th>收货人</th>
					<th>联系电话</th>
					<th>收货地址</th>
					<th>订单金额</th>
					<th>状态</th>
					<th>下单时间</th>
					<th>操作</th>
				</tr>
			</thead>
			<tbody>
				{#each orders as order}
					<tr>
						<td class="order-id">{order.order_number}</td>
						<td>{order.contact_name}</td>
						<td>{order.contact_phone}</td>
						<td class="address">{order.shipping_address}</td>
						<td class="price">¥{order.total_amount}</td>
						<td>
							<span class="order-status {getStatusClass(order.status)}">
								{order.status_display}
							</span>
						</td>
						<td class="time">{order.created_at}</td>
						<td>
							<button class="btn-view" on:click={() => loadOrderDetail(order)}>详情</button>
							<div class="status-actions">
								{#if order.status === 'pending'}
									<button class="btn-paid" on:click={() => updateStatus(order, 'paid')}>支付</button>
								{/if}
								{#if order.status === 'paid'}
									<button class="btn-ship" on:click={() => updateStatus(order, 'shipped')}>发货</button>
								{/if}
								{#if order.status === 'shipped'}
									<button class="btn-complete" on:click={() => updateStatus(order, 'completed')}>完成</button>
								{/if}
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#if selectedOrder}
	<div class="modal-overlay" on:click={(e) => e.target === e.currentTarget && closeDetail()}>
		<div class="modal">
			<div class="modal-header">
				<h3>订单详情</h3>
				<button class="modal-close" on:click={closeDetail}>×</button>
			</div>
			<div class="modal-body">
				<div class="order-detail-header">
					<div class="info-row">
						<span class="label">订单号:</span>
						<span>{selectedOrder.order_number}</span>
					</div>
					<div class="info-row">
						<span class="label">订单状态:</span>
						<span class="order-status {getStatusClass(selectedOrder.status)}">
							{selectedOrder.status_display}
						</span>
					</div>
				</div>

				<div class="detail-section">
					<h4>收货信息</h4>
					<div class="info-grid">
						<div class="info-row">
							<span class="label">收货人:</span>
							<span>{selectedOrder.contact_name}</span>
						</div>
						<div class="info-row">
							<span class="label">联系电话:</span>
							<span>{selectedOrder.contact_phone}</span>
						</div>
						<div class="info-row full-width">
							<span class="label">收货地址:</span>
							<span>{selectedOrder.shipping_address}</span>
						</div>
					</div>
				</div>

				<div class="detail-section">
					<h4>订单商品</h4>
					<div class="items-table">
						<div class="items-header">
							<span class="col-name">商品</span>
							<span class="col-price">单价</span>
							<span class="col-qty">数量</span>
							<span class="col-subtotal">小计</span>
						</div>
						{#each selectedOrder.items as item}
							<div class="items-row">
								<span class="col-name">{item.book_title}</span>
								<span class="col-price">¥{item.price}</span>
								<span class="col-qty">x {item.quantity}</span>
								<span class="col-subtotal">¥{item.subtotal}</span>
							</div>
						{/each}
					</div>
				</div>

				<div class="detail-section total-section">
					<div class="total-row">
						<span class="label">订单总金额:</span>
						<span class="value">¥{selectedOrder.total_amount}</span>
					</div>
				</div>

				<div class="detail-section">
					<div class="info-row">
						<span class="label">下单时间:</span>
						<span>{selectedOrder.created_at}</span>
					</div>
					{#if selectedOrder.updated_at}
						<div class="info-row">
							<span class="label">更新时间:</span>
							<span>{selectedOrder.updated_at}</span>
						</div>
					{/if}
				</div>

				<div class="status-update-section">
					<h4>更新订单状态</h4>
					<div class="status-buttons">
						{#if selectedOrder.status === 'pending'}
							<button class="status-btn paid" on:click={() => updateStatus(selectedOrder, 'paid')}>
								标记为已支付
							</button>
						{/if}
						{#if selectedOrder.status === 'paid'}
							<button class="status-btn shipped" on:click={() => updateStatus(selectedOrder, 'shipped')}>
								标记为已发货
							</button>
						{/if}
						{#if selectedOrder.status === 'shipped'}
							<button class="status-btn completed" on:click={() => updateStatus(selectedOrder, 'completed')}>
								标记为已完成
							</button>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30px;
		flex-wrap: wrap;
		gap: 15px;
	}

	.page-header h1 {
		margin: 0;
		color: #333;
	}

	.btn-secondary {
		padding: 10px 20px;
		background: #f8f9fa;
		color: #333;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		font-weight: 500;
		text-decoration: none;
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

	.orders-table-container {
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		overflow: hidden;
		overflow-x: auto;
	}

	.orders-table {
		width: 100%;
		border-collapse: collapse;
		min-width: 1000px;
	}

	.orders-table th,
	.orders-table td {
		padding: 15px;
		text-align: left;
		border-bottom: 1px solid #f0f0f0;
	}

	.orders-table th {
		background: #f8f9fa;
		font-weight: 500;
		color: #555;
		font-size: 13px;
		text-transform: uppercase;
		white-space: nowrap;
	}

	.order-id {
		font-weight: 500;
		color: #333;
		font-family: monospace;
	}

	.address {
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.price {
		font-weight: 500;
		color: #ff6b6b;
	}

	.time {
		font-size: 13px;
		color: #888;
		white-space: nowrap;
	}

	.order-status {
		padding: 4px 12px;
		border-radius: 20px;
		font-size: 12px;
		font-weight: 500;
		white-space: nowrap;
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

	.status-actions {
		margin-top: 5px;
	}

	.btn-view {
		padding: 6px 12px;
		background: #e8f0fe;
		color: #667eea;
		border: none;
		border-radius: 4px;
		font-size: 13px;
		cursor: pointer;
		margin-right: 8px;
	}

	.btn-paid,
	.btn-ship,
	.btn-complete {
		padding: 6px 10px;
		border: none;
		border-radius: 4px;
		font-size: 12px;
		cursor: pointer;
		margin-right: 5px;
	}

	.btn-paid {
		background: #d4edda;
		color: #155724;
	}

	.btn-ship {
		background: #cce5ff;
		color: #004085;
	}

	.btn-complete {
		background: #e2e3e5;
		color: #383d41;
	}

	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 20px;
	}

	.modal {
		background: white;
		border-radius: 10px;
		width: 100%;
		max-width: 600px;
		max-height: 90vh;
		overflow-y: auto;
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 25px;
		border-bottom: 1px solid #eee;
	}

	.modal-header h3 {
		margin: 0;
		font-size: 18px;
		color: #333;
	}

	.modal-close {
		background: none;
		border: none;
		font-size: 28px;
		color: #999;
		cursor: pointer;
		line-height: 1;
	}

	.modal-body {
		padding: 25px;
	}

	.order-detail-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 10px;
		margin-bottom: 20px;
	}

	.info-row {
		display: flex;
		gap: 8px;
		font-size: 14px;
	}

	.info-row .label {
		color: #666;
		flex-shrink: 0;
	}

	.info-row.full-width {
		grid-column: 1 / -1;
	}

	.detail-section {
		margin-bottom: 25px;
	}

	.detail-section h4 {
		margin: 0 0 15px 0;
		font-size: 15px;
		color: #333;
		border-bottom: 1px solid #f0f0f0;
		padding-bottom: 10px;
	}

	.info-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 10px;
	}

	.items-table {
		border: 1px solid #eee;
		border-radius: 5px;
		overflow: hidden;
	}

	.items-header {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr 1fr;
		background: #f8f9fa;
		padding: 10px 15px;
		font-weight: 500;
		font-size: 13px;
		color: #555;
	}

	.items-row {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr 1fr;
		padding: 12px 15px;
		border-top: 1px solid #f0f0f0;
		font-size: 14px;
	}

	.items-row:last-child {
		border-bottom: none;
	}

	.col-subtotal {
		font-weight: 500;
		color: #ff6b6b;
	}

	.total-section {
		text-align: right;
	}

	.total-row {
		display: inline-flex;
		align-items: center;
		gap: 10px;
	}

	.total-row .label {
		font-size: 16px;
		color: #333;
	}

	.total-row .value {
		font-size: 24px;
		font-weight: bold;
		color: #ff6b6b;
	}

	.status-update-section {
		margin-top: 20px;
		padding-top: 20px;
		border-top: 1px solid #eee;
	}

	.status-update-section h4 {
		margin: 0 0 15px 0;
		font-size: 15px;
		color: #333;
	}

	.status-buttons {
		display: flex;
		gap: 10px;
	}

	.status-btn {
		padding: 10px 20px;
		border: none;
		border-radius: 5px;
		font-size: 14px;
		cursor: pointer;
	}

	.status-btn.paid {
		background: #d4edda;
		color: #155724;
	}

	.status-btn.shipped {
		background: #cce5ff;
		color: #004085;
	}

	.status-btn.completed {
		background: #e2e3e5;
		color: #383d41;
	}
</style>
