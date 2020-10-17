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
            <div class="starter-template">
                <h1>Star Yuuki BOT - WebAdmin</h1>
                <p class="lead">Perfect LINE BOT for Groups Protection.</p>
                <p>The administrator control center of LINE BOT</p>
                <div class="status damage"></div>
            </div>

            <div class="password_box">
                <form class="form-inline mt-2 mt-md-0 login-box" method="post">
                    <input v-model="password" class="form-control mr-sm-2" type="password" placeholder="Type your admin password" aria-label="Login" name="code">
                    <button @click.prevent="authorize" class="btn btn-outline-success my-2 my-sm-0" type="submit">Login</button>
                </form>
            </div>
        </div>
        `,
    data() {
        return {
            password: ""
        }
    },
    methods: {
        authorize() {
            let body = new FormData();
            body.append("code", this.password);
            fetch("/api/verify", {
                    method: "POST",
                    body
                })
                .then(body => body.json())
                .then(data => {
                    if (data.status == 200) {
                        location.reload();
                    } else {
                        $(".status").text("Wrong password");
                        $(".status").fadeIn();
                    }
                });
        }
    }
};