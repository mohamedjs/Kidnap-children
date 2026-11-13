<template>
  <div class="dashboard-profile" v-cloak>
    <div class="feed-area">

      <!-- Page header -->
      <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:1.5rem;font-weight:800;color:#0F172A;margin:0 0 4px;display:flex;align-items:center;gap:10px;">
          <span style="background:linear-gradient(135deg,#FEF2F2,#FEE2E2);border:1px solid rgba(220,38,38,.2);border-radius:10px;width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;">
            <i class="fas fa-search" style="color:#DC2626;font-size:16px;" aria-hidden="true"></i>
          </span>
          Missing Children
        </h1>
        <p style="font-size:.875rem;color:#64748B;margin:0;">Active cases in the community — help by sharing and providing tips.</p>
      </div>

      <!-- Search & Filter Bar -->
      <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px;padding:16px;margin-bottom:1.5rem;box-shadow:0 1px 3px rgba(15,23,42,.06);">
        <form @submit.prevent="filter_post()" role="search" aria-label="Search missing children">
          <div style="display:grid;grid-template-columns:1fr auto auto auto;gap:10px;align-items:center;flex-wrap:wrap;">

            <!-- Text search -->
            <div style="position:relative;">
              <i class="fas fa-search" style="position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#94A3B8;font-size:13px;" aria-hidden="true"></i>
              <input
                type="search"
                v-model="filter.query"
                @input="debouncedSearch"
                placeholder="Search by name, description, location..."
                style="width:100%;height:42px;border:1px solid #E2E8F0;border-radius:999px;padding:0 16px 0 38px;font-size:.875rem;color:#0F172A;background:#F8FAFC;transition:all .15s;"
                aria-label="Search missing children cases"
              >
            </div>

            <!-- Gender -->
            <select
              v-model="filter.gender"
              @change="filter_post()"
              style="height:42px;border:1px solid #E2E8F0;border-radius:10px;padding:0 12px;font-size:.875rem;color:#334155;background:#F8FAFC;cursor:pointer;"
              aria-label="Filter by gender"
            >
              <option value="">All Genders</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>

            <!-- Age -->
            <input
              type="number"
              v-model="filter.age"
              @change="filter_post()"
              placeholder="Age"
              min="0" max="18"
              style="height:42px;width:80px;border:1px solid #E2E8F0;border-radius:10px;padding:0 12px;font-size:.875rem;color:#334155;background:#F8FAFC;"
              aria-label="Filter by age"
            >

            <!-- Actions -->
            <div style="display:flex;gap:8px;">
              <button
                type="submit"
                style="height:42px;padding:0 20px;background:#2563EB;color:#fff;border:none;border-radius:10px;font-size:.875rem;font-weight:600;cursor:pointer;transition:background .15s;display:flex;align-items:center;gap:6px;"
                aria-label="Apply search filters"
              >
                <i class="fas fa-filter" aria-hidden="true"></i>
                Search
              </button>
              <button
                type="button"
                @click="reset_filter()"
                style="height:42px;width:42px;background:#F1F5F9;color:#64748B;border:none;border-radius:10px;cursor:pointer;transition:all .15s;font-size:14px;"
                title="Reset filters"
                aria-label="Reset search filters"
              >
                <i class="fas fa-redo" aria-hidden="true"></i>
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- Results summary -->
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;" v-if="!loading_data">
        <p style="font-size:.875rem;font-weight:600;color:#334155;margin:0;">
          <span style="color:#DC2626;font-weight:800;">{{ posts.length }}</span> active missing cases
        </p>
        <p style="font-size:.75rem;color:#94A3B8;margin:0;">Updated in real-time</p>
      </div>

      <!-- Posts list -->
      <ul class="list_ofPosts list-unstyled" aria-label="Missing children reports">
        <li v-for="(post, key) in posts" :key="post.id">
          <article class="post-card" :aria-label="'Missing child report: ' + post.name">

            <!-- Card Header -->
            <div class="post-card-header">
              <div class="post-avatar-wrap">
                <img class="post-avatar" :src="post.user.image" :alt="post.user.name + ' profile picture'">
                <div class="verified-badge" aria-label="Verified member">
                  <i class="fas fa-check" aria-hidden="true"></i>
                </div>
              </div>

              <div class="post-meta">
                <p class="post-author">{{ post.user.name }}</p>
                <p class="post-time">
                  <i class="fas fa-clock" style="font-size:10px;margin-right:3px;" aria-hidden="true"></i>
                  {{ moment(post.created_at).fromNow() }}
                </p>
              </div>

              <div class="post-header-right">
                <span class="post-status-badge status-missing" role="status" aria-label="Status: Missing">
                  Missing
                </span>
                <div v-if="post.user.id == user.id" class="dropdown show">
                  <button class="post-more-btn" data-toggle="dropdown"
                    aria-haspopup="true" aria-expanded="false"
                    :aria-label="'Options for ' + post.name + ' report'">
                    <i class="fas fa-ellipsis-h" aria-hidden="true"></i>
                  </button>
                  <div class="dropdown-menu dropdown-menu-right" style="border-radius:12px;border:1px solid #E2E8F0;box-shadow:0 10px 32px rgba(15,23,42,.12);padding:4px;">
                    <a class="dropdown-item" href="#" style="border-radius:8px;font-size:.875rem;">
                      <i class="fas fa-edit" style="margin-right:8px;color:#2563EB;" aria-hidden="true"></i>Edit
                    </a>
                    <a class="dropdown-item" href="#" @click.prevent="delete_post(post.id, key)"
                       style="border-radius:8px;font-size:.875rem;color:#DC2626;">
                      <i class="fas fa-trash-alt" style="margin-right:8px;" aria-hidden="true"></i>Delete
                    </a>
                  </div>
                </div>
              </div>
            </div>

            <!-- Child Info -->
            <div class="post-card-info">
              <div class="child-info-grid">
                <div class="info-item">
                  <p class="info-label">Name</p>
                  <p class="info-value">{{ post.name }}</p>
                </div>
                <div class="info-item">
                  <p class="info-label">Age</p>
                  <p class="info-value">{{ post.age }} years old</p>
                </div>
                <div class="info-item">
                  <p class="info-label">Gender</p>
                  <p class="info-value">{{ (post.gender == 1 || post.gender === 'male') ? 'Male' : 'Female' }}</p>
                </div>
                <div class="info-item">
                  <p class="info-label">Last Seen</p>
                  <p class="info-value">{{ moment(post.created_at).format('MMM D, YYYY') }}</p>
                </div>
              </div>

              <div class="post-location" v-if="post.description">
                <i class="fas fa-map-marker-alt" aria-hidden="true"></i>
                <span>{{ post.description.substring(0, 100) + (post.description.length > 100 ? '...' : '') }}</span>
              </div>

              <p class="post-description" v-if="post.description">{{ post.description }}</p>

              <div class="ai-badge" v-if="post.ai_match_score">
                <i class="fas fa-brain" aria-hidden="true"></i>
                AI Similarity:
                <span class="ai-badge-pct">{{ post.ai_match_score }}%</span>
                confidence
              </div>
            </div>

            <!-- Photos carousel -->
            <div class="post-card-photo" v-if="post.images && post.images.length">
              <carousel :dots="false" :nav="true" :items="1">
                <vue-load-image v-for="post_image in post.images" :key="post_image.id">
                  <img slot="image" :src="post_image.image" :alt="post.name + ' – missing child photo'" class="post-child-img">
                  <img slot="preloader" :src="base_url + '/front/svg/image-loader.8402b89.gif'" alt="Loading..." class="post-child-img" style="object-fit:contain;">
                  <div slot="error" style="height:180px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:8px;color:#94A3B8;">
                    <i class="fas fa-image" style="font-size:28px;" aria-hidden="true"></i>
                    <span style="font-size:.8125rem;">Photo unavailable</span>
                  </div>
                </vue-load-image>
                <template slot="prev">
                  <div class="photo-arrows swiper-button-prev" role="button" aria-label="Previous photo">
                    <i class="fas fa-chevron-left" aria-hidden="true"></i>
                  </div>
                </template>
                <template slot="next">
                  <div class="photo-arrows swiper-button-next" role="button" aria-label="Next photo">
                    <i class="fas fa-chevron-right" aria-hidden="true"></i>
                  </div>
                </template>
              </carousel>
            </div>

            <!-- Engagement stats -->
            <div class="post-card-stats" aria-label="Post engagement statistics">
              <div class="stats-left">
                <div class="stat-item">
                  <i class="fas fa-heart" aria-hidden="true"></i>
                  <span>{{ post.likes_count || 0 }} Likes</span>
                </div>
                <div class="stat-item">
                  <i class="fas fa-comment" aria-hidden="true"></i>
                  <span>{{ post.count_comment || 0 }} Comments</span>
                </div>
              </div>
              <div class="stats-right">{{ post.shares_count || 0 }} Shares</div>
            </div>

            <!-- Action buttons -->
            <div class="post-card-actions" role="group" :aria-label="'Actions for ' + post.name + ' report'">
              <button class="post-action-btn" aria-label="Like this report">
                <i class="far fa-heart" aria-hidden="true"></i>
                <span>Like</span>
              </button>
              <a class="post-action-btn" :href="base_url + '/get_message/' + post.user.id" aria-label="Send message to reporter">
                <i class="far fa-comment-dots" aria-hidden="true"></i>
                <span>Message</span>
              </a>
              <button class="post-action-btn active" aria-label="Comment on this report">
                <i class="far fa-comment-alt" aria-hidden="true"></i>
                <span>Comment</span>
              </button>
              <button class="post-action-btn" aria-label="Share this report">
                <i class="fas fa-share" aria-hidden="true"></i>
                <span>Share</span>
              </button>
              <button class="post-action-btn action-report" aria-label="Flag this report">
                <i class="fas fa-flag" aria-hidden="true"></i>
                <span>Tip/Info</span>
              </button>
            </div>

            <!-- Comments -->
            <div class="post-card-comments" aria-label="Comments section">
              <button v-if="post.count_comment > 2"
                class="load-comments-btn"
                @click.prevent="load_more_comment(post.id, key)"
                :aria-label="'Load more comments for ' + post.name">
                <i class="fas fa-chevron-down" aria-hidden="true"></i>
                View {{ post.count_comment - post.comments.length }} more comment(s)
              </button>

              <ul class="comment-list" :aria-label="'Comments on ' + post.name">
                <li v-if="show_dot">
                  <div style="display:flex;align-items:center;gap:8px;padding:4px 0;" aria-live="polite">
                    <div style="display:flex;gap:3px;">
                      <span style="width:6px;height:6px;border-radius:50%;background:#94A3B8;animation:wave 1.4s ease infinite;"></span>
                      <span style="width:6px;height:6px;border-radius:50%;background:#94A3B8;animation:wave 1.4s ease .2s infinite;"></span>
                      <span style="width:6px;height:6px;border-radius:50%;background:#94A3B8;animation:wave 1.4s ease .4s infinite;"></span>
                    </div>
                    <span style="font-size:.75rem;color:#94A3B8;">Someone is typing...</span>
                  </div>
                </li>
                <li class="comment-item" v-for="(comment, key_comment) in post.comments" :key="comment.id">
                  <img class="comment-avatar" :src="comment.user.image" :alt="comment.user.name + ' avatar'">
                  <div class="comment-bubble">
                    <p class="comment-author">{{ comment.user.name }}</p>
                    <p class="comment-text">{{ comment.comment }}</p>
                  </div>
                  <div class="comment-actions" v-if="comment.user.id == user.id">
                    <div class="dropdown show">
                      <button class="post-more-btn" style="width:28px;height:28px;" data-toggle="dropdown"
                        aria-haspopup="true" aria-expanded="false" :aria-label="'Options for comment'">
                        <i class="fas fa-ellipsis-h" style="font-size:12px;" aria-hidden="true"></i>
                      </button>
                      <div class="dropdown-menu dropdown-menu-right" style="border-radius:10px;min-width:120px;border:1px solid #E2E8F0;box-shadow:0 8px 24px rgba(15,23,42,.1);padding:4px;">
                        <a class="dropdown-item" href="#"
                          :id="'update_com' + comment.id"
                          @click.prevent="update_comment(comment.id, comment.comment, key_comment)"
                          style="border-radius:6px;font-size:.8125rem;">
                          <i class="fas fa-edit" style="margin-right:6px;color:#2563EB;" aria-hidden="true"></i>Edit
                        </a>
                        <a class="dropdown-item" href="#"
                          @click.prevent="delete_comment(comment.id, key_comment, key)"
                          style="border-radius:6px;font-size:.8125rem;color:#DC2626;">
                          <i class="fas fa-trash-alt" style="margin-right:6px;" aria-hidden="true"></i>Delete
                        </a>
                      </div>
                    </div>
                  </div>
                </li>
              </ul>

              <form @submit.prevent="add_comment(key, post.id)" class="write-comment-form" :aria-label="'Comment on ' + post.name">
                <img :src="user.image" :alt="user.name" class="write-comment-avatar">
                <input
                  @keydown="showtyping()"
                  v-model="comment"
                  class="write-comment-input"
                  type="text"
                  placeholder="Share a tip or comment..."
                  :aria-label="'Write comment for ' + post.name"
                >
                <button class="submit-comment-btn" type="submit" aria-label="Post comment">
                  <i class="fas fa-paper-plane" aria-hidden="true"></i>
                </button>
              </form>
            </div>

          </article>
        </li>
      </ul>

      <!-- Loading -->
      <transition name="fade">
        <div class="feed-loading" v-if="loading_data" role="status" aria-live="polite">
          <i class="fas fa-spinner fa-spin" aria-hidden="true"></i>
          Loading missing children reports...
        </div>
      </transition>

      <!-- Empty state -->
      <div v-if="!loading_data && posts.length === 0"
        style="text-align:center;padding:3rem;background:#fff;border:1px solid #E2E8F0;border-radius:16px;box-shadow:0 1px 3px rgba(15,23,42,.06);">
        <div style="width:64px;height:64px;background:#FEF2F2;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">
          <i class="fas fa-search" style="font-size:24px;color:#DC2626;" aria-hidden="true"></i>
        </div>
        <h3 style="font-size:1.125rem;font-weight:700;color:#0F172A;margin:0 0 8px;">No cases found</h3>
        <p style="font-size:.875rem;color:#64748B;margin:0 0 16px;">Try adjusting your search filters or browse all cases.</p>
        <button @click="reset_filter()" style="background:#2563EB;color:#fff;border:none;border-radius:10px;padding:10px 20px;font-size:.875rem;font-weight:600;cursor:pointer;">
          Clear Filters
        </button>
      </div>

      <div class="feed-end-msg" v-if="show_end_message && posts.length > 0" role="status">
        You've seen all {{ posts.length }} active missing cases. Please help by sharing.
      </div>

    </div>
  </div>
</template>

<script>
import carousel from 'vue-owl-carousel'
import VueLoadImage from 'vue-load-image'

export default {
  components: { carousel, 'vue-load-image': VueLoadImage },
  props: ['user'],

  data() {
    return {
      posts: [],
      next_url: '',
      filter: { gender: '', from: '', to: '', city: '', query: '', age: '' },
      comment: '',
      comment_id: '',
      uri: base_url + '/api/posts',
      validationErrors: [],
      base_url: base_url,
      next_comment_url: '',
      page_num: 1,
      remove_comment_key: '',
      loading: false,
      show_dot: false,
      loading_data: false,
      show_end_message: false,
      searchTimer: null
    }
  },

  methods: {
    add_comment(key, id) {
      var _this = this;
      var formData = new FormData();
      formData.append('comment', this.comment);
      formData.append('post_id', id);
      formData.append('key', key);
      if (this.comment_id !== '') {
        formData.append('_method', 'patch');
        axios.post(base_url + '/comments/' + this.comment_id, formData)
          .then(function(response) {
            _this.posts[key].comments.splice(_this.remove_comment_key, 1);
            _this.posts[key].comments.push(response.data.comment);
            _this.comment = '';
            _this.comment_id = '';
          }).catch(error => {
            if (error.response && error.response.status === 422) {
              _this.validationErrors = error.response.data.errors;
            }
          });
      } else {
        axios.post(base_url + '/comments', formData)
          .then(function(response) {
            _this.posts[key].comments.push(response.data.comment);
            _this.comment = '';
          }).catch(error => {
            if (error.response && error.response.status === 422) {
              _this.validationErrors = error.response.data.errors;
            }
          });
      }
    },

    delete_comment(comment_id, comment_key, post_key) {
      if (!confirm('Are you sure?')) return;
      var _this = this;
      axios.delete(base_url + '/comments/' + comment_id)
        .then(function() {
          _this.posts[post_key].comments.splice(comment_key, 1);
        }).catch(error => console.log(error));
    },

    update_comment(comment_id, comment, comment_key) {
      this.comment = comment;
      this.comment_id = comment_id;
      this.remove_comment_key = comment_key;
    },

    load_more_comment(post_id, key) {
      var _this = this;
      if (_this.posts[key].comments.length < _this.posts[key].count_comment) {
        axios.get(this.base_url + '/comments?post_id=' + post_id + '&page=' + this.page_num)
          .then(function(response) {
            for (var i = 0; i < response.data.comments.data.length; i++) {
              _this.posts[key].comments.push(response.data.comments.data[i]);
            }
            _this.next_comment_url = response.data.comments.next_page_url;
            if (_this.next_comment_url) _this.page_num++;
          }).catch(error => console.log(error));
      }
    },

    showtyping() {
      Echo.private('comment-post').whisper('typing', { message: 'typing', typing: true });
    },

    debouncedSearch() {
      clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => this.filter_post(), 400);
    },

    reset_filter() {
      this.filter = { gender: '', from: '', to: '', city: '', query: '', age: '' };
      this.get_posts();
    },

    get_posts() {
      var _this = this;
      this.loading_data = true;
      axios.get(this.uri, { params: { type: 'missed' } })
        .then(function(response) {
          var postsData = response.data.data || (response.data.posts ? response.data.posts.data : []);
          var nextUrl = response.data.next_page_url || (response.data.posts ? response.data.posts.next_page_url : null);
          _this.posts = postsData;
          _this.next_url = nextUrl;
          _this.loading_data = false;
          _this.show_end_message = !nextUrl;
        }).catch(function(error) {
          console.log(error);
          _this.loading_data = false;
        });
    },

    filter_post() {
      var _this = this;
      this.loading_data = true;
      this.posts = [];
      var params = Object.assign({ type: 'missed' }, this.filter);
      axios.get(base_url + '/api/search', { params })
        .then(function(response) {
          var postsData = response.data.data || (response.data.posts ? response.data.posts.data : []);
          var nextUrl = response.data.next_page_url || (response.data.posts ? response.data.posts.next_page_url : null);
          _this.posts = postsData;
          _this.next_url = nextUrl;
          _this.data = new FormData();
          _this.loading = false;
          _this.loading_data = false;
          _this.show_end_message = !nextUrl;
        }).catch(function(error) {
          console.log(error);
          _this.loading_data = false;
        });
    },

    load_posts() {
      var _this = this;
      if (this.next_url && !this.loading_data) {
        this.loading_data = true;
        axios.get(_this.next_url)
          .then(function(response) {
            var postsData = response.data.data || (response.data.posts ? response.data.posts.data : []);
            var nextUrl = response.data.next_page_url || (response.data.posts ? response.data.posts.next_page_url : null);
            if (postsData.length > 0) {
              _this.posts = _this.posts.concat(postsData);
              _this.next_url = nextUrl;
              _this.loading_data = false;
            } else {
              _this.loading_data = false;
              _this.show_end_message = true;
            }
          }).catch(function(error) {
            console.log(error);
            _this.loading_data = false;
          });
      }
    },

    delete_post(post_id, post_key) {
      if (!confirm('Are you sure you want to delete this report?')) return;
      var _this = this;
      axios.delete(base_url + '/posts/' + post_id)
        .then(function() {
          _this.posts.splice(post_key, 1);
        }).catch(error => console.log(error));
    }
  },

  created() {
    var _this = this;
    Echo.private('comment-post')
      .listen('.comment.created', (e) => {
        if (_this.posts[e.key]) _this.posts[e.key].comments.push(e.comment);
      })
      .listenForWhisper('typing', (e) => {
        if (e.typing) _this.show_dot = true;
        setTimeout(() => { _this.show_dot = false; }, 4000);
      });
    Echo.private('post-event')
      .listen('.post.created', () => { _this.get_posts(); });
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      const visible = document.documentElement.clientHeight;
      const pageHeight = document.documentElement.scrollHeight;
      if (visible + scrollY >= pageHeight - 200 && this.next_url) {
        this.load_posts();
      }
    });
  },

  mounted() {
    this.get_posts();
  }
}
</script>
