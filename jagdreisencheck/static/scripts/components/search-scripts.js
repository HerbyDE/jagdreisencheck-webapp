
$(".selectpicker").change(function () {

    var data = {
        'country': $("#id_country").val(),
        'company': $("#id_company").val(),
        'game': $("#id_game").val(),
    };

    var form = $(this).closest("form");

    $.get({
        url: form.data("results-url"),
        data: data,
        success: function (data) {
            var submit = form.find("button[type=submit]");
            var results = submit.data("results-translation");
            var search = submit.data("search-translation");

            if(data.count < 3) {
                submit.html("".concat("<i class=\"fa fa-chevron-right\"></i> ", search));
            } else {
                submit.html("<i class=\"fa fa-chevron-right\"></i> ".concat(data.count, " ", results));
            }

        },
        error: function (xHr, textStatus) {
            console.log(xHr, textStatus)
        }
    });


});