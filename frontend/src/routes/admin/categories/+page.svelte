<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	let categories = [];
	let loading = true;
	let error = '';

	let showModal = false;
	let editingCategory = null;
	let categoryName = '';

	async function loadCategories() {
		loading = true;
		error = '';
		try {
			categories = await api.getCategories();
		} catch (e) {
			error = e.message || '加载分类失败';
		} finally {
			loading = false;
		}
	}

	function openAddModal() {
		editingCategory = null;
		categoryName = '';
		showModal = true;
	}

	function openEditModal(category) {
		editingCategory = category;
		categoryName = category.name;
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		editingCategory = null;
		categoryName = '';
	}

	async function submitForm() {
		if (!categoryName.trim()) {
			alert('请输入分类名称');
			return;
		}

		try {
			if (editingCategory) {
				await api.updateCategory(editingCategory.id, { name: categoryName.trim() });
				alert('更新成功');
			} else {
				await api.createCategory({ name: categoryName.trim() });
				alert('添加成功');
			}

			closeModal();
			loadCategories();
		} catch (e) {
			alert('操作失败: ' + e.message);
		}
	}

	async function deleteCategory(category) {
		if (!confirm(`确定要删除分类"${category.name}"吗？\n注意：删除分类后，关联该分类的图书分类将被清空。`)) return;

		try {
			await api.deleteCategory(category.id);
			alert('删除成功');
			loadCategories();
		} catch (e) {
			alert('删除失败: ' + e.message);
		}
	}

	onMount(() => {
		loadCategories();
	});
</script>

<div class="page-header">
	<h1>📂 分类管理</h1>
	<div class="header-actions">
		<a href="/admin" class="btn-secondary">返回图书管理</a>
		<a href="/admin/orders" class="btn-secondary">订单管理</a>
		<button class="btn-primary" on:click={openAddModal}>添加分类</button>
	</div>
</div>

{#if loading}
	<div class="loading">加载中...</div>
{:else if error}
	<div class="error">{error}</div>
{:else}
	<div class="categories-container">
		{#if categories.length === 0}
			<div class="empty">
				<div class="empty-icon">📂</div>
				<h2>暂无分类</h2>
				<p>点击上方按钮添加第一个分类</p>
			</div>
		{:else}
			<div class="categories-grid">
				{#each categories as category}
					<div class="category-card">
						<div class="category-icon">📚</div>
						<h3 class="category-name">{category.name}</h3>
						<p class="category-meta">
							<small>创建于: {category.created_at || '未知'}</small>
						</p>
						<div class="category-actions">
							<button class="btn-edit" on:click={() => openEditModal(category)}>编辑</button>
							<button class="btn-delete" on:click={() => deleteCategory(category)}>删除</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/if}

{#if showModal}
	<div class="modal-overlay" on:click={(e) => e.target === e.currentTarget && closeModal()}>
		<div class="modal">
			<div class="modal-header">
				<h3>{editingCategory ? '编辑分类' : '添加分类'}</h3>
				<button class="modal-close" on:click={closeModal}>×</button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label>分类名称 *</label>
					<input
						type="text"
						bind:value={categoryName}
						placeholder="请输入分类名称"
						on:keydown={(e) => e.key === 'Enter' && submitForm()}
					/>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" on:click={closeModal}>取消</button>
				<button class="btn-submit" on:click={submitForm}>
					{editingCategory ? '保存' : '添加'}
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
		flex-wrap: wrap;
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

	.btn-primary:hover {
		opacity: 0.9;
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

	.btn-secondary:hover {
		background: #e9ecef;
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
		font-size: 60px;
		margin-bottom: 20px;
	}

	.empty h2 {
		margin: 0 0 10px 0;
		color: #333;
	}

	.empty p {
		margin: 0;
		color: #666;
	}

	.categories-container {
		width: 100%;
	}

	.categories-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 20px;
	}

	.category-card {
		background: white;
		border-radius: 10px;
		padding: 25px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
		transition: transform 0.3s ease, box-shadow 0.3s ease;
	}

	.category-card:hover {
		transform: translateY(-3px);
		box-shadow: 0 5px 20px rgba(0, 0, 0, 0.12);
	}

	.category-icon {
		font-size: 40px;
		text-align: center;
		margin-bottom: 15px;
	}

	.category-name {
		margin: 0 0 10px 0;
		font-size: 18px;
		color: #333;
		text-align: center;
	}

	.category-meta {
		margin: 0 0 15px 0;
		text-align: center;
	}

	.category-meta small {
		color: #999;
		font-size: 12px;
	}

	.category-actions {
		display: flex;
		justify-content: center;
		gap: 10px;
	}

	.btn-edit {
		padding: 8px 18px;
		background: #e8f0fe;
		color: #667eea;
		border: none;
		border-radius: 5px;
		font-size: 14px;
		cursor: pointer;
		transition: background 0.2s;
	}

	.btn-edit:hover {
		background: #d0e3ff;
	}

	.btn-delete {
		padding: 8px 18px;
		background: #fff5f5;
		color: #ff6b6b;
		border: none;
		border-radius: 5px;
		font-size: 14px;
		cursor: pointer;
		transition: background 0.2s;
	}

	.btn-delete:hover {
		background: #ffe0e0;
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
		max-width: 450px;
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

	.modal-close:hover {
		color: #666;
	}

	.modal-body {
		padding: 25px;
	}

	.form-group {
		width: 100%;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-size: 14px;
		font-weight: 500;
		color: #555;
	}

	.form-group input {
		width: 100%;
		padding: 12px 15px;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 15px;
		box-sizing: border-box;
	}

	.form-group input:focus {
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

	.btn-cancel:hover {
		background: #e9ecef;
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

	.btn-submit:hover {
		opacity: 0.9;
	}
</style>
