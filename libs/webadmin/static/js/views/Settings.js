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
                <p v-if="shutdownStatus" class="my-3 p-3 bg-white">Disconnected.</p>
                <div v-else>
                    <h6 class="border-bottom border-gray pb-2 mb-0">Settings</h6>
                    <a
                     v-for="(setting, settingKey, settingIndex) in settings"
                     :key="settingIndex"
                     class="media text-muted pt-3"
                     href="#"
                     @click.prevent="setting.action">
                        <svg class="bd-placeholder-img mr-2 rounded" width="32" height="32" xmlns="http://www.w3.org/2000/svg"
                            preserveAspectRatio="xMidYMid slice" focusable="false" role="img" aria-label="Placeholder: 32x32">
                            <title>{{settingKey}}</title>
                            <rect width="100%" height="100%" :fill="setting.color"/>
                            <text x="50%" y="50%" :fill="setting.color" dy=".3em">32x32</text>
                        </svg>
                        <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                            <strong class="d-block text-gray-dark">{{settingKey}}</strong>
                            <span id="Join_setting">{{setting.preview}}</span>
                        </p>
                    </a>
                </div>
            </div>
            `,
    methods: {
        shutdown() {
            this.shutdownStatus = true;
            fetch(`/api/shutdown`, {
                credentials: "same-origin"
            });
        }
    },
    data() {
        return {
            shutdownStatus: false,
            settings: {
                Profile: {
                    color: "#007bff",
                    icon: "#6f42c1",
                    preview: "Edit LINE profile of the console BOT.",
                    action: () => this.$router.push({path: "/profile"})
                },
                "Yuuki Configure": {
                    color: "#e83e8c",
                    icon: "#6f42c1",
                    preview: "Settings for the BOT works.",
                    action: () => alert("Unavailable")
                },
                Shutdown: {
                    color: "#6f42c1",
                    icon: "#6f42c1",
                    preview: "Turn off the BOT.",
                    action: this.shutdown
                },
            }
        }
    }
};