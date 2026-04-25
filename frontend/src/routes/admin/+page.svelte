<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

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

	onMount(() => {
		loadCategories();
		loadBooks();
	});
</script>

<div class="page-header">
	<h1>⚙️ 后台管理 - 图书</h1>
	<div class="header-actions">
		<a href="/admin/categories" class="btn-secondary">分类管理</a>
		<a href="/admin/orders" class="btn-secondary">订单管理</a>
		<button class="btn-primary" on:click={openAddModal}>添加图书</button>
	</div>
</div>

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
		margin-bottom: 30px;
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

	.books-table-container {
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		overflow: hidden;
	}

	.books-table {
		width: 100%;
		border-collapse: collapse;
	}

	.books-table th,
	.books-table td {
		padding: 15px;
		text-align: left;
		border-bottom: 1px solid #f0f0f0;
	}

	.books-table th {
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
