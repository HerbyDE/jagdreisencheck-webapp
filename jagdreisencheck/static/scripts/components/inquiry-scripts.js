

$("#AddHunterForm").click(function (e) {
    // e.preventDefault();

    var url = $(this).data("href");

    $.get({
        url: url,
        data: {
            extraForms: $(this).data("forms")
        },
        success: function (data) {
            var $html = $.parseHTML(data.form);
            var $hunterData = $(".hunter-data");
            $hunterData.last().after($html);

            $hunterData.each(function (idx) {
                if(idx !== $hunterData.length) $(this).find(".delete-hunter").remove();
            });

            $(".selectpicker").selectpicker("refresh");

            $("#AddHunterForm").data("forms", $hunterData.length + 1);
            $("input[name=hunterdata_set-TOTAL_FORMS]").val($hunterData.length + 1);

        },
        error: function (textStatus) {
            if(textStatus.status === 500) return alert("Error 500: Internal server error. Please try again in 10 minutes.");
        }
    })

});


$(document).on("click", ".delete-hunter",function () {
    // e.preventDefault();

    var url = $(this).data("href");
    var $deleteHunter = $(this);

    $.get({
        url: url,
        data: {
            extraForms: $(this).data("forms"),
            removeForm: true
        },
        success: function (data) {
            var $hunterData = $(".hunter-data");

            $deleteHunter.parent().parent().remove();

        },
        error: function (textStatus) {
            if(textStatus.status === 500) return alert("Error 500: Internal server error. Please try again in 10 minutes.");
        }
    })

});


$(".btn-inquiry").click(function () {
    var $btn = $(this);

    if($btn.data("read") === "False") {
        $.get({
            url: $btn.data("url"),
            data: {
                iq: $btn.data("id"),
            }
        })
    }

});