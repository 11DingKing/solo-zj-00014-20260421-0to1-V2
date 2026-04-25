<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let book = null;
	let loading = true;
	let error = '';
	let quantity = 1;

	let reviews = [];
	let reviewsPage = 1;
	let hasMoreReviews = false;
	let loadingReviews = false;
	let hasReviewed = false;
	let myReview = null;
	let reviewRating = 5;
	let reviewContent = '';
	let submittingReview = false;

	async function loadBook() {
		loading = true;
		error = '';
		try {
			book = await api.getBook($page.params.id);
			await Promise.all([loadReviews(), checkMyReview()]);
		} catch (e) {
			error = e.message || '加载图书失败';
		} finally {
			loading = false;
		}
	}

	async function loadReviews(pageNum = 1, append = false) {
		loadingReviews = true;
		try {
			const result = await api.getReviewsByBook($page.params.id, pageNum);
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

	async function checkMyReview() {
		try {
			const result = await api.getMyReview($page.params.id);
			hasReviewed = result.has_review;
			myReview = result.review;
		} catch (e) {
			console.error('检查我的评价失败:', e);
		}
	}

	async function submitReview() {
		if (reviewRating < 1 || reviewRating > 5) {
			alert('请选择 1-5 星评分');
			return;
		}

		submittingReview = true;
		try {
			await api.submitReview($page.params.id, reviewRating, reviewContent);
			alert('评价提交成功');
			await Promise.all([loadBook(), refreshBookStats()]);
		} catch (e) {
			alert('提交失败: ' + e.message);
		} finally {
			submittingReview = false;
		}
	}

	async function deleteReview(reviewId) {
		if (!confirm('确定要删除这条评价吗？')) return;

		try {
			await api.deleteReview(reviewId);
			alert('删除成功');
			await Promise.all([loadReviews(), checkMyReview(), refreshBookStats()]);
		} catch (e) {
			alert('删除失败: ' + e.message);
		}
	}

	async function refreshBookStats() {
		try {
			const updatedBook = await api.getBook($page.params.id);
			book.average_rating = updatedBook.average_rating;
			book.review_count = updatedBook.review_count;
		} catch (e) {
			console.error('刷新图书统计失败:', e);
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

	function renderStars(rating, interactive = false) {
		let stars = [];
		for (let i = 1; i <= 5; i++) {
			stars.push({
				filled: i <= rating,
				value: i
			});
		}
		return stars;
	}

	$: stars = renderStars(reviewRating);

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

				<div class="rating-summary">
					<div class="stars-display">
						{#each renderStars(Math.round(book.average_rating || 0)) as star}
							<span class={star.filled ? 'star-filled' : 'star-empty'}>★</span>
						{/each}
					</div>
					<span class="rating-value">{book.average_rating || '-'}</span>
					<span class="review-count">({book.review_count || 0} 条评价)</span>
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

		<div class="reviews-section">
			<h2>用户评价</h2>

			<div class="review-form-section">
				{#if hasReviewed}
					<div class="already-reviewed">
						<span class="check-icon">✓</span>
						<span>您已评价过该书籍</span>
					</div>
				{:else}
					<h3>发表评价</h3>
					<div class="review-form">
						<div class="form-group">
							<label>评分:</label>
							<div class="star-rating">
								{#each stars as star, i}
									<button
										type="button"
										class={star.filled ? 'star-btn star-btn-filled' : 'star-btn'}
										on:click={() => reviewRating = i + 1}
									>★</button>
								{/each}
								<span class="rating-text">{reviewRating} 星</span>
							</div>
						</div>
						<div class="form-group">
							<label>评价内容:</label>
							<textarea
								bind:value={reviewContent}
								placeholder="分享您对这本书的看法..."
								rows="4"
							></textarea>
						</div>
						<button
							class="submit-review-btn"
							on:click={submitReview}
							disabled={submittingReview}
						>
							{submittingReview ? '提交中...' : '提交评价'}
						</button>
					</div>
				{/if}
			</div>

			<div class="reviews-list">
				{#if reviews.length === 0 && !loadingReviews}
					<div class="no-reviews">暂无评价</div>
				{:else}
					{#each reviews as review}
						<div class="review-item">
							<div class="review-header">
								<div class="review-stars">
									{#each renderStars(review.rating) as star}
										<span class={star.filled ? 'star-filled' : 'star-empty'}>★</span>
									{/each}
								</div>
								<span class="review-date">{formatDate(review.created_at)}</span>
								{#if review.is_owner}
									<button
										class="delete-review-btn"
										on:click={() => deleteReview(review.id)}
									>删除</button>
								{/if}
							</div>
							{#if review.content}
								<div class="review-content">{review.content}</div>
							{/if}
						</div>
					{/each}

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
		margin-bottom: 20px;
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

	.rating-summary {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 20px;
	}

	.stars-display .star-filled {
		color: #ffc107;
		font-size: 18px;
	}

	.stars-display .star-empty {
		color: #ddd;
		font-size: 18px;
	}

	.rating-value {
		font-size: 18px;
		font-weight: bold;
		color: #ffc107;
	}

	.review-count {
		font-size: 14px;
		color: #666;
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

	.reviews-section {
		margin-top: 60px;
		padding-top: 40px;
		border-top: 2px solid #f0f0f0;
	}

	.reviews-section h2 {
		margin: 0 0 30px 0;
		font-size: 24px;
		color: #333;
	}

	.review-form-section {
		background: #f8f9fa;
		padding: 25px;
		border-radius: 10px;
		margin-bottom: 30px;
	}

	.review-form-section h3 {
		margin: 0 0 20px 0;
		font-size: 18px;
		color: #333;
	}

	.already-reviewed {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 15px 20px;
		background: #e8f5e9;
		color: #2e7d32;
		border-radius: 8px;
	}

	.check-icon {
		font-size: 18px;
		font-weight: bold;
	}

	.review-form .form-group {
		margin-bottom: 20px;
	}

	.review-form .form-group label {
		display: block;
		margin-bottom: 10px;
		font-weight: 500;
		color: #333;
	}

	.star-rating {
		display: flex;
		align-items: center;
		gap: 5px;
	}

	.star-btn {
		background: none;
		border: none;
		font-size: 28px;
		color: #ddd;
		cursor: pointer;
		padding: 0;
		transition: color 0.2s;
	}

	.star-btn:hover,
	.star-btn-filled {
		color: #ffc107;
	}

	.rating-text {
		margin-left: 10px;
		font-size: 14px;
		color: #666;
	}

	.review-form textarea {
		width: 100%;
		padding: 12px;
		border: 1px solid #ddd;
		border-radius: 5px;
		font-size: 14px;
		resize: vertical;
		box-sizing: border-box;
	}

	.review-form textarea:focus {
		outline: none;
		border-color: #667eea;
	}

	.submit-review-btn {
		padding: 12px 30px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 5px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.submit-review-btn:hover:not(:disabled) {
		opacity: 0.9;
	}

	.submit-review-btn:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	.reviews-list {
		margin-top: 20px;
	}

	.no-reviews {
		text-align: center;
		padding: 40px;
		color: #999;
		font-size: 16px;
	}

	.review-item {
		padding: 20px 0;
		border-bottom: 1px solid #eee;
	}

	.review-item:last-child {
		border-bottom: none;
	}

	.review-header {
		display: flex;
		align-items: center;
		gap: 15px;
		margin-bottom: 10px;
	}

	.review-stars .star-filled {
		color: #ffc107;
		font-size: 16px;
	}

	.review-stars .star-empty {
		color: #ddd;
		font-size: 16px;
	}

	.review-date {
		font-size: 13px;
		color: #999;
	}

	.delete-review-btn {
		margin-left: auto;
		padding: 4px 12px;
		background: #fff5f5;
		color: #ff6b6b;
		border: none;
		border-radius: 4px;
		font-size: 13px;
		cursor: pointer;
		transition: background 0.2s;
	}

	.delete-review-btn:hover {
		background: #ffe0e0;
	}

	.review-content {
		font-size: 14px;
		line-height: 1.6;
		color: #555;
	}

	.load-more-container {
		text-align: center;
		margin-top: 30px;
	}

	.load-more-btn {
		padding: 12px 40px;
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
</style>
