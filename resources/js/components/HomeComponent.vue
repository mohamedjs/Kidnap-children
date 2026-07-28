<template>
  <div class="dashboard-profile" v-cloak>

    <!-- Feed area wrapper -->
    <div class="feed-area">

      <!-- Feed filter tabs -->
      <div class="feed-filters" role="tablist" aria-label="Filter posts by type">
        <button class="feed-filter-btn active" data-type="" @click="setFilter('')" role="tab" :aria-selected="filter.type === ''">
          <i class="fas fa-layer-group" aria-hidden="true"></i> All Posts
        </button>
        <button class="feed-filter-btn" data-type="missed" @click="setFilter('missed')" role="tab" :aria-selected="filter.type === 'missed'">
          <i class="fas fa-search" aria-hidden="true"></i> Missing
        </button>
        <button class="feed-filter-btn" data-type="founded" @click="setFilter('founded')" role="tab" :aria-selected="filter.type === 'founded'">
          <i class="fas fa-check-circle" aria-hidden="true"></i> Found
        </button>
      </div>

      <!-- Create Report Card -->
      <div class="create-post-card" role="region" aria-label="Create a new report">
        <div class="create-post-trigger">
          <img :src="user.image" :alt="user.name + ' avatar'" class="create-post-avatar">
          <button class="create-post-placeholder"
            data-toggle="collapse" data-target="#create-post-body"
            aria-expanded="false" aria-controls="create-post-body"
            @click="toggleForm">
            What happened? Report a missing or found child...
          </button>
        </div>

        <div class="create-post-actions">
          <button class="create-action-btn" data-toggle="collapse" data-target="#create-post-body"
            @click="toggleForm" aria-label="Upload photo for report">
            <i class="fas fa-camera" aria-hidden="true"></i> Photo
          </button>
          <button class="create-action-btn" data-toggle="collapse" data-target="#create-post-body"
            @click="toggleForm" aria-label="Report missing child">
            <i class="fas fa-search" aria-hidden="true"></i> Missing Report
          </button>
          <button class="create-action-btn" data-toggle="collapse" data-target="#create-post-body"
            @click="toggleForm" aria-label="Report found child">
            <i class="fas fa-check-circle" aria-hidden="true"></i> Found Report
          </button>
        </div>

        <!-- Collapsible form -->
        <div class="create-post-form collapse" id="create-post-body" :class="{ 'is-open': form_open }">
          <form @submit.prevent="create_post()" novalidate>

            <div class="form-row">
              <div class="form-group">
                <label for="person_name">Child's Name *</label>
                <input
                  id="person_name"
                  :class="'form-control' + (errors.has('person_name') ? ' is-invalid' : '')"
                  v-validate="{ required: true, alpha_spaces: true }"
                  name="person_name"
                  v-model="post.name"
                  type="text"
                  placeholder="Full name"
                  autocomplete="off"
                >
                <span v-if="errors.has('person_name')" class="invalid-feedback" role="alert">
                  {{ errors.first('person_name') }}
                </span>
              </div>

              <div class="form-group">
                <label for="gender_select">Gender</label>
                <select id="gender_select" class="form-control" v-model="post.gender" aria-label="Select gender">
                  <option value="">Select gender</option>
                  <option value="1">Male</option>
                  <option value="2">Female</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="birth_date">Date of Birth</label>
                <input
                  id="birth_date"
                  class="form-control date"
                  v-model="post.birth_date"
                  name="birth_date"
                  placeholder="YYYY-MM-DD"
                  type="text"
                >
              </div>

              <div class="form-group">
                <label for="age_input">Age *</label>
                <input
                  id="age_input"
                  :class="'form-control' + (errors.has('age') ? ' is-invalid' : '')"
                  v-model="post.age"
                  v-validate="{ required: true, numeric: true, min_value: 0, max_value: 18 }"
                  name="age"
                  placeholder="Age in years"
                  type="number"
                  min="0" max="18"
                >
                <span v-if="errors.has('age')" class="invalid-feedback" role="alert">
                  {{ errors.first('age') }}
                </span>
              </div>
            </div>

            <div class="form-group">
              <label for="post_type">Report Type *</label>
              <select id="post_type" class="form-control" v-model="post.type" aria-label="Select report type">
                <option value="">Select type</option>
                <option value="missed">Missing Child</option>
                <option value="founded">Found Child</option>
              </select>
            </div>

            <div class="form-group">
              <label for="description">Description & Last Known Location *</label>
              <textarea
                id="description"
                :class="'form-control' + (errors.has('description') ? ' is-invalid' : '')"
                v-validate="{ required: true }"
                v-model="post.description"
                name="description"
                placeholder="Describe the child, clothing, last known location, any identifying features..."
                rows="4"
              ></textarea>
              <span v-if="errors.has('description')" class="invalid-feedback" role="alert">
                {{ errors.first('description') }}
              </span>
            </div>

            <!-- Photo upload -->
            <div class="form-group">
              <label>Child's Photo(s)</label>
              <label class="upload-area" for="photo-upload-input" tabindex="0"
                @keydown.enter="$refs.file.click()" aria-label="Click or press Enter to upload photos">
                <i class="fas fa-cloud-upload-alt" aria-hidden="true"></i>
                <p>Click to upload photos of the child</p>
                <p style="font-size:.75rem;color:#94A3B8;margin-top:4px;">PNG, JPG up to 2MB each</p>
              </label>
              <input
                id="photo-upload-input"
                class="sr-only"
                ref="file"
                type="file"
                v-validate
                data-vv-rules="image|size:2000|ext:jpeg,jpg,png"
                accept="image/*"
                name="post_image"
                @change="loadFile($event)"
                multiple
                aria-hidden="true"
                tabindex="-1"
              >
              <span v-if="errors.has('post_image')" class="invalid-feedback" role="alert">
                {{ errors.first('post_image') }}
              </span>
            </div>

            <!-- Preview uploaded photos -->
            <ul class="uploaded-photos" aria-label="Uploaded photos preview"></ul>

            <button class="submit-post-btn" type="submit" :disabled="loading_posts_result">
              <span v-if="!loading_posts_result">
                <i class="fas fa-paper-plane" aria-hidden="true"></i>
                Submit Report & Search AI Matches
              </span>
              <span v-else>
                <i class="fas fa-spinner fa-spin" aria-hidden="true"></i>
                Searching AI Matches...
              </span>
            </button>
          </form>
        </div>
      </div>
      <!-- /create-post-card -->

      <!-- AI search results notice -->
      <transition name="fade">
        <div v-if="loading_posts_result" class="feed-loading" role="status" aria-live="polite">
          <i class="fas fa-spinner fa-spin" aria-hidden="true"></i>
          AI is searching for matching cases across the database...
        </div>
      </transition>

      <!-- Posts feed -->
      <ul class="list_ofPosts list-unstyled" aria-label="Posts feed">
        <li v-for="(post, key) in posts" :key="post.id">
          <article class="post-card" :aria-label="'Report for ' + post.name">

            <!-- Card Header -->
            <div class="post-card-header">
              <div class="post-avatar-wrap">
                <img class="post-avatar" :src="post.user.image" :alt="post.user.name + ' avatar'">
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
                <!-- Status badge -->
                <span :class="'post-status-badge ' + (post.type === 'missed' ? 'status-missing' : 'status-found')"
                  role="status"
                  :aria-label="'Status: ' + (post.type === 'missed' ? 'Missing' : 'Found Safe')">
                  {{ post.type === 'missed' ? 'Missing' : 'Found Safe' }}
                </span>

                <!-- Post owner options -->
                <div v-if="post.user.id == user.id" class="dropdown show">
                  <button class="post-more-btn" data-toggle="dropdown"
                    aria-haspopup="true" aria-expanded="false"
                    :aria-label="'Options for ' + post.name + ' post'">
                    <i class="fas fa-ellipsis-h" aria-hidden="true"></i>
                  </button>
                  <div class="dropdown-menu dropdown-menu-right" style="border-radius:12px;border:1px solid #E2E8F0;box-shadow:0 10px 32px rgba(15,23,42,.12);padding:4px;">
                    <a class="dropdown-item" href="#" style="border-radius:8px;font-size:.875rem;" >
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
            <!-- /card-header -->

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
                  <p class="info-value">{{ post.gender == 1 ? 'Male' : 'Female' }}</p>
                </div>
                <div class="info-item">
                  <p class="info-label">Reported</p>
                  <p class="info-value">{{ moment(post.created_at).format('MMM D, YYYY') }}</p>
                </div>
              </div>

              <!-- Last known location -->
              <div class="post-location">
                <i class="fas fa-map-marker-alt" aria-hidden="true"></i>
                <span>{{ post.description ? post.description.substring(0, 80) + '...' : 'Location not specified' }}</span>
              </div>

              <!-- Description -->
              <p class="post-description" v-if="post.description">
                {{ post.description }}
              </p>

              <!-- AI similarity badge (shown when applicable) -->
              <div class="ai-badge" v-if="post.ai_match_score">
                <i class="fas fa-brain" aria-hidden="true"></i>
                AI Similarity Match:
                <span class="ai-badge-pct">{{ post.ai_match_score }}%</span>
                confidence
              </div>
            </div>

            <!-- Child photos carousel -->
            <div class="post-card-photo" v-if="post.images && post.images.length">
              <carousel :dots="false" :nav="true" :items="1" class="swiper-wrapper">
                <vue-load-image v-for="post_image in post.images" :key="post_image.id">
                  <img slot="image" :src="post_image.image" :alt="post.name + ' – child photo'" class="post-child-img">
                  <img slot="preloader" :src="base_url + '/front/svg/image-loader.8402b89.gif'" alt="Loading photo..." class="post-child-img" style="object-fit:contain;">
                  <div slot="error" style="height:200px;display:flex;align-items:center;justify-content:center;color:#94A3B8;flex-direction:column;gap:8px;">
                    <i class="fas fa-image" style="font-size:32px;" aria-hidden="true"></i>
                    <span style="font-size:.875rem;">Photo unavailable</span>
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
              <div class="stats-right">
                {{ post.shares_count || 0 }} Shares
              </div>
            </div>

            <!-- Action buttons -->
            <div class="post-card-actions" role="group" :aria-label="'Actions for ' + post.name + ' report'">
              <button class="post-action-btn" aria-label="Like this report" @click.prevent>
                <i class="far fa-heart" aria-hidden="true"></i>
                <span>Like</span>
              </button>
              <button class="post-action-btn active" aria-label="Comment on this report">
                <i class="far fa-comment-alt" aria-hidden="true"></i>
                <span>Comment</span>
              </button>
              <button class="post-action-btn" aria-label="Share this report">
                <i class="fas fa-share" aria-hidden="true"></i>
                <span>Share</span>
              </button>
              <button class="post-action-btn" aria-label="Save this report">
                <i class="far fa-bookmark" aria-hidden="true"></i>
                <span>Save</span>
              </button>
              <button class="post-action-btn action-report" aria-label="Report this post as inappropriate">
                <i class="fas fa-flag" aria-hidden="true"></i>
                <span>Report</span>
              </button>
            </div>
            <!-- /actions -->

            <!-- Comments section -->
            <div class="post-card-comments" aria-label="Comments section">

              <!-- Load more comments -->
              <button v-if="post.count_comment > 2"
                class="load-comments-btn"
                @click.prevent="load_more_comment(post.id, key)"
                :aria-label="'Load more comments for ' + post.name">
                <i class="fas fa-chevron-down" aria-hidden="true"></i>
                View {{ post.count_comment - post.comments.length }} more comment(s)
              </button>

              <ul class="comment-list" :aria-label="'Comments on ' + post.name + ' report'">
                <!-- Typing indicator -->
                <li v-if="show_dot">
                  <div style="display:flex;align-items:center;gap:8px;padding:4px 0;" aria-live="polite" aria-label="Someone is typing">
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
                        aria-haspopup="true" aria-expanded="false"
                        :aria-label="'Options for comment by ' + comment.user.name">
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

              <!-- Write comment form -->
              <form @submit.prevent="add_comment(key, post.id)" class="write-comment-form" :aria-label="'Write a comment on ' + post.name + ' report'">
                <img :src="user.image" :alt="user.name + ' avatar'" class="write-comment-avatar">
                <input
                  @keydown="showtyping()"
                  v-model="comment"
                  class="write-comment-input"
                  type="text"
                  placeholder="Write a comment..."
                  :aria-label="'Comment on ' + post.name + ' report'"
                >
                <button class="submit-comment-btn" type="submit" aria-label="Submit comment">
                  <i class="fas fa-paper-plane" aria-hidden="true"></i>
                </button>
              </form>
            </div>
            <!-- /comments -->

          </article>
        </li>
      </ul>
      <!-- /posts feed -->

      <!-- Infinite scroll loader -->
      <transition name="fade">
        <div class="feed-loading" v-if="loading_data" role="status" aria-live="polite">
          <i class="fas fa-spinner fa-spin" aria-hidden="true"></i>
          Loading more reports...
        </div>
      </transition>

      <!-- End of feed -->
      <div class="feed-end-msg" v-if="show_end_message" role="status">
        🎉 You've seen all the reports. Help share to reach more people.
      </div>

    </div>
    <!-- /feed-area -->

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
      data: new FormData(),
      posts: [],
      post: {
        name: '',
        gender: '',
        birth_date: moment(new Date()).format('YYYY-MM-DD'),
        description: '',
        age: '',
        type: ''
      },
      filter: { gender: '', from: '', to: '', city: '', type: '' },
      comment: '',
      comment_id: '',
      uri: base_url + '/posts',
      validationErrors: [],
      base_url: base_url,
      next_url: '',
      next_comment_url: '',
      page_num: 1,
      remove_comment_key: '',
      loading: false,
      show_dot: false,
      loading_data: false,
      show_end_message: false,
      loading_posts_result: false,
      form_open: false
    }
  },

  methods: {
    toggleForm() {
      this.form_open = !this.form_open;
    },

    setFilter(type) {
      this.filter.type = type;
      // Update UI button states
      document.querySelectorAll('.feed-filter-btn').forEach(btn => btn.classList.remove('active'));
      event.currentTarget.classList.add('active');
      this.posts = [];
      this.next_url = this.uri;
      this.get_posts();
    },

    get_posts() {
      var _this = this;
      var params = {};
      if (this.filter.type) params.type = this.filter.type;
      axios.get(this.uri, { params }).then(function(response) {
        _this.posts = response.data.posts.data;
        _this.next_url = response.data.posts.next_page_url;
      }).catch(error => console.log(error));
    },

    load_posts() {
      var _this = this;
      if (this.next_url) {
        this.loading_data = true;
        axios.get(_this.next_url).then(function(response) {
          if (response.data.posts.data.length > 0) {
            _this.posts = _this.posts.concat(response.data.posts.data);
            _this.next_url = response.data.posts.next_page_url;
            _this.loading_data = false;
          } else {
            _this.show_end_message = true;
            _this.loading_data = false;
          }
        }).catch(error => console.log(error));
      }
    },

    add_comment(key, id) {
      var _this = this;
      this.data.append('comment', this.comment);
      this.data.append('post_id', id);
      this.data.append('key', key);

      if (this.comment_id !== '') {
        this.data.append('_method', 'patch');
        axios.post(base_url + '/comments/' + this.comment_id, this.data)
          .then(function(response) {
            _this.posts[key].comments.splice(_this.remove_comment_key, 1);
            _this.posts[key].comments.push(response.data.comment);
            _this.data = new FormData();
            _this.comment = '';
            _this.comment_id = '';
          }).catch(error => {
            if (error.response && error.response.status === 422) {
              _this.validationErrors = error.response.data.errors;
            }
          });
      } else {
        axios.post(base_url + '/comments', this.data)
          .then(function(response) {
            _this.posts[key].comments.push(response.data.comment);
            _this.data = new FormData();
            _this.comment = '';
          }).catch(error => {
            if (error.response && error.response.status === 422) {
              _this.validationErrors = error.response.data.errors;
            }
          });
      }
    },

    delete_comment(comment_id, comment_key, post_key) {
      if (!confirm('Are you sure you want to delete this comment?')) return;
      var _this = this;
      axios.delete(base_url + '/comments/' + comment_id)
        .then(function(response) {
          _this.posts[post_key].comments.splice(comment_key, 1);
          _this.data = new FormData();
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
            if (_this.next_comment_url) {
              _this.page_num = _this.page_num + 1;
            }
          }).catch(error => console.log(error));
      }
    },

    showtyping() {
      Echo.private('comment-post').whisper('typing', {
        message: 'someone is writing a comment',
        typing: true
      });
    },

    loadFile(event) {
      for (var i = 0; i < event.target.files.length; i++) {
        var img = '<li><div class="img-box"><img class="img-fluid" src="' +
          URL.createObjectURL(event.target.files[i]) + '" alt="Uploaded photo preview"></div></li>';
        $('.uploaded-photos').append(img);
        this.data.append('images[]', event.target.files[i]);
      }
    },

    create_post() {
      this.posts = [];
      this.loading_posts_result = true;
      var _this = this;
      this.data.append('name', this.post.name);
      this.data.append('gender', this.post.gender);
      this.data.append('description', this.post.description);
      this.data.append('birth_date', this.post.birth_date);
      this.data.append('age', this.post.age);
      this.data.append('lat', 31.022323);
      this.data.append('lng', 31.12120);
      this.data.append('type', this.post.type);
      const config = { headers: { 'content-type': 'multipart/form-data' } };
      axios.post(base_url + '/posts', this.data, config)
        .then(function(response) {
          if (response.data.results && response.data.results.length > 0) {
            _this.posts = response.data.results;
            _this.loading_posts_result = false;
            _this.next_url = null;
            alert('✅ AI found ' + response.data.results.length + ' matching case(s) for your report!');
          } else {
            _this.loading_posts_result = false;
            _this.get_posts();
            _this.data = new FormData();
            alert('Report submitted. No immediate AI matches found — your report is now live in the community feed.');
          }
          _this.form_open = false;
        }).catch(error => {
          _this.loading_posts_result = false;
          console.log(error);
        });
    },

    delete_post(post_id, post_key) {
      if (!confirm('Are you sure you want to delete this report?')) return;
      var _this = this;
      axios.delete(base_url + '/posts/' + post_id)
        .then(function(response) {
          _this.posts.splice(post_key, 1);
          _this.data = new FormData();
        }).catch(error => console.log(error));
    }
  },

  created() {
    var _this = this;

    // Real-time comment listener
    Echo.private('comment-post')
      .listen('.comment.created', (e) => {
        _this.posts[e.key].comments.push(e.comment);
      })
      .listenForWhisper('typing', (e) => {
        if (e.typing) {
          _this.show_dot = true;
        }
        setTimeout(() => { _this.show_dot = false; }, 4000);
      });

    // Real-time post listener
    Echo.private('post-event')
      .listen('.post.created', (e) => {
        _this.get_posts();
      });

    // Infinite scroll
    window.addEventListener('scroll', (e) => {
      const scrollY = window.scrollY;
      const visible = document.documentElement.clientHeight;
      const pageHeight = document.documentElement.scrollHeight;
      const nearBottom = visible + scrollY >= pageHeight - 200;
      if (nearBottom && this.next_url && !this.loading_data && !this.loading_posts_result) {
        this.load_posts();
      }
    });
  },

  mounted() {
    this.get_posts();
  }
}
</script>
