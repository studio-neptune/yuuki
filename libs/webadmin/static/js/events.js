$(function () {
    $.ajax({
        url: "/api",
        type: "GET",
        data: {
          user_name: $("#user_name").val()
        },
        error: function(xhr) {
          alert("Something was wrong.");
        },
        success: function(response) {
            $("#msg_user_name").html(response);
            $("#msg_user_name").fadeIn();
        }
      });
})