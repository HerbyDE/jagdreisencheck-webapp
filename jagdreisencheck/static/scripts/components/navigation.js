
$(document).scroll(function () {
    var $offset = $(window).scrollTop();
    var $navbar = $(".jrc-navbar");
    var $toolbar = $("#cms-top");

    if ($toolbar.length > 0) {
        $navbar.css('top', '46px');
    } else {
        $navbar.css('top', 'auto');
    }

    if($offset > 90) {
        $navbar.addClass("scrolled");
        $navbar.css("top", "0");
        if($toolbar.length > 0) {
            $navbar.css("top", "46px");
        }
    } else {
        $navbar.removeClass("scrolled");
        if($toolbar.length > 0) {
            $navbar.css("top", "46px");
        }
    }

});

$(".navbar-toggler").click(function () {
    var $nav = $(".jrc-navbar");
    var $toggler = $(".navbar-toggler");

    if($toggler.hasClass("collapsed")) {
        $nav.addClass("toggled");
        $toggler.css("color", "#868e96");
    } else {
        $nav.removeClass("toggled");
        if(!$nav.hasClass("scrolled")) {
             $toggler.css("color", "#ffffff");
        } else {
             $toggler.css("color", "#868e96");
        }

    }

});