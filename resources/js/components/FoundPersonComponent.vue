<template>
    <div class="dashboard-profile">
      <div class="dashboard-profile-content">
        <div class="row">
          <div class="col-lg-12">
            <ul class="list_ofPosts list-unstyled">
              <li v-for="(post,key) in posts" :key="key">
                  <div class="post">
                    <div class="photo-box-slider swiper-container">
                      <carousel :dots="false"  :nav="false" :items="1" class="swiper-wrapper">
                        <vue-load-image v-for="post_image in post.images" :key="post_image.key">
                           <img slot="image" :src="post_image.image" class="img-responsive"/>
                           <img slot="preloader" :src="base_url+'/front/svg/image-loader.8402b89.gif'" class="img-responsive"/>
                           <div slot="error">about</div>
                         </vue-load-image>
                        <template  slot="prev">
                          <div class="swiper-button-prev lost-people-btn-prev photo-arrows"><i class="fas fa-chevron-left"></i></div>
                        </template>
                        <template  slot="next">
                          <div class="swiper-button-next lost-people-btn-next photo-arrows"><i class="fas fa-chevron-right"></i></div>
                        </template>
                      </carousel>
                    </div>
                    <div class="post-data">
                      <div class="post-owner">
                        <div class="img-box"><img class="img-fluid" :src="post.user.image"></div>
                        <div class="owner_date">
                          <h4 class="owner-name">{{post.user.name}}</h4>
                          <p class="post-time">{{moment(post.created_at).format('LL')}}</p>
                        </div>
                        <div v-if="post.user.id == user.id" class="dropdown show setting-dropdown icon-box"><a class="chat-menu" href="#" role="button" id="profile-setting-dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-h"></i></a>
                          <div class="dropdown-menu" aria-labelledby="profile-setting-dropdown" style="top: 25px !important"><a class="dropdown-item" href="#">Edit</a><a class="dropdown-item" @click.prevent = "delete_post(post.id,key)" href="#">Delete</a></div>
                        </div>
                        <div class="clearfix"></div>
                      </div>
                      <div class="post-data-content">
                        <ul class="lostPerson_data list-unstyled">
                          <li>
                            <p class="label">Person Name:</p><span class="value">{{post.name}}</span>
                          </li>
                          <li>
                            <p class="label">gender:</p><span class="value">{{post.gender == 1 ? 'male':'female'}}</span>
                          </li>
                          <li>
                            <p class="label">Lost Date:</p><span class="value">{{moment(post.created_at).format('LL')}}</span>
                          </li>
                          <li>
                            <p class="label">Age:</p><span class="value">{{post.age}}</span>
                          </li>
                          <li>
                            <p class="loatDetails">{{post.description}}</p>
                          </li>
                        </ul>
                      </div>
                      <ul class="post-btn-list list-unstyled d-flex justify-content-between">
                        <li><a class="post-btn" :href="base_url+'/get_message/'+post.user.id"><i class="far fa-comment-dots"></i><span>Send Message</span></a></li>
                        <li><a class="post-btn active-btn" href="#"><i class="far fa-comment-alt"></i><span>Comment</span></a></li>
                        <li><a class="post-btn" href="#"><i class="fas fa-share"></i><span>Share</span></a></li>
                      </ul>
                      <div class="comments">
                        <ul class="user-comments-list list-unstyled">
                          <li v-if="post.count_comment > 2"><a @click.prevent= "load_more_comment(post.id,key)" href="#" style="cursor:pointer;color:#9E2FB2" class="comment-box">load comments</a></li>
                          <li v-for="(comment,key_comment) in post.comments" :key="key_comment">
                            <div class="user-photo"><img class="img-fluid" :src="comment.user.image"></div>
                            <div class="comment-box">
                              <p class="usern-name">{{comment.user.name}}</p>
                              <p class="user-comment">{{comment.comment}}</p>
                            </div>
                            <div v-if="comment.user.id == user.id" class="dropdown show setting-dropdown icon-box"><a class="chat-menu" href="#" role="button" id="profile-setting-dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-h"></i></a>
                              <div class="dropdown-menu" aria-labelledby="profile-setting-dropdown" style="top: 25px !important"><a class="dropdown-item" :id="'update_com'+comment.id" @click.prevent = "update_comment(comment.id,comment.comment,key_comment)" href="#">Edit</a><a class="dropdown-item" @click.prevent = "delete_comment(comment.id,key_comment,key)" href="#">Delete</a></div>
                            </div>
                          </li>
                          <li>
                            <div class="typing" v-if="show_dot" id="loading">
                              <span></span>
                              <span></span>
                              <span></span>
                            </div>
                          </li>
                        </ul>
                        <form @submit.prevent="add_comment(key,post.id)" class="write-comment">
                          <input @keydown="showtyping()" v-model="comment" class="input-write" type="text" placeholder="Write Comment....">
                          <button class="submit-comment" type="submit"><i class="fas fa-paper-plane"></i></button>
                        </form>
                      </div>
                      <div :class="'post_label '+[ post.type==='missed' ? 'label-missed' : 'label-found']"><span>{{post.type}}</span></div>
                    </div>
                  </div>
              </li>
            </ul>
            <transition name="fade">
              <div class="loading_data" v-if="loading_data">
                <span class="fa fa-spinner fa-spin"></span> Loading
              </div>
            </transition>
              <div class="loading_data" v-if="show_end_message">
                 No More Posts :)
              </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import carousel from 'vue-owl-carousel'
import VueLoadImage from 'vue-load-image'
    export default {
      components: { carousel , 'vue-load-image': VueLoadImage },
       data(){
        return{
          data : new FormData(),
          posts:[],
          post:{'name':'' , 'gender':'' , 'birth_date' : moment(new Date()).format('YYYY-MM-DD') , 'description' : '' , 'age' : ''},
          next_url:'',
          filter:{'gender':'' , 'from' : '' , 'to' : '' , 'city' : '' },
          comment:'',
          comment_id : '',
          uri:base_url+'/posts',
          validationErrors:[],
          base_url:base_url,
          next_comment_url:'',
          page_num:1,
          remove_comment_key : '',
          loading:false,
          show_dot:false,
          loading_data:false,
          show_end_message:false
        }
      },
       props:['user'],
       methods: {
         add_comment(key,id){
           var _this = this
           this.data.append('comment' , this.comment)
           this.data.append('post_id' , id)
           this.data.append('key',key)
           if(this.comment_id!='')
           {
             this.data.append('comment' , this.comment)
             this.data.append('_method' , 'patch')
               axios.post(base_url+'/comments/'+this.comment_id , this.data)
                 .then(function (response){
                     // let obj = _this.posts[key].comments.find(x => x.id === _this.comment_id);
                     // let index = array.indexOf(obj)
                     // _this.posts[key].comments.splice(index,1)
                     console.log(response.data.comment.data);
                    _this.posts[key].comments.splice(_this.remove_comment_key,1)
                    _this.posts[key].comments.push(response.data.comment)
                    _this.data = new FormData()
                    _this.comment = ''
                   }).catch(
                     error =>{
                       if (error.response.status == 422){
                         _this.validationErrors = error.response.data.errors;
                        }
                      }
                   )
           }
           else
           {
             axios.post(base_url+'/comments', this.data )
               .then(function (response){
                    _this.posts[key].comments.push(response.data.comment)
                     _this.data = new FormData()
                     _this.comment = ''
                 }).catch( error =>{
                   if (error.response.status == 422){
                     _this.validationErrors = error.response.data.errors
                    }
                  }
                 )
            }
         },
         delete_comment(comment_id,comment_key,post_key){
           var _this = this
           var result = confirm("Are You Sure?");
           if(result){
             axios.delete(base_url+'/comments/'+comment_id)
               .then(function (response){
                    _this.posts[post_key].comments.splice(comment_key , 1)
                     _this.data = new FormData()
                 }).catch(
                     error => console.log(error)
                 )
               }
          },
         update_comment(comment_id,comment,comment_key){
            var _this = this
            this.comment = comment
            this.comment_id = comment_id
            this.remove_comment_key = comment_key
         },
         load_more_comment(post_id,key){
           var _this = this;
           if(_this.posts[key].comments.length < _this.posts[key].count_comment){
             axios.get(this.base_url+'/comments?post_id='+post_id+'&page='+this.page_num).then(function (response) {
               for (var i = 0; i < response.data.comments.data.length; i++) {
                _this.posts[key].comments.push(response.data.comments.data[i]);
               }
               _this.next_comment_url = response.data.comments.next_page_url;
               if(_this.next_comment_url){
                 _this.page_num = _this.page_num+1
               }
             }).catch(
               error => console.log(error)
             );
           }
         },
         showtyping(){
            Echo.private('comment-post')
                .whisper('typing', {
                message: 'some one write comment',
                typing: true
              })
         },
         get_posts(){
           var _this = this;
           axios.get(this.uri+'?type='+"founded").then(function (response) {
             _this.posts = response.data.posts.data;
             _this.next_url = response.data.posts.next_page_url;
           }).catch(
             error => console.log(error)
           );
         },
         filter_post(){
           var _this=this;
           this.loading = true
           this.posts = []
           axios.get(base_url+'/posts?type='+"founded", {params:_this.filter} )
             .then(function (response){
                    _this.posts = response.data.posts.data
                   _this.next_url = response.data.posts.next_page_url
                   _this.data = new FormData()
                   _this.loading=false
               }).catch(
                   error => console.log(error)
               )
         },
         load_posts(){
           var _this = this;
           if(this.next_url){
             this.loading_data = true
             axios.get(_this.next_url).then(function (response) {
               if(response.data.posts.data.length > 0){
                 _this.posts = _this.posts.concat(response.data.posts.data);
                 _this.next_url = response.data.posts.next_page_url;
                  _this.loading_data = false
                 }
                 else{
                   _this.show_end_message = true
                 }
             }).catch(
               error => console.log(error)
             );
          }
         },
         delete_post(post_id,post_key){
           var _this = this
           var result = confirm("Are You Sure?");
           if(result){
             axios.delete(base_url+'/posts/'+post_id)
               .then(function (response){
                    _this.posts.splice(post_key,1)
                     _this.data = new FormData()
                     //_this.post = ''
                 }).catch(
                     error => console.log(error)
                 )
          }
        }
       },
       created() {
         //do something after creating vue instance
         let _this = this
         Echo.private('comment-post')
           .listen('.comment.created', (e) => {
             _this.posts[e.key].comments.push(e.comment)
           })
          .listenForWhisper('typing', (e) => {
            if(e.typing) {
              _this.show_dot = true}
            else {
               _this.show_dot = false}
            setTimeout(()=>{
              _this.show_dot = false
            },9000)
          })
         Echo.private('post-event')
            .listen('.post.created', (e) => {
                _this.get_posts()
            })

            // Detect when scrolled to bottom.
             window.addEventListener('scroll', e => {
               const scrollY = window.scrollY
               const visible = document.documentElement.clientHeight
               const pageHeight = document.documentElement.scrollHeight
               const bottomOfPage = visible + scrollY >= pageHeight
               if((bottomOfPage || pageHeight < visible) && this.next_url){
                 this.load_posts();
               }
             });
             this.load_posts();
       },
       mounted() {
            this.get_posts()
        }
    }
</script>
