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
                <h6 class="border-bottom border-gray pb-2 mb-0">Groups</h6>
                <div id="groups">
                    <div
                     v-for="(group, groupIndex) in groupList"
                     :key="groupIndex"
                     :title="group.id"
                     class="media pt-3">
                        <img v-if="group.pictureStatus" class="mini-logo mr-2 rounded" :src="group.pictureStatus">
                        <svg v-else viewBox="0 0 16 16" class="mini-logo mr-2 rounded" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z"/>
                        </svg>
                        <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                            <strong class="d-block text-gray-dark">{{group.name}}</strong>
                            {{getGroupStatus(group)}}
                        </p>
                        <p v-if="!checkSystemMessage(group)">
                            <a href="#" class="text-danger" title="Leave" @click.prevent="leave_group(group.id)">
                                <svg width="30px" height="30px" viewBox="0 0 16 16" class="bi bi-door-open" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                    <path fill-rule="evenodd" d="M1 15.5a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 0 1h-13a.5.5 0 0 1-.5-.5zM11.5 2H11V1h.5A1.5 1.5 0 0 1 13 2.5V15h-1V2.5a.5.5 0 0 0-.5-.5z"/>
                                    <path fill-rule="evenodd" d="M10.828.122A.5.5 0 0 1 11 .5V15h-1V1.077l-6 .857V15H3V1.5a.5.5 0 0 1 .43-.495l7-1a.5.5 0 0 1 .398.117z"/>
                                    <path d="M8 9c0 .552.224 1 .5 1s.5-.448.5-1-.224-1-.5-1-.5.448-.5 1z"/>
                                </svg>
                            </a>
                        </p>
                    </div>
                </div>
            </div>
            `,
    methods: {
        checkSystemMessage(group) {
            return group.hasOwnProperty("systemMessage") && group.systemMessage
        },
        getGroupStatus(group) {
            if (this.checkSystemMessage(group)) {
                return "";
            }
            const membersCount = group.members ? group.members.length : 0
            const inviteeCount = group.invitee ? group.invitee.length : 0
            return `Members:${membersCount} Invites:${inviteeCount}`;
        },
        leave_group(group_id) {
            const checkpoint = confirm("The group will be removed from the BOT, are you sure?");
            if (!checkpoint) return;
            let body = new FormData();
            body.append("id", group_id);
            fetch("/api/groups", {
                method: "DELETE",
                body
            });
            const deleteIndex = this.groupList.findIndex(group => group.id === group_id);
            this.groupList.splice(deleteIndex, 1);
        },
        async fetchGroupsJoined() {
            return await new Promise((resolve, reject) => fetch("/api/groups", {
                credentials: "same-origin"
            })
                .then((body) => body.json())
                .catch(reject)
                .then(resolve));
        },
        async fetchGroupsInfo(group_ids) {
            return await new Promise((resolve, reject) => fetch(`/api/groups/${group_ids.join(',')}`, {
                credentials: "same-origin"
            })
                .then((body) => body.json())
                .catch(reject)
                .then(resolve));
        }
    },
    data() {
        return {
            groupList: [{
                name: "Loading...",
                systemMessage: true
            }]
        }
    },
    async created() {
        const groupJoined = await this.fetchGroupsJoined();
        if (groupJoined.length) {
            this.groupList = await this.fetchGroupsInfo(groupJoined);
        } else {
            this.groupList = [{
                name: "(empty)",
                systemMessage: true
            }];
        }
    }
};