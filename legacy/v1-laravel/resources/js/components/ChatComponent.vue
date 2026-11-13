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
          chat_object:{'sender_id':'' , 'reciever_id':'' , 'message' : ''},
          validationErrors:[],
          base_url:base_url,
          show_dot:false,
          uri:base_url+'/api/messages'
        }
      },
       props:['user'],
       methods: {
         scrollBottom() {
           this.$nextTick(() => {
             var elem = document.getElementById('Commentbox');
             if (elem) {
               elem.scrollTop = elem.scrollHeight;
             }
           });
         },
         get_chat(user_id){
           var _this = this;
           this.chat_object.reciever_id = user_id;
           axios.get(this.base_url + '/api/messages/' + user_id)
             .then(function (response) {
               if (response.data && response.data.messages !== undefined) {
                 _this.user_chats = response.data.messages;
                 let contact = _this.chats.find(c => c.user_id == user_id);
                 if (contact) {
                   _this.name_u = contact.user_name;
                   _this.image_u = contact.user_image;
                 } else {
                   axios.get(_this.base_url + '/api/profile/' + user_id).then(res => {
                     if (res.data && res.data.user) {
                       _this.name_u = res.data.user.name;
                       _this.image_u = res.data.user.image;
                     }
                   }).catch(e => console.log(e));
                 }
               } else if (response.data && response.data.all) {
                 _this.user_chats = response.data.all;
                 _this.name_u = response.data.user_info.name;
                 _this.image_u = response.data.user_info.image;
               }
               _this.scrollBottom();
             }).catch(function (error) {
               // Fallback to legacy route
               axios.get(_this.base_url + '/chat?send_id=' + _this.user.id + '&recieve_id=' + user_id)
                 .then(function (res) {
                   _this.user_chats = res.data.all;
                   _this.name_u = res.data.user_info.name;
                   _this.image_u = res.data.user_info.image;
                   _this.scrollBottom();
                 }).catch(err => console.log(err));
             });
         },
         all_user(){
           var _this = this;
           axios.get(this.base_url + '/api/messages/conversations')
             .then(function (response) {
               if (response.data && response.data.conversations) {
                 _this.chats = response.data.conversations.map(c => ({
                   user_id: c.user.id,
                   user_name: c.user.name,
                   user_image: c.user.image || (_this.base_url + '/front/images/user.png'),
                   message: c.last_message ? c.last_message.message : '',
                   created_at: c.last_message ? moment(c.last_message.created_at).fromNow() : ''
                 }));
               } else {
                 _this.chats = response.data;
               }
               if (_this.chats.length > 0 && !_this.name_u) {
                 _this.get_chat(_this.chats[0].user_id);
               }
               _this.scrollBottom();
             }).catch(function (error) {
               // Fallback to legacy endpoint
               axios.get(_this.base_url + '/chat/' + _this.user.id).then(function (res) {
                 _this.chats = res.data;
                 if (_this.chats.length > 0 && !_this.name_u) {
                   _this.get_chat(_this.chats[0].user_id);
                 }
                 _this.scrollBottom();
               }).catch(err => console.log(err));
             });
         },
         send_message(){
           var _this = this;
           if (!this.chat_object.message || !this.chat_object.reciever_id) return;
           this.chat_object.sender_id = this.user.id;
           
           axios.post(this.base_url + '/api/messages', {
             reciever_id: this.chat_object.reciever_id,
             message: this.chat_object.message
           }).then(function (response) {
             let sentChat = response.data.chat || response.data;
             _this.user_chats.push(sentChat);
             _this.chat_object.message = '';
             _this.scrollBottom();
             _this.all_user();
           }).catch(function (error) {
             // Fallback to legacy POST endpoint
             axios.post(_this.base_url + '/chat', _this.chat_object).then(function (res) {
               _this.get_chat(_this.chat_object.reciever_id);
               _this.chat_object.message = '';
               _this.scrollBottom();
             }).catch(err => console.log(err));
           });
         },
         showtyping(){
           var _this = this;
           if (window.Echo && _this.chat_object.reciever_id) {
             window.Echo.private('chat.' + _this.chat_object.reciever_id)
               .whisper('typing', {
                 message: _this.user.name + ' is typing',
                 typing: true
               });
           }
           if (window.Echo) {
             window.Echo.private('chat')
               .whisper('typing', {
                 message: _this.user.name + ' is typing',
                 typing: true
               });
           }
         }
       },
       created() {
         let _this = this;
         if (window.Echo && this.user && this.user.id) {
           // Private channel for target user (ChatMessageSent event broadcasts on chat.{reciever_id})
           window.Echo.private('chat.' + this.user.id)
             .listen('.message.sent', (e) => {
               if (e.chat) {
                 if (_this.chat_object.reciever_id == e.chat.sender_id || _this.chat_object.reciever_id == e.chat.reciever_id) {
                   // Append message if current chat conversation matches
                   let exists = _this.user_chats.some(m => m.id === e.chat.id);
                   if (!exists) {
                     _this.user_chats.push(e.chat);
                     _this.scrollBottom();
                   }
                 }
                 _this.all_user();
               }
             })
             .listenForWhisper('typing', (e) => {
               if (e.typing) {
                 _this.show_dot = true;
                 setTimeout(() => { _this.show_dot = false; }, 4000);
               }
             });

           // Global legacy chat channel
           window.Echo.private('chat')
             .listen('.chat.created', (e) => {
               if (_this.chat_object.reciever_id) {
                 _this.get_chat(_this.chat_object.reciever_id);
               }
             })
             .listenForWhisper('typing', (e) => {
               if (e.typing) {
                 _this.show_dot = true;
                 setTimeout(() => { _this.show_dot = false; }, 4000);
               }
             });
         }
       },
       mounted() {
         this.all_user();
       }
    }
</script>
