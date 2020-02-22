
(function () {

    var $hunter = $(".hunter-data");

    $hunter.each(function (idx) {
        if(idx !== 0) {
            $(this).find("input").removeAttr("required");
            $(this).find("select").removeAttr("required");
        }
    });

})(jQuery);