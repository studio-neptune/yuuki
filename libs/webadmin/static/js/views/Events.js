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
                <h6 class="border-bottom border-gray pb-2 mb-0">Event: {{doctype}}</h6>
                <div id="events">
                    <div class="media pt-3">
                        <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                            <strong class="d-block text-gray-dark">{{title}}</strong>
                            {{content}}
                        </p>
                    </div>
                </div>
            </div>
        `,
    props: ["doctype"],
    data() {
        return {
            data: []
        }
    },
    created() {
        fetch(`/api/events/${this.doctype}`, {
                credentials: "same-origin"
            })
            .then((body) => body.json())
            .then((events) => {
                this.data = events.map((event) => {
                    return {
                        title: event.substring(0, 24),
                        content: event.substring(26, element.length)
                    }
                });
            });
    },
};