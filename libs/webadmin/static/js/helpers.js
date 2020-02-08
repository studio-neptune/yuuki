/*jshint esversion: 6 */

/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

function format2html(title, context) {
    return "<div class=\"media pt-3\">" +
        "<img class=\"mini-logo mr-2 rounded\" src=\"" + object_server + "/os/p/" + title + "\">" +
        "<p class=\"media-body pb-3 mb-0 small lh-125 border-bottom border-gray\">" +
        "<strong class=\"d-block text-gray-dark\">" + title + "</strong>" +
        context +
        "</p>" +
        "</div>";
}

$(function(){
    $.ajax({
        url: "/api",
        type: "POST",
        data: {
            task: "get_helpers"
        },
        error: function () {
            alert("Something was wrong.");
        },
        success: function (response) {
            let show = "";
            if (response.result.length) {
                response.result.forEach(element => {
                    show += format2html(
                        element,
                        element
                    );
                });
            } else {
                show += "<p class=\"pt-3\">Nothing</p>";
            }
            $("#helpers").html(show);
            $("#helpers").fadeIn();
        }
    });
});