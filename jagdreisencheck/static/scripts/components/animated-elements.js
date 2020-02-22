(function ($) {
  var selectors = [];

  var check_binded = false;
  var check_lock = false;
  var defaults = {
    interval: 250,
    force_process: false
  };
  var $window = $(window);

  var $prior_appeared = [];

  function appeared(selector) {
    return $(selector).filter(function() {
      return $(this).is(':appeared');
    });
  }

  function process() {
    check_lock = false;
    for (var index = 0, selectorsLength = selectors.length; index < selectorsLength; index++) {
      var $appeared = appeared(selectors[index]);

      $appeared.trigger('appear', [$appeared]);

      if ($prior_appeared[index]) {
        var $disappeared = $prior_appeared[index].not($appeared);
        $disappeared.trigger('disappear', [$disappeared]);
      }
      $prior_appeared[index] = $appeared;
    }
  }

  function add_selector(selector) {
    selectors.push(selector);
    $prior_appeared.push();
  }

  // ":appeared" custom filter
  $.expr.pseudos.appeared = $.expr.createPseudo(function() {
    return function(element) {
      var $element = $(element);
      if (!$element.is(':visible')) {
        return false;
      }

      var window_left = $window.scrollLeft();
      var window_top = $window.scrollTop();
      var offset = $element.offset();
      var left = offset.left;
      var top = offset.top;

      if(top + $element.height() >= window_top &&
          top - ($element.data('appear-top-offset') || 0) <= window_top + $window.height() &&
          left + $element.width() >= window_left &&
          left - ($element.data('appear-left-offset') || 0) <= window_left + $window.width()) return true;

    };
  });

  $.fn.extend({
    // watching for element's appearance in browser viewport
    appear: function(selector, options) {
      $.appear(this, options);
      return this;
    }
  });

  $.extend({
    appear: function(selector, options) {
      var opts = $.extend({}, defaults, options || {});

      if (!check_binded) {
        var on_check = function() {
          if (check_lock) {
            return;
          }
          check_lock = true;

          setTimeout(process, opts.interval);
        };

        $(window).scroll(on_check).resize(on_check);
        check_binded = true;
      }

      if (opts.force_process) {
        setTimeout(process, opts.interval);
      }

      add_selector(selector);
    },
    // force elements's appearance check
    force_appear: function() {
      if (check_binded) {
        process();
        return true;
      }
      return false;
    }
  });
})(jQuery);

var $modal = $(".modal");

$modal.on("show.bs.modal", function () {
  var bars = $(this).find(".progress-bar");

  bars.each(function () {

    if ($(this).data("init") === false) {
      $(this).delay(100).animate({
        width: $(this).data("width") + "%"
      }, 200);

      $(this).prop('Counter',0).animate({
        Counter: $(this).data("width")
      }, {
        duration: 1000,
        easing: 'linear',
      });

      $(this).data("init", true);

    }

  })
});


$modal.on("hidden.bs.modal", function () {
  var bars = $(this).find(".progress-bar");
  bars.each(function () {
    $(this).data("init", false);
  })
});


function getValue(numerator, denominator) {
    return numerator / denominator;
}

$(document).ready(function () {
    var circleProgress = $(".circle-progress");

    circleProgress.each(function () {
        var numerator = $(this).data('rating');
        var denominator = $(this).data('denominator');

        numerator = numerator.replace(",", ".");

        $(this).circleProgress({
            value: getValue(numerator, denominator),
            fill: {color: '#61b561'},
            size: 150,
            animation: { duration: 2400, easing: "circleProgressEasing" },
        });

    });
});

