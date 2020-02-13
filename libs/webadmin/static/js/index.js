/*jshint esversion: 6 */

/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

function init(id, data) {
    $.ajax({
        url: "/api",
        type: "POST",
        data: {
            task: "get_logs",
            data: data
        },
        error: function () {
            $(id).text("Something was wrong.");
        },
        success: function (response) {
            let ajax_result = response.result;
            if (ajax_result.length)
                $(id).text(ajax_result[ajax_result.length - 1]);
            else
                $(id).text("Nothing");
        }
    });
}

$(function () {
    init("#Join_Event", "JoinGroup");
    init("#Kick_Event", "KickEvent");
    init("#Cancel_Event", "CancelEvent");
    init("#Block_Event", "BlackList");
});