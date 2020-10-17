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
    </div>
    `,
    router,
    methods: {
        async verifyAccess() {
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
        router() {
            this.verifyAccess();
        },
    },
    created() {
        this.verifyAccess();
    },
    data() {
        return {
            accessStatus: false,
            router: this.$router.currentRoute,
            pageList: {
                "/dashboard": "Dashboard",
                "/groups": "Groups",
                "/helpers": "Helpers",
                "/settings": "Settings"
            }
        }
    }
}).$mount('#app')