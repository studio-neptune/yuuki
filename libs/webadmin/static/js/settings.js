/*
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

function shutdown() {
    $(".container").html("<p class=\"my-3 p-3 bg-white rounded shadow-sm\">Disconnected.</p>");
    $.post("/api", {
        task: "shutdown"
    });
}