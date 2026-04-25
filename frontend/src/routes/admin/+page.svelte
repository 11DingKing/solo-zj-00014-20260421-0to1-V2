<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let activeTab = 'books';

	let categories = [];
	let books = [];
	let loading = true;
	let error = '';

	let showModal = false;
	let editingBook = null;

	let formData = {
		title: '',
		author: '',
		isbn: '',
		price: '',
		stock: 0,
		category: '',
		cover_url: '',
		description: ''
	};

	let reviews = [];
	let reviewsPage = 1;
	let hasMoreReviews = false;
	let loadingReviews = false;

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
			const result = await api.getBooks();
			books = result.results || result;
		} catch (e) {
			error = e.message || '加载图书失败';
		} finally {
			loading = false;
		}
	}

	async function loadReviews(pageNum = 1, append = false) {
		loadingReviews = true;
		try {
			const result = await api.getAllReviews({ page: pageNum });
			if (append) {
				reviews = [...reviews, ...result.results];
			} else {
				reviews = result.results;
			}
			hasMoreReviews = !!result.next;
			reviewsPage = pageNum;
		} catch (e) {
			console.error('加载评价失败:', e);
		} finally {
			loadingReviews = false;
		}
	}

	async function loadMoreReviews() {
		if (!hasMoreReviews || loadingReviews) return;
		await loadReviews(reviewsPage + 1, true);
	}

	function openAddModal() {
		editingBook = null;
		formData = {
			title: '',
			author: '',
			isbn: '',
			price: '',
			stock: 0,
			category: '',
			cover_url: '',
			description: ''
		};
		showModal = true;
	}

	function openEditModal(book) {
		editingBook = book;
		formData = {
			title: book.title,
			author: book.author,
			isbn: book.isbn || '',
			price: book.price.toString(),
			stock: book.stock,
			category: book.category?.toString() || '',
			cover_url: book.cover_url || '',
			description: book.description || ''
		};
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		editingBook = null;
	}

	async function submitForm() {
		if (!formData.title.trim()) {
			alert('请输入书名');
			return;
		}
		if (!formData.author.trim()) {
			alert('请输入作者');
			return;
		}
		if (!formData.price || parseFloat(formData.price) <= 0) {
			alert('请输入有效的价格');
			return;
		}

		try {
			const data = {
				...formData,
				price: parseFloat(formData.price),
				category: formData.category ? parseInt(formData.category) : null
			};

			if (editingBook) {
				await api.updateBook(editingBook.id, data);
				alert('更新成功');
			} else {
				await api.createBook(data);
				alert('添加成功');
			}

			closeModal();
			loadBooks();
		} catch (e) {
			alert('操作失败: ' + e.message);
		}
	}

	async function deleteBook(book) {
		if (!confirm(`确定要删除图书《${book.title}》吗？`)) return;

		try {
			await api.deleteBook(book.id);
			alert('删除成功');
			loadBooks();
		} catch (e) {
			alert('删除失败: ' + e.message);
		}
	}

	async function deleteReview(review) {
		if (!confirm(`确定要删除这条评价吗？\n书籍: ${review.book_title}\n评分: ${review.rating}星`)) return;

		try {
			await api.adminDeleteReview(review.id);
			alert('删除成功');
			loadReviews();
		} catch (e) {
			alert('删除失败: ' + e.message);
		}
	}

	function formatDate(dateStr) {
		const date = new Date(dateStr);
		return date.toLocaleDateString('zh-CN', {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function renderStars(rating) {
		let stars = '';
		for (let i = 1; i <= 5; i++) {
			stars += i <= rating ? '★' : '☆';
		}
		return stars;
	}

	function switchTab(tab) {
		activeTab = tab;
		if (tab === 'reviews' && reviews.length === 0) {
			loadReviews();
		}
	}

	onMount(() => {
		loadCategories();
		loadBooks();
	});
</script>

<div class="page-header">
	<h1>⚙️ 后台管理</h1>
	<div class="header-actions">
		{#if activeTab === 'books'}
			<button class="btn-primary" on:click={openAddModal}>添加图书</button>
		{/if}
	</div>
</div>

<div class="admin-tabs">
	<button
		class={activeTab === 'books' ? 'tab-btn active' : 'tab-btn'}
		on:click={() => switchTab('books')}
	>
		📚 图书管理
	</button>
	<a href="/admin/categories" class="tab-btn">📂 分类管理</a>
	<a href="/admin/orders" class="tab-btn">📦 订单管理</a>
	<button
		class={activeTab === 'reviews' ? 'tab-btn active' : 'tab-btn'}
		on:click={() => switchTab('reviews')}
	>
		⭐ 评价管理
	</button>
</div>

{#if activeTab === 'books'}
	{#if loading}
		<div class="loading">加载中...</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else}
		<div class="books-table-container">
			<table class="books-table">
				<thead>
					<tr>
						<th>封面</th>
						<th>书名</th>
						<th>作者</th>
						<th>分类</th>
						<th>价格</th>
						<th>库存</th>
						<th>操作</th>
					</tr>
				</thead>
				<tbody>
					{#each books as book}
						<tr>
							<td>
								<div class="thumb">
									{#if book.cover_url}
										<img src={book.cover_url} alt={book.title} />
									{:else}
										<span>📖</span>
									{/if}
								</div>
							</td>
							<td class="title-col">{book.title}</td>
							<td>{book.author}</td>
							<td>{book.category_name || '-'}</td>
							<td class="price-col">¥{book.price}</td>
							<td>
								<span class={book.stock > 0 ? 'in-stock' : 'out-of-stock'}>
									{book.stock}
								</span>
							</td>
							<td>
								<button class="btn-edit" on:click={() => openEditModal(book)}>编辑</button>
								<button class="btn-delete" on:click={() => deleteBook(book)}>删除</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			{#if books.length === 0}
				<div class="empty">暂无图书</div>
			{/if}
		</div>
	{/if}
{:else if activeTab === 'reviews'}
	{#if loadingReviews && reviews.length === 0}
		<div class="loading">加载中...</div>
	{:else}
		<div class="reviews-table-container">
			{#if reviews.length === 0}
				<div class="empty">暂无评价</div>
			{:else}
				<table class="reviews-table">
					<thead>
						<tr>
							<th>书籍</th>
							<th>评分</th>
							<th>评价内容</th>
							<th>创建时间</th>
							<th>用户会话ID</th>
							<th>操作</th>
						</tr>
					</thead>
					<tbody>
						{#each reviews as review}
							<tr>
								<td class="book-title-col">
									<div class="book-info">
										<div class="book-name">{review.book_title}</div>
										<div class="book-author">{review.book_author}</div>
									</div>
								</td>
								<td>
									<span class="stars-display">{renderStars(review.rating)}</span>
									<span class="rating-text">({review.rating}星)</span>
								</td>
								<td class="content-col">
									{review.content || '<span class="no-content">无评价内容</span>'}
								</td>
								<td class="date-col">{formatDate(review.created_at)}</td>
								<td class="session-col">{review.user_session_id.slice(0, 12)}...</td>
								<td>
									<button class="btn-delete" on:click={() => deleteReview(review)}>删除</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>

				{#if hasMoreReviews}
					<div class="load-more-container">
						<button
							class="load-more-btn"
							on:click={loadMoreReviews}
							disabled={loadingReviews}
						>
							{loadingReviews ? '加载中...' : '加载更多'}
						</button>
					</div>
				{/if}
			{/if}
		</div>
	{/if}
{/if}

{#if showModal}
	<div class="modal-overlay" on:click={(e) => e.target === e.currentTarget && closeModal()}>
		<div class="modal">
			<div class="modal-header">
				<h3>{editingBook ? '编辑图书' : '添加图书'}</h3>
				<button class="modal-close" on:click={closeModal}>×</button>
			</div>
			<div class="modal-body">
				<div class="form-grid">
					<div class="form-group full-width">
						<label>书名 *</label>
						<input type="text" bind:value={formData.title} placeholder="请输入书名" />
					</div>
					<div class="form-group">
						<label>作者 *</label>
						<input type="text" bind:value={formData.author} placeholder="请输入作者" />
					</div>
					<div class="form-group">
						<label>ISBN</label>
						<input type="text" bind:value={formData.isbn} placeholder="请输入ISBN" />
					</div>
					<div class="form-group">
						<label>价格 *</label>
						<input type="number" bind:value={formData.price} step="0.01" min="0" placeholder="请输入价格" />
					</div>
					<div class="form-group">
						<label>库存</label>
						<input type="number" bind:value={formData.stock} min="0" placeholder="请输入库存数量" />
					</div>
					<div class="form-group">
						<label>分类</label>
						<select bind:value={formData.category}>
							<option value="">请选择分类</option>
							{#each categories as category}
								<option value={category.id}>{category.name}</option>
							{/each}
						</select>
					</div>
					<div class="form-group full-width">
						<label>封面图片URL</label>
						<input type="text" bind:value={formData.cover_url} placeholder="请输入封面图片URL" />
					</div>
					<div class="form-group full-width">
						<label>简介</label>
						<textarea bind:value={formData.description} placeholder="请输入图书简介" rows="4" />
					</div>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" on:click={closeModal}>取消</button>
				<button class="btn-submit" on:click={submitForm}>
					{editingBook ? '保存' : '添加'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
		flex-wrap: wrap;
		gap: 15px;
	}

	.page-header h1 {
		margin: 0;
		color: #333;
	}

	.header-actions {
		display: flex;
		gap: 10px;
	}

	.admin-tabs {
		display: flex;
		gap: 5px;
		margin-bottom: 30px;
		border-bottom: 2px solid #f0f0f0;
		padding-bottom: 0;
	}

	.tab-btn {
		padding: 12px 24px;
		background: transparent;
		color: #666;
		border: none;
		border-bottom: 2px solid transparent;
		border-radius: 5px 5px 0 0;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
		margin-bottom: -2px;
		text-decoration: none;
	}

	.tab-btn:hover {
		color: #667eea;
		background: #f8f9fa;
	}

	.tab-btn.active {
		color: #667eea;
		border-bottom-color: #667eea;
		background: #f8f9fa;
	}

	.btn-primary {
		padding: 10px 20px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 5px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
	}

	.btn-secondary {
		padding: 10px 20px;
		background: #f8f9fa;
		color: #333;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
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

	.books-table-container,
	.reviews-table-container {
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		overflow: hidden;
	}

	.books-table,
	.reviews-table {
		width: 100%;
		border-collapse: collapse;
	}

	.books-table th,
	.books-table td,
	.reviews-table th,
	.reviews-table td {
		padding: 15px;
		text-align: left;
		border-bottom: 1px solid #f0f0f0;
	}

	.books-table th,
	.reviews-table th {
		background: #f8f9fa;
		font-weight: 500;
		color: #555;
		font-size: 13px;
		text-transform: uppercase;
	}

	.thumb {
		width: 50px;
		height: 65px;
		background: #f0f0f0;
		border-radius: 4px;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
	}

	.thumb img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.thumb span {
		font-size: 24px;
		color: #ccc;
	}

	.title-col {
		font-weight: 500;
		color: #333;
	}

	.book-title-col .book-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.book-name {
		font-weight: 500;
		color: #333;
	}

	.book-author {
		font-size: 12px;
		color: #999;
	}

	.price-col {
		font-weight: 500;
		color: #ff6b6b;
	}

	.in-stock {
		color: #27ae60;
		font-weight: 500;
	}

	.out-of-stock {
		color: #ff6b6b;
		font-weight: 500;
	}

	.stars-display {
		color: #ffc107;
		font-size: 16px;
	}

	.rating-text {
		margin-left: 5px;
		font-size: 13px;
		color: #666;
	}

	.content-col {
		max-width: 300px;
		color: #555;
		font-size: 13px;
		line-height: 1.5;
	}

	.no-content {
		color: #999;
		font-style: italic;
	}

	.date-col,
	.session-col {
		font-size: 12px;
		color: #999;
	}

	.btn-edit {
		padding: 6px 12px;
		background: #e8f0fe;
		color: #667eea;
		border: none;
		border-radius: 4px;
		font-size: 13px;
		cursor: pointer;
		margin-right: 8px;
	}

	.btn-delete {
		padding: 6px 12px;
		background: #fff5f5;
		color: #ff6b6b;
		border: none;
		border-radius: 4px;
		font-size: 13px;
		cursor: pointer;
	}

	.load-more-container {
		text-align: center;
		padding: 20px;
		border-top: 1px solid #f0f0f0;
	}

	.load-more-btn {
		padding: 10px 30px;
		background: #f8f9fa;
		color: #667eea;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.load-more-btn:hover:not(:disabled) {
		background: #e8f0fe;
		border-color: #667eea;
	}

	.load-more-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
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
		max-width: 700px;
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

	.form-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20px;
	}

	.form-group.full-width {
		grid-column: 1 / -1;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-size: 14px;
		font-weight: 500;
		color: #555;
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 10px 12px;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		box-sizing: border-box;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #667eea;
	}

	.modal-footer {
		padding: 15px 25px;
		border-top: 1px solid #eee;
		display: flex;
		justify-content: flex-end;
		gap: 10px;
	}

	.btn-cancel {
		padding: 10px 25px;
		background: #f8f9fa;
		color: #666;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		cursor: pointer;
	}

	.btn-submit {
		padding: 10px 25px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 5px;
		font-size: 14px;
		cursor: pointer;
	}
</style>
