function shutdown() {
    $(".container").html("<p class=\"my-3 p-3 bg-white rounded shadow-sm\">Disconnected.</p>");
    $.post("/api", {
        task: "shutdown"
    });
}