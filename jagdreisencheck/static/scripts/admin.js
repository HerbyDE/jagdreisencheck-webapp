$(document).ready(function () {
    let $model = $("#id_model");
    let $fields = $("#id_fields");
    $model.change(function () {

        $.ajax({
            url: "/search/admin/fetch/model/fields/",
            method: "GET",
            dataType: "JSON",
            data: {
                modelID: $model.val()
            },
            success: function (data) {
                $fields.children().remove();
                for (let i = 0; i < data.data.length; i++) {
                    $fields.append('<option value="' + data.data[i][0] + '">' + data.data[i][1] + '</option>')
                }
            },
            error: function (data, xHR) {
                console.log(data);
                console.log(xHR);
            }

        })


    })
});