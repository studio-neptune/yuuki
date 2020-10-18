/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

export default {
    template: `
            <div class="text-center my-3 p-3 bg-white rounded shadow-sm">
                <h2 class="border-bottom border-gray pb-2 mb-0">Star Yuuki BOT</h2>
                <p class="mt-3">The perfectest LINE Group Protective BOT.</p>
                <img class="rounded w-50 mt-5 mb-5" v-show="logo" :src="logo" alt="Logo" />
                <div class="mx-auto mt-3 w-75">
                    <p class="bg-dark text-light rounded p-3">
                        This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.<br />
                        If a copy of the MPL was not distributed with this file, You can obtain one at<br />
                        <a class="text-light" href="http://mozilla.org/MPL/2.0/" target="_blank" rel="noreferrer noopener">http://mozilla.org/MPL/2.0/</a>.
                    </p>
                    <p>
                        <a class="mr-1" title="Homepage" href="https://line.starinc.xyz/star-yuuki-bot/" target="_blank" rel="noreferrer noopener">
                            <svg width="30px" height="30px" viewBox="0 0 16 16" class="bi bi-house-door-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                              <path d="M6.5 10.995V14.5a.5.5 0 0 1-.5.5H2a.5.5 0 0 1-.5-.5v-7a.5.5 0 0 1 .146-.354l6-6a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 .146.354v7a.5.5 0 0 1-.5.5h-4a.5.5 0 0 1-.5-.5V11c0-.25-.25-.5-.5-.5H7c-.25 0-.5.25-.5.495z"/>
                              <path fill-rule="evenodd" d="M13 2.5V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z"/>
                            </svg>
                        </a>
                        <a class="ml-1" title="Repository" href="https://github.com/star-inc/star_yuuki_bot" target="_blank" rel="noreferrer noopener">
                            <svg width="30px" height="30px" viewBox="0 0 16 16" class="bi bi-code-slash" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" d="M4.854 4.146a.5.5 0 0 1 0 .708L1.707 8l3.147 3.146a.5.5 0 0 1-.708.708l-3.5-3.5a.5.5 0 0 1 0-.708l3.5-3.5a.5.5 0 0 1 .708 0zm6.292 0a.5.5 0 0 0 0 .708L14.293 8l-3.147 3.146a.5.5 0 0 0 .708.708l3.5-3.5a.5.5 0 0 0 0-.708l-3.5-3.5a.5.5 0 0 0-.708 0zm-.999-3.124a.5.5 0 0 1 .33.625l-4 13a.5.5 0 0 1-.955-.294l4-13a.5.5 0 0 1 .625-.33z"/>
                            </svg>
                        </a>
                    </p>
                    <p>&copy; 2020 <a class="text-dark" href="https://starinc.xyz" target="_blank" rel="noreferrer noopener">Star Inc.</a></p>
                </div>
            </div>
            `,
    data() {
        return {
            logo: ""
        }
    },
    created() {
        fetch("/logo", {
            credentials: "same-origin"
        })
            .then((body) => body.text())
            .then((text) => this.logo = text)
    },
};