$(document).ready(function () {
    $("#id_country").parent().parent().hide();
    $("#id_region").parent().parent().hide();
    $(".card-body button[type=submit]").hide();
    $("#login").show();

    $("#id_company").prepend("<option value='' selected='selected'>"+$(".form-url").data("empty")+"</option>");
    $('.selectpicker').selectpicker('refresh');

});


$("#id_company").change(function () {

    $("#id_country").parent().parent().hide();
    $("#id_region").parent().parent().hide();
    $("#tripNotFound").show();
    $("hr.hide").show();
    $(".card-body button[type=submit]").hide();

    var data = Object;
    var url = $(".form-url").data("url");
    data["company"] = $(this).val();

    $.ajax({
        url: url,
        data: data,
        success: function (data, status, xhr) {
            var countryField = $("#id_country");
            countryField.empty();

            countryField.prepend("<option value='' selected='selected'>"+$(".form-url").data("empty")+"</option>");
            Object.keys(data.results.countries).forEach(function (key) {
                countryField.append("<option value="+key+">"+data.results.countries[key]+"</option>")
            });

            $('.selectpicker').selectpicker('refresh');

            countryField.parent().parent().show();

        },
        error: function (status, xhr) {
            console.log(status, xhr)
        }
    });

});


$("#id_country").change(function () {
   var data = Object;
    var url = $(".form-url").data("url");
    data["country"] = $(this).val();

    $("#id_region").parent().parent().hide();
    $("#tripNotFound").show();
    $("hr.hide").show();
    $(".card-body button[type=submit]").hide();

    $.ajax({
        url: url,
        data: data,
        success: function (data, status, xhr) {
            var regionField = $("#id_region");
            regionField.empty();

            regionField.prepend("<option value='' selected='selected'>"+$(".form-url").data("empty")+"</option>");
            for(var i=0; i < data.results.regions.length; i++) {
                regionField.append("<option value="+data.results.regions[i].value+">"+data.results.regions[i].text+"</option>");
            }

            $('.selectpicker').selectpicker('refresh');

            regionField.parent().parent().show();

        },
        error: function (status, xhr) {
            console.log(status, xhr)
        }
    });
});

$("#id_region").change(function () {
    $("#tripNotFound").hide();
    $("hr.hide").hide();
    $(".card-body button[type=submit]").show();
});