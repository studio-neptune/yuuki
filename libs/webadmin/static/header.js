(function () {
    $.get("/api/i", function (data) {
        name = data;
    });
    var page_list = {
        "/": "Dashboard",
        "/groups": "Groups",
        "/helpers": "Helpers",
        "/settings": "Settings"
    };
    var nav_list = "";
    for (var p_key in page_list) {
        if (window.location.pathname === p_key)
            nav_list += "<a class=\"nav-link active\" href=\"" + p_key + "\">" + page_list[p_key] + "</a>";
        else
            nav_list += "<a class=\"nav-link js-lookforward\" data-transition-enter=\"slideleft\" href=\"" + p_key + "\">" + page_list[p_key] + "</a>";
    }
    var html_text =
        "<nav class=\"navbar navbar-expand-md navbar-dark fixed-top bg-dark\">" +
        "<a class=\"navbar-brand\" href=\"/\">" + name + " - WebAdmin</a>" +
        "<button class=\"navbar-toggler\" type=\"button\" data-toggle=\"collapse\" data-target=\"#navbarCollapse\"aria-controls=\"navbarCollapse\" aria-expanded=\"false\" aria-label=\"Toggle navigation\">" +
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
    $("#header").html(html_text);
})();