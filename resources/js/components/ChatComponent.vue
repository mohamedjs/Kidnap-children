<template>
    <div class="dashboard-profile">
      <div class="customer-dashboard-content-page">
        <div class="friends-chat chat-users-aside">
          <div class="search-box">
            <input class="search-input" id="search-input" type="text" placeholder="Search">
            <div class="search-icon-box"><i class="fas fa-search"></i></div>
          </div>
          <div class="chat-users-scroll-box-container" id="friends-box">
            <ul class="chat-users-scroll-box list-unstyled friends-message show-content-box perfect-scroll" id="friends-message">
              <li v-if="chats.length > 0" v-for="chat in chats">
                <a @click.prevent="get_chat(chat.user_id)" class="mesaage-box gray-box" href="#">
                  <div class="photo-box">
                    <div class="dot-box"></div>
                    <img class="img-fluid" :src="chat.user_image">
                  </div>
                  <div class="message-content">
                    <h3 class="sender-name">{{chat.user_name}}</h3>
                    <p class="message">{{chat.message}}</p>
                  </div>
                  <div class="message-date">
                    <p class="date">{{ chat.created_at }}</p>
                  </div>
                </a>
              </li>
            </ul>
            <ul class="chat-users-scroll-box list-unstyled friends-search perfect-scroll" id="friends-search">
              <li v-if="chats.length > 0" v-for="chat in chats">
                <a @click.prevent="get_chat(chat.user_id)" class="friend-box d-flex justify-content-between" href="#">
                  <div class="d-flex justify-content-start">
                    <div class="friend-photo-box"><img class="img-fluid" :src="chat.user_image"></div>
                    <p class="friend-name">{{chat.user_name}}</p>
                  </div>
                  <div class="active-state"></div>
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div class="chat-box">
          <div class="chat-header d-flex justify-content-between align-items-center">
            <div class="d-flex justify-content-start">
              <div class="close-chat-btn"><i class="fas fa-arrow-left"></i></div>
              <div class="photo-box"><img class="img-fluid" :src="image_u"></div>
              <h4 class="title"> {{name_u}}</h4>
            </div>
            <div class="dropdown show setting-dropdown"><a class="chat-menu" href="#" role="button" id="profile-setting-dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-h"></i></a>
              <div class="dropdown-menu" aria-labelledby="profile-setting-dropdown" style="top: 25px !important"><a class="dropdown-item" href="#" data-toggle="modal" data-target="#add-to-group">Add to group</a><a class="dropdown-item" href="#">Unfriend</a><a class="dropdown-item" href="#">Block</a><a class="dropdown-item" href="customer-profile__reviews.html">View Profile</a></div>
            </div>
          </div>
          <div class="chat-conversation perfect-scroll" id="Commentbox">
            <div>
              <div v-if="user_chats.length > 0" v-for="user_chat in user_chats" class="messages-container">
                <ul :class="'messages-list '+ [ user_chat.sender_id=== user.id ? 'sent-messages' : 'received-messages'] +' list-unstyled'">
                  <li>
                    <div class="message">
                      <p>{{user_chat.message}}</p>
                    </div>
                  </li>
                </ul>
                <div class="clearfix"></div>
              </div>
            </div>
            <div class="typing" v-if="show_dot" id="loading">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
          <form @submit.prevent="send_message()">
            <div class="send-message">
              <input @keydown="showtyping()" class="form-control" v-model="chat_object.message" type="text" placeholder="Type a message ...">
              <button class="icon-box" type="submit"><i class="fas fa-share"></i></button>
            </div>
          </form>
        </div>
      </div>
    </div>
</template>

<script>
    export default {
       data(){
        return{
          data : new FormData(),
          chats:[],
          name_u:'',
          image_u:'',
          user_id_send:'',
          user_chats : [],
          chat_object:{'sender_id':'' , 'reciever_id':1 , 'message' : ''},
          validationErrors:[],
          base_url:base_url,
          show_dot:false,
          uri:base_url+'/chat'
        }
      },
       props:['user'],
       methods: {
         get_chat(user_id){
           var _this = this;
           axios.get(this.uri+'?send_id='+this.user.id+'&recieve_id='+user_id).then(function (response) {
             console.log(response);
             _this.user_chats = response.data.all;
             _this.name_u=response.data.user_info.name
             _this.image_u=response.data.user_info.image
             _this.chat_object.reciever_id=response.data.user_info.id
             var elem = document.getElementById('Commentbox');
             elem.scrollTop = elem.scrollHeight;
           }).catch(
             error => console.log(error)
           )
         },
         all_user(){
           var _this = this;
           axios.get(this.uri+'/'+this.user.id).then(function (response) {
             console.log(response);
             _this.chats = response.data
             if(_this.chats.length > 0){
               _this.get_chat(_this.chats[0].user_id)
              }
              var elem = document.getElementById('Commentbox');
              elem.scrollTop = elem.scrollHeight;
           }).catch(
             error => console.log(error)
           );
         },
         send_message(){
           var _this = this;
           this.chat_object.sender_id = this.user.id
           console.log(this.chat_object)
           axios.post(this.uri,this.chat_object).then(function (response) {
             console.log(response);
             _this.get_chat(_this.chat_object.reciever_id);
             _this.chat_object = {'sender_id':'' , 'reciever_id':'' , 'message' : ''}
             var elem = document.getElementById('Commentbox');
             elem.scrollTop = elem.scrollHeight;
           }).catch(
             error => console.log(error)
           )
         },
         showtyping(){
           var _this = this
            Echo.private('chat')
                .whisper('typing', {
                message: _this.user.name+' is typing',
                typing: true
              })
         }
       },
       created() {
         //do something after creating vue instance
         let _this = this
         Echo.private('chat')
           .listen('.chat.created', (e) => {
             _this.get_chat(_this.chat_object.reciever_id);
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
       },
       mounted() {
         this.all_user();

        }
    }
</script>
