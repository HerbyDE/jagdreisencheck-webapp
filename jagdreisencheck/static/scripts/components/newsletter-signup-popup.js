
$(document).ready(function () {
    $(".modal").modal("hide");

    var clicker = eval(getCookie("clicked-pages"));
    var abc = "";


    createCookie("clicked-pages", clicker + 1, 28);

    // Loads at page four.
    if(clicker === 3) $(".modal").modal("show");

});