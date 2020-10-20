/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

export default {
    template: `
        <div>
            <div :title="profileId" class="d-flex align-items-center p-3 my-3 text-white-50 bg-purple rounded shadow-sm">
                <img v-if="profilePicture" width="48" height="48" class="mr-3" :src="profilePicture">
                <svg v-else width="48" height="48" viewBox="0 0 16 16" class="mr-3" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                </svg>
                <div class="lh-100">
                    <h6 class="mb-0 text-white lh-100">{{ profileName }}</h6>
                    <small>{{ version }}</small>
                </div>
            </div>

            <form class="my-3 p-3 bg-white rounded shadow-sm" method="POST">
                <h6 class="border-bottom border-gray pb-2 mb-0">Broadcast</h6>
                <textarea v-model="broadcastText" class="form-control" cols="50" rows="5" placeholder="Type any text message for announcing..." :disabled="broadcastStatus"></textarea>
                <div class="mt-1">
                    <label for="name">Audience: </label>
                    <label class="checkbox-inline">
                        <input v-model="broadcastAudience.contacts" type="checkbox" id="inlineCheckbox1" value="option1" disabled> Contacts
                    </label>
                    <label class="checkbox-inline">
                        <input v-model="broadcastAudience.groups" type="checkbox" id="inlineCheckbox2" value="option2" :disabled="broadcastStatus" > Groups
                    </label>
                </div>
                <input @click.prevent="broadcast" class="form-control text-light bg-primary mt-1" type="submit" value="Send" :disabled="broadcastStatus" />
            </form>

            <div class="my-3 p-3 bg-white rounded shadow-sm">
                <h6 class="border-bottom border-gray pb-2 mb-0">Recent updates</h6>
                <router-link
                 v-for="(event, eventKey, eventIndex) in events"
                 :key="eventIndex"
                 class="media text-muted pt-3"
                 :to="event.href">
                    <svg class="bd-placeholder-img mr-2 rounded" width="32" height="32" xmlns="http://www.w3.org/2000/svg"
                        preserveAspectRatio="xMidYMid slice" focusable="false" role="img" aria-label="Placeholder: 32x32">
                        <title>{{event.title}}</title>
                        <rect width="100%" height="100%" :fill="event.color"/>
                        <text x="50%" y="50%" :fill="event.color" dy=".3em">32x32</text>
                    </svg>
                    <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                        <strong class="d-block text-gray-dark">[{{event.title}}]</strong>
                        <span>{{getPreview(event)}}</span>
                    </p>
                </router-link>
            </div>
        </div>
        `,
    methods: {
        getPreview(event) {
            return "preview" in event ? event.preview : "Loading...";
        },
        async broadcast() {
            if (!this.broadcastText) return alert("Empty message");
            const checkpoint = confirm("The message will be broadcast, are you sure?");
            if (!checkpoint) return;
            this.broadcastStatus = true;
            let body = new FormData();
            body.set("message", this.broadcastText);
            await Promise.all(Object.keys(this.broadcastAudience).map((target) => {
                if (this.broadcastAudience[target]) {
                    body.set("audience", target);
                    return fetch("/api/broadcast", {
                        method: "POST",
                        body
                    });
                }
            }));
            this.broadcastText = "";
            this.broadcastStatus = false;
        },
        async fetchEventPreview(eventKey) {
            const result = await this.getEventInfo(eventKey);
            if (result.length > 0) {
                this.$set(this.events[eventKey], "preview", result[result.length - 1]);
            } else {
                this.$set(this.events[eventKey], "preview", "(empty)");
            }
        },
        async getEventInfo(eventKey) {
            return await new Promise((resolve, reject) => fetch(`/api/events/${eventKey}`, {
                credentials: "same-origin"
            })
                .then((body) => body.json())
                .catch(reject)
                .then(resolve));
        }
    },
    data() {
        return {
            version: "",
            profileId: "",
            profileName: "",
            profilePicture: "",
            broadcastStatus: false,
            broadcastText: "",
            broadcastAudience: {
                contacts: false,
                groups: false,
            },
            events: {
                JoinGroup: {
                    title: "Join Event",
                    color: "#6f42c1",
                    href: "/events/JoinGroup"
                },
                BlackList: {
                    title: "Block Event",
                    color: "#007bff",
                    href: "/events/BlackList"
                },
                KickEvent: {
                    title: "Kick Event",
                    color: "#e83e8c",
                    href: "/events/KickEvent"
                },
                CancelEvent: {
                    title: "Cancel Event",
                    color: "#00ff00",
                    href: "/events/CancelEvent"
                },
            },
        }
    },
    created() {
        fetch("/api/profile", {
            credentials: "same-origin"
        })
            .then((body) => body.json())
            .then((profile) => {
                this.profileId = profile.id;
                this.version = profile.version;
                this.profileName = profile.name;
                this.profilePicture = profile.picture;
            });
        Object.keys(this.events).forEach(this.fetchEventPreview)
    },
};