/*jshint esversion: 6 */

/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

function nav_items(active, path, path_name) {
    if (active)
        return "<a class=\"nav-link active\" href=\"" + path + "\">" + path_name + "</a>";
    return "<a class=\"nav-link\" data-transition-enter=\"slideleft\" href=\"" + path + "\">" + path_name + "</a>";
}

function header2html(yuuki_name) {
    let page_list = {
        "/": "Dashboard",
        "/groups": "Groups",
        "/helpers": "Helpers",
        "/settings": "Settings"
    };
    let nav_list = "";
    Object.keys(page_list).forEach(p_key => {
        if (window.location.pathname === p_key)
            nav_list += nav_items(true, p_key, page_list[p_key])
        else
            nav_list += nav_items(false, p_key, page_list[p_key])
    });
    return "<nav class=\"navbar navbar-expand-md navbar-dark fixed-top bg-dark\">" +
        "<a class=\"navbar-brand\" href=\"/\">" + yuuki_name + " - WebAdmin</a>" +
        "<button class=\"navbar-toggler\" type=\"button\" data-toggle=\"collapse\"          data-target=\"#navbarCollapse\"aria-controls=\"navbarCollapse\" aria-expanded=\"false\" aria-label=\"Toggle         navigation\">" +
        "<span class=\"navbar-toggler-icon\"></span>" +
        "</button>" +
        "<div class=\"collapse navbar-collapse\" id=\"navbarCollapse\">" +
        "<ul class=\"navbar-nav mr-auto\"></ul>" +
        "<a href=\"/logout\"><button class=\"btn btn-outline-success my-2 my-sm-0\">Logout</button></a>" +
        "</div>" +
        "</nav>" +
        "<div class=\"nav-scroller bg-white shadow-sm\">" +
        "<nav class=\"nav nav-underline\">" + nav_list + "</nav>" +
        "</div>";
}

$(function () {
    $.get("/api/i", function (data) {
        $("#header").html(header2html(data));
    });
});