
/**
 * First we will load all of this project's JavaScript dependencies which
 * includes Vue and other libraries. It is a great starting point when
 * building robust, powerful web applications using Vue and Laravel.
 */

require('./bootstrap');

window.Vue = require('vue');

import VeeValidate from 'vee-validate';
Vue.use(VeeValidate);
// moment for date formate
window.moment = require('moment');
window.moment.locale(window.default_locale);
Vue.prototype.moment = window.moment;
//loader
import InfiniteLoading from 'vue-infinite-loading';
Vue.use(InfiniteLoading, {
  slots: {
   noMore: 'No Data To Show:(',
 }
});


/**
 * The following block of code may be used to automatically register your
 * Vue components. It will recursively scan this directory for the Vue
 * components and automatically register them with their "basename".
 *
 * Eg. ./components/ExampleComponent.vue -> <example-component></example-component>
 */

// const files = require.context('./', true, /\.vue$/i)
// files.keys().map(key => Vue.component(key.split('/').pop().split('.')[0], files(key).default))

Vue.component('example-component', require('./components/ExampleComponent.vue').default);
Vue.component('vue-home', require('./components/HomeComponent.vue').default);
Vue.component('vue-profile', require('./components/ProfileComponent.vue').default);
Vue.component('inner-post-vue',require('./components/InnerPostComponent').default);
Vue.component('inner-post-vue',require('./components/InnerPostComponent').default);
Vue.component('found-person-vue',require('./components/FoundPersonComponent').default);
Vue.component('missed-person-vue',require('./components/MissedPersonComponent').default);
Vue.component('chat-vue',require('./components/ChatComponent').default);
/**
 * Next, we will create a fresh Vue application instance and attach it to
 * the page. Then, you may begin adding components to this application
 * or customize the JavaScript scaffolding to fit your unique needs.
 */

const app = new Vue({
    el: '#app'

});
