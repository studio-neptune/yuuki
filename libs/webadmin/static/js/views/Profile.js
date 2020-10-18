/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

export default {
    template: `
            <div class="text-center my-3 card">
                    <div class="mx-auto w-100 p-5 card-header" >
                        <img class="rounded" :src="profilePicture" alt="Profile Picture" width="128" height="128">
                    </div>
                <div v-if="!modify">
                    <div class="mx-auto mt-3 card-body">
                        <h6 class="text-dark lh-100">{{ profileName }}</h6>
                        <p class="mt-3 mb-3 text-secondary" v-html="statusMessage"></p>
                        <button class="btn btn-primary" @click="switchButton">Modify</button>
                    </div>
                    </div>
                <div v-else>
                    <div class="mx-auto mt-3 card-body">
                        <input class="form-control text-dark lh-100" v-model="profileName" maxlength="20" />
                        <textarea class="form-control mt-3 mb-3 text-secondary" v-model="profileStatus" maxlength="1000"></textarea>
                        <button class="btn btn-primary" @click="switchButton">Save</button>
                    </div>
                </div>
            </div>
            `,
    methods: {
        switchButton() {
            if (this.modify) {
                let body = new FormData();
                body.append("name", this.profileName);
                body.append("status", this.profileStatus);
                fetch("/api/profile", {
                    method: "PUT",
                    body
                });
            }
            this.modify = !this.modify;
        },
        escapeHtml(text) {
            let map = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;",
            };
            return text.replace(/[&<>"']/g, function (m) {
                return map[m];
            });
        },
    },
    computed: {
        statusMessage() {
            return this.escapeHtml(this.profileStatus).replace(/\n/g, "<br />");
        },
    },
    data() {
        return {
            profileName: "",
            profileStatus: "",
            profilePicture: "",
            modify: false
        }
    },
    created() {
        fetch("/api/profile", {
            credentials: "same-origin"
        })
            .then((body) => body.json())
            .then((profile) => {
                this.profileName = profile.name;
                this.profileStatus = profile.status;
                this.profilePicture = profile.picture;
            });
    }
};