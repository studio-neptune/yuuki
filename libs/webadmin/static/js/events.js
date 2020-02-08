/*jshint esversion: 6 */

/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

var events = [
    "JoinGroup",
    "KickEvent",
    "CancelEvent",
    "BlackList"
];

function format2html(title, context) {
    return "<div class=\"media pt-3\">" +
        "<p class=\"media-body pb-3 mb-0 small lh-125 border-bottom border-gray\">" +
        "<strong class=\"d-block text-gray-dark\">" + title + "</strong>" +
        context +
        "</p>" +
        "</div>";
}

function log_query(data) {
    $.ajax({
        url: "/api",
        type: "POST",
        data: {
            task: "get_logs",
            data: data
        },
        error: function () {
            $("#events").html("<p class=\"pt-3\">Something was wrong.</p>");
            $("#events").fadeIn();
        },
        success: function (response) {
            let show = "<h6 class=\"border-bottom border-gray pb-2 mb-0\">" + data + "</h6>";
            if (response.result.length) {
                response.result.forEach(element => {
                    show += format2html(
                        element.substring(0, 24),
                        element.substring(26, element.length)
                    );
                });
            } else {
                show += "<p class=\"pt-3\">Nothing</p>";
            }
            $("#events").html(show);
            $("#events").fadeIn();
        }
    });
}

$(function () {
    let url = window.location.href;
    let data = url.substring(url.lastIndexOf('#') + 1);
    if (url.includes("#") && events.includes(data)) {
        log_query(data);
    } else {
        window.location.href = "/";
    }
});