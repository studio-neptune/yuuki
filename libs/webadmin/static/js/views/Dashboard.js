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
            <div class="d-flex align-items-center p-3 my-3 text-white-50 bg-purple rounded shadow-sm">
                <img class="mr-3" :src="profilePicture" alt="" width="48" height="48">
                <div class="lh-100">
                    <h6 class="mb-0 text-white lh-100">{{ profileName }}</h6>
                    <small>{{ version }}</small>
                </div>
            </div>

            <form class="my-3 p-3 bg-white rounded shadow-sm" method="POST">
                <h6 class="border-bottom border-gray pb-2 mb-0">Boardcast</h6>
                <textarea v-model="boardcastText" class="form-control" cols="50" rows="5" placeholder="Type any text message for announcing..."></textarea>
                <div class="mt-1">
                    <label for="name">Audience: </label>
                    <label class="checkbox-inline">
                        <input v-model="boardcastAudience.contacts" type="checkbox" id="inlineCheckbox1" value="option1" disabled> Contacts
                    </label>
                    <label class="checkbox-inline">
                        <input v-model="boardcastAudience.groups" type="checkbox" id="inlineCheckbox2" value="option2"> Groups
                    </label>
                </div>
                <input @click.prevent="boardcast" class="form-control text-light bg-primary mt-1" type="submit" value="Send" />
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
                        <title>{{eventKey}}</title>
                        <rect width="100%" height="100%" :fill="event.color"/>
                        <text x="50%" y="50%" :fill="event.color" dy=".3em">32x32</text>
                    </svg>
                    <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                        <strong class="d-block text-gray-dark">[{{eventKey}}]</strong>
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
        boardcast() {
            let checkpoint = confirm("The message will broadcast, are you sure?");
            if (!this.boardcastText && checkpoint) return;
            let body = new FormData();
            body.set("message", this.boardcastText);
            for (let target in this.boardcastAudience) {
                if (this.boardcastAudience[target]) {
                    body.set("audience", target);
                    fetch("/api/boardcast", {
                        method: "POST",
                        body
                    });
                }
            }
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
            profileName: "",
            boardcastText: "",
            boardcastAudience: {
                contacts: false,
                groups: false,
            },
            profilePicture: "",
            events: {
                "Join Event": {
                    color: "#6f42c1",
                    href: "/events/JoinGroup"
                },
                "Block Event": {
                    color: "#007bff",
                    href: "/events/BlackList"
                },
                "Kick Event": {
                    color: "#e83e8c",
                    href: "/events/KickEvent"
                },
                "Cancel Event": {
                    color: "#00ff00",
                    href: "/events/CancelEvent"
                },
            },
        }
    },
    async created() {
        fetch("/api/profile", {
                credentials: "same-origin"
            })
            .then((body) => body.json())
            .then((profile) => {
                this.version = profile.version;
                this.profileName = profile.name;
                this.profilePicture = profile.picture;
            });
        Object.keys(this.events).forEach(this.fetchEventPreview)
    },
};