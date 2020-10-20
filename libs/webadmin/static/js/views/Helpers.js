/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

export default {
    template: `
            <div class="my-3 p-3 bg-white rounded shadow-sm">
                <h6 class="border-bottom border-gray pb-2 mb-0">Helper</h6>
                <div id="helpers">
                    <div
                     v-for="(helper, helperIndex) in helperList"
                     :key="helperIndex"
                     :title="helper.id"
                     class="media pt-3">
                        <img v-if="helper.picture" class="mini-logo mr-2 rounded" :src="helper.picture">
                        <svg v-else viewBox="0 0 16 16" class="mini-logo mr-2 rounded" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                        </svg>
                        <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                            <strong class="d-block text-gray-dark">{{helper.name}}</strong>
                            {{helper.status}}
                        </p>
                    </div>
                </div>
            </div>
            `,
    data() {
        return {
            helperList: [{name: "Loading..."}]
        }
    },
    created() {
        fetch("/api/helpers", {
            credentials: "same-origin"
        })
            .then((body) => body.json())
            .then((helper_list) => {
                this.helperList = helper_list.length ? helper_list : [{name: "(empty)"}];
            });
    }
};