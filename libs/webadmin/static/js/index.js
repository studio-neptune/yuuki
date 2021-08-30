/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

import Cookies from 'https://cdn.jsdelivr.net/npm/js-cookie@rc/dist/js.cookie.min.mjs';

import Login from "./views/Login.js";
import Dashboard from "./views/Dashboard.js";
import Groups from "./views/Groups.js";
import Helpers from "./views/Helpers.js";
import Settings from "./views/Settings.js";
import Profile from "./views/Profile.js";
import Events from "./views/Events.js";
import About from "./views/About.js";
import NotFound from "./views/NotFound.js";

const router = new VueRouter({
    routes: [{
        path: '/',
        component: Login
    },
        {
            path: '/dashboard',
            component: Dashboard
        },
        {
            path: '/groups',
            component: Groups
        },
        {
            path: '/helpers',
            component: Helpers
        },
        {
            path: '/settings',
            component: Settings,
        },
        {
            path: '/profile',
            component: Profile,
        },
        {
            path: '/events/:doctype',
            component: Events,
            props: true
        },
        {
            path: '/about',
            component: About,
            props: true
        },
        {
            path: '*',
            component: NotFound
        },
    ]
})

new Vue({
    template: `
    <div>
        <div v-if="accessStatus" class="nav-scroller bg-white shadow-sm pt-1 pb-1">
            <nav class="nav nav-underline">
                <router-link
                 v-for="(item, target, itemId) in pageList"
                 :key="itemId"
                 class="nav-link"
                 data-transition-enter="slideleft"
                 :to="target">{{item}}</router-link>
            </nav>
        </div>
        <main id="app" role="main" class="container">
            <router-view></router-view>
        </main>
        <div class="text-center m-5">
            <a title="About SYB" @click.prevent="about" href="#">
                <svg width="25px" height="25px" viewBox="0 0 16 16" class="bi bi-info-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                    <path d="M8.93 6.588l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588z"/>
                    <circle cx="8" cy="4.5" r="1"/>
                </svg>
            </a>
        </div>
    </div>
    `,
    router,
    methods: {
        about() {
            if (this.$router.currentRoute.path === "/about") {
                this.$router.push({path: "/"})
            } else {
                this.$router.push({path: "/about"})
            }
        },
        verifyAccess() {
            if (this.$router.currentRoute.path === "/about") return;
            if (Cookies.get('yuuki_admin')) {
                if (this.$router.currentRoute.path === "/") {
                    this.$router.push({
                        path: "/dashboard"
                    });
                }
                this.accessStatus = true;
            } else {
                if (this.$router.currentRoute.path !== "/") {
                    this.$router.push({
                        path: "/"
                    });
                }
                this.accessStatus = false;
            }
        },
    },
    watch: {
        $route() {
            this.verifyAccess();
        }
    },
    created() {
        this.verifyAccess();
    },
    data() {
        return {
            accessStatus: false,
            pageList: {
                "/dashboard": "Dashboard",
                "/groups": "Groups",
                "/helpers": "Helpers",
                "/settings": "Settings"
            }
        }
    }
}).$mount('#app')