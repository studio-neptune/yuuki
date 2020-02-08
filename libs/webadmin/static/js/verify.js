/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

$(function () {
    $('form.login-box').on('submit', function (e) {
        $.ajax({
            type: "POST",
            url: "/verify",
            data: $(this).serialize(),
            success: function (data) {
                if (data.status == 200) {
                    Cookies.set('yuuki_admin', data.session);
                    location.reload();
                } else {
                    $(".status").text("Wrong password");
                    $(".status").fadeIn();
                }
            }
        });
        e.preventDefault();
    });
});