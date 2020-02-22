$(document).ready(function () {
    $(".nav-buttons").not(":eq(0)").remove();

    $('#CreateCompanyForm').hide();
    $('#CreateGameForm').hide();

    $(".ap_quality").hide();
    $(".dog-use").hide();
    $(".ml_quality").hide();
    $(".ac_quality").hide();

    $("textarea").css("min-height: 200px");

    var $pageElements = $(".page-element");
    var this_element = 0;

    for(var i=0; i < $pageElements.length; i++) {
        var element = $pageElements[i];
        if($(element).hasClass("active")) this_element = i;
    }

    $($pageElements[this_element]).show();
    if($($pageElements[this_element]).attr("id", "reviews")) $(".btn-rate").show();

    $("#id_years_as_active_hunter").parent().parent().hide();
    $('#id_countries_visited_for_hunting').parent().parent().hide();

    if($("#id_hunting_license").val() === 'True') {
        $("#id_years_as_active_hunter").parent().parent().show();
        $('#id_countries_visited_for_hunting').parent().parent().show();
    }

});


// Form Validation and Stepper
$("input").on("change", function () {
    var validInputs = [];
    if ($(this).attr("name") === "username" || $(this).attr("name") === "email") {
        $.ajax({
            type: 'GET',
            url: "https://"+window.location.hostname+"/accounts/validate/ue/",
            data: {
                'username': $('#id_username').val(),
                'email': $('#id_email').val()
            },
            success: function (data) {
                data = JSON.parse(data);
                validInputs.length = 0;
                if (data['email'] === false) {
                    $('#id_email').css("border-color", "red");
                    $(".has-error.email").text("A user with this E-Mail already exists.");
                    validInputs.push("F")
                } else {
                    $('#id_email').css("border-color", "darkgreen");
                    $(".has-error.email").text("");
                    validInputs.push("T")
                }
                if (data['username'] === false) {
                    $('#id_username').css("border-color", "red");
                    $(".has-error.username").text("A user with this Username already exists.");
                    validInputs.push("F")
                } else {
                    $('#id_username').css("border-color", "darkgreen");
                    $(".has-error.username").text("");
                    validInputs.push("T")
                }
                if (data["email"] === true && data["username"] === true) {
                    validInputs.push("T")
                }

            }
        });
    }
});

function setError(field) {
    $(this).css("border-color", "red");
    $(this).parent().parent().find(".control-label").find("[data-toggle=tooltip]").popover("hide");
    $(".password-error").show();
    field.parent().find(".control-label").css("color", "red");
    field.parent().parent().find(".control-label").css("color", "red");
    field.css("border-color", "red");
    field.parent().parent().find(".control-label").find("[data-toggle=tooltip]").popover("show",{delay:{ "show": 0, "hide": 3000 }});
    setTimeout(function () {
        field.parent().parent().find(".control-label").find("[data-toggle=tooltip]").popover("hide");
    }, 3000)
}

function setValid(field) {
    $(this).parent().find(".control-label").css("color", "darkgreen");
    $(this).parent().parent().find(".control-label").css("color", "darkgreen");
    $(this).css("border-color", "darkgreen");
    $(this).parent().parent().find(".control-label").find("[data-toggle=tooltip]").popover("hide");
    $(".password-error").hide();
}


$(".next-btn").click(function () {
    var $stepcontainer = $(this).parent().parent().parent();
    var $nextstep = $stepcontainer.next();

    var texttest = /^([\w-\d.\s\p{L}\p{N}\u00c4\u00e4\u00d6\u00f6\u00dc\u00fc\u00df\!\@\#\$\%\^\&\*,]{2,})+$/;
    var mailtest = /^([\w-.]+@([\w-]+\.)+[\w-]{2,5})?$/;
    var numbtest = /^[0-9]+$/;
    // var usertest = /^[0-9a-zA-Z_\-]$/;
    var passtest = /^([a-zA-Z0-9!§$%&=?*+'#\-_><;,:.\u00c4\u00e4\u00d6\u00f6\u00dc\u00fc\u00df]{8,})+$/;
    var datetest = /^([\d]{2,4})+\.+([\d]{2})+\.+([\d]{2})+$/;
    var testdict = {
        "text": texttest,
        "email": mailtest,
        "number": numbtest,
        "password": passtest,
        "date": datetest,
        "hidden": numbtest,
        "checkbox": "/true/"
    };
    var validInputs = [];
    var $validat = [];
    var $reqInputs = [];

    if ($stepcontainer.find("input").length > 0) {
        // Checks all inputs in current step.
        $stepcontainer.find("input").each(function () {
            // Checks all inputs and if they're required.
            if ($(this).prop("required")) {
                // Validates common required inputs via a dict of regex values.
                $reqInputs.push($(this).attr("name"));
                if ($(this).val().length > 0) {
                    var $type = $(this).attr("type");
                    if ($(this).attr("type") === 'checkbox') {
                        if (!$(this)[0].checked) {
                            setError($(this));
                        } else {
                            setValid($(this));
                            $validat.push("T");
                        }
                    } else {
                        if (!testdict[$type].test($(this).val())) {
                            setError($(this));
                        } else {
                            if ($(this).attr("type") === "password" && $(this).attr("name") === "password") {
                                var value = $(this).val();
                                var confirm = $("#id_confirm_passwd");

                                if(value === confirm.val()) {
                                    setValid($(this));
                                    $validat.push("T");
                                } else {
                                    setError($(this));
                                }

                            } else {
                                setValid($(this));
                                $validat.push("T");
                            }
                        }
                    }

                } else {
                    setError($(this));
                }
            }
        });
        $stepcontainer.find("select").each(function () {
            if ($(this).prop("required")) {
                $reqInputs.push($(this).attr("name"));
                if (!$(this).val().length > 0) {
                    $(this).parent().find(".bs-placeholder").css("border-color", "red");
                } else {
                    if ($(this).attr("name") === "agree_to_tos" || $(this).attr("name") === "agree_to_privacy") {
                        if ($(this).val() !== 1) {
                            var $label = $(this).parent().find("label").text();
                            $(this).parent().find(".bs-placeholder").css("border-color", "red");
                            $(this).parent().find("has-error").text("You must accept the " + $label);
                        } else {
                            $(this).parent().find(".bs-placeholder").css("border-color", "darkgreen");
                            $(this).parent().find("has-error").text("");
                        }
                    }
                    $(this).parent().find(".bs-placeholder").css("border-color", "darkgreen");
                    $validat.push("T")
                }
            }
        });
        if (!($reqInputs.length === $validat.length)) {
        } else {
            if ($("#id_username").css("border-color") === "red" || $("#id_email").css("border-color") === "red") {

            } else {
                if ($.inArray("F", validInputs) === -1) {
                    $stepcontainer.hide();
                    $nextstep.show();
                }
            }
        }
    } else {
        // Only true when current step has no inputs.
        $stepcontainer.hide();
        $nextstep.show();
    }
});
$(".prev-btn").click(function () {
    var $step = $(this);
    var $stepcontainer = $step.parent().parent().parent();
    var $prevstep = $stepcontainer.prev();

    $stepcontainer.hide();
    $prevstep.show()

});


// Create Trip form JS
$("#id_alternative_program").change(function () {
    var $initLabel = $("#id_quality_alternative_program").parent().parent().find("label");
    if ($(this).val() === "True") {
        $(".ap_quality").show();
        $("#id_quality_alternative_program").attr("required", "true");
        $initLabel.append("<span style='color: red;'>*</span>");
    } else {
        $(".ap_quality").hide();
        $("#id_quality_alternative_program").removeAttr("required");
    }
});


$("#id_accommodation_type").change(function () {
    var $initLabel = $("#id_accommodation_type").parent().parent().find("label");
    if ($(this).val() !== "SO") {
        $(".ac_quality").show();
        $("#id_accommodation_type").attr("required", "true");
        $initLabel.append("<span style='color: red;'>*</span>");
    } else {
        $(".ac_quality").hide();
        $("#id_accommodation_type").removeAttr("required");
    }
});


$("#id_meal_option").change(function () {
    var $initLabel = $("#id_meal_quality").parent().parent().find("label");
    if ($(this).val() !== "N") {
        $(".ml_quality").show();
        $("#id_meal_quality").attr("required", "true");
        $initLabel.append("<span style='color: red;'>*</span>");
    } else {
        $(".ml_quality").hide();
        $("#id_meal_quality").removeAttr("required");
    }
});


$("#id_use_of_dogs").change(function () {
    var $init1Label = $("#id_dog_purpose").parent().parent().find("label");
    var $init2Label = $("#id_dog_quality").parent().parent().find("label");
    if ($(this).val() === "True") {
        $(".dog-use").show();
        $("#id_dog_purpose").attr("required", "true");
        $("#id_dog_quality").attr("required", "true");
    } else {
        $(".dog-use").hide();
        $("#id_dog_purpose").removeAttr("required");
        $("#id_dog_quality").removeAttr("required");
    }
});
$("#id_hunting_license").change(function () {
    if ($(this).val() === 'False') {
        $('#id_years_as_active_hunter').parent().parent().parent().hide();
        $('#id_years_as_active_hunter').parent().parent().hide();
        $('#id_countries_visited_for_hunting').parent().parent().hide();
    } else {
        $('#id_years_as_active_hunter').parent().parent().parent().show();
        $('#id_years_as_active_hunter').parent().parent().show();
        $('#id_countries_visited_for_hunting').parent().parent().parent().show();
        $('#id_countries_visited_for_hunting').parent().parent().show();
    }
});
$("#id_kind_of_inquiry").change(function () {
    if($(this).val() !== "S") {
        $(".group-travel").show()
    } else {
        $(".group-travel").hide()
    }
});
$("input[type=file]").change(function() {
  var file = $(this)[0].files[0].name;
  $(this).parent().find("label[for=validatedCustomFile]").text(file);
});

// Trip Creation
$('#newCompany').click(function () {
    $("#createTripForm").hide();
    $('#CreateCompanyForm').show();
});
$('#newGame').click(function () {
    $("#createTripForm").hide();
    $('#CreateGameForm').show();
});
$(".hide-form").click(function () {
    $(this).parent().parent().parent().hide();
    $("#createTripForm").show()
});
$('#CreateCompanyForm').submit(function (e) {
    e.preventDefault();
    $.ajax({
        url: '/de/accounts/register/corporate/nameonly/',
        type: "post",
        data: $('#CreateCompanyForm').serialize(),
        success: function (data) {
            if (data.errors) {
                for (var field in data.errors) {
                    $('.errorlist.company').append('<p><b>' + data.errors[field] + '</b></p>');
                }
                return false;
            } else {
                $('#CreateCompanyForm').hide();
                $('#createTripForm').show();
                $('#id_company').append('<option value="' + data.company.pk + '" selected>' + data.company.name + '</option>');
                $('.selectpicker').selectpicker('refresh');
            }
        },
        error: function (xHR) {
            $(".errorlist.company").append('<p><b>' + xHR.status + " " + xHR.statusText + '</b></p>')
        }
    });
});
$('#CreateGameForm').submit(function (e) {
    e.preventDefault();
    $.ajax({
        url: '/de/jagdreisen/create/game/',
        type: "post",
        data: $('#CreateGameForm').serialize(),
        success: function (data) {

            var $gameForm = $('#CreateGameForm');
            var $tripForm = $('#createTripForm');
            var $input = $("#id_game");

            if (data.errors) {
                for (var field in data.errors) {
                    $('.errorlist.game').append('<p><b>' + data.errors[field] + '</b></p>');
                }

                $('#id_game option[value='+data.value+']').attr("selected", true);

                $gameForm.hide();
                $tripForm.show();


            } else {
                $gameForm.hide();
                $tripForm.show();
                $input.append('<option value="' + data.game.pk + '" selected>' + data.game.name + '</option>');
            }

            $('.selectpicker').selectpicker('refresh');

        },
        error: function (xHR) {
            $(".errorlist.game").append('<p><b>' + xHR.status + " " + xHR.statusText + '</b></p>')
        }
    });
});



