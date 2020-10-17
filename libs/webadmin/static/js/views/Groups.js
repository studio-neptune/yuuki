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
                     class="media pt-3">
                        <img class="mini-logo mr-2 rounded" :src="group.pictureStatus">
                        <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                            <strong class="d-block text-gray-dark">{{group.name}}</strong>
                            {{group.id}}
                        </p>
                    </div>
                </div>
            </div>
            `,
    methods: {
        async fetchGroupsJoined() {
            return await new Promise((resolve, reject) => fetch("/api/groups", {
                credentials: "same-origin"
            })
                .then((body) => body.json())
                .catch(reject)
                .then(resolve));
        },
        async fetchGroupsInfo(groupIds) {
            return await new Promise((resolve, reject) => fetch(`/api/groups/${groupIds.join(',')}`, {
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
                name: "Loading..."
            }]
        }
    },
    async created() {
        const groupJoined = await this.fetchGroupsJoined();
        if (groupJoined.length) {
            this.groupList = await this.fetchGroupsInfo(groupJoined);
        } else {
            this.groupList = [{
                name: "(empty)"
            }];
        }
    }
};