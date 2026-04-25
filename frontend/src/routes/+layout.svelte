<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	let cartCount = 0;

	async function loadCart() {
		try {
			const cart = await api.getCart();
			cartCount = cart.total_items || 0;
		} catch (e) {
			cartCount = 0;
		}
	}

	onMount(() => {
		loadCart();
	});

	function handleNavigate() {
		loadCart();
	}

	$: $page.url, handleNavigate();
</script>

<nav class="navbar">
	<div class="nav-container">
		<a href="/" class="nav-brand">📚 在线书店</a>
		<div class="nav-links">
			<a href="/" class:active={$page.url.pathname === '/'}>首页</a>
			<a href="/cart" class:active={$page.url.pathname === '/cart'}>
				购物车
				{#if cartCount > 0}
					<span class="cart-badge">{cartCount}</span>
				{/if}
			</a>
			<a href="/orders" class:active={$page.url.pathname === '/orders'}>我的订单</a>
			<a href="/admin" class:active={$page.url.pathname.startsWith('/admin')}>后台管理</a>
		</div>
	</div>
</nav>

<main class="main-content">
	<slot />
</main>

<style>
	.navbar {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 0;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
	}

	.nav-container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 20px;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.nav-brand {
		font-size: 1.5rem;
		font-weight: bold;
		color: white;
		text-decoration: none;
		padding: 15px 0;
	}

	.nav-links {
		display: flex;
		gap: 10px;
	}

	.nav-links a {
		color: rgba(255, 255, 255, 0.9);
		text-decoration: none;
		padding: 15px 20px;
		font-weight: 500;
		transition: all 0.3s ease;
		position: relative;
	}

	.nav-links a:hover,
	.nav-links a.active {
		color: white;
		background: rgba(255, 255, 255, 0.15);
	}

	.cart-badge {
		background: #ff6b6b;
		color: white;
		border-radius: 50%;
		padding: 2px 8px;
		font-size: 0.75rem;
		margin-left: 5px;
		position: absolute;
		top: 8px;
		right: 5px;
	}

	.main-content {
		max-width: 1200px;
		margin: 0 auto;
		padding: 30px 20px;
		min-height: calc(100vh - 80px);
	}
</style>
