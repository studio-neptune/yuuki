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
                    $(".status").text("Wrong password")
                }
            }
        });
        e.preventDefault();
    });
});