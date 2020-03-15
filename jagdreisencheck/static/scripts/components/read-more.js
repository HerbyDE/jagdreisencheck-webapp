// Read more function
$('.read-more-button').click(function () {
    var $paragraph = $(this).parent().parent()[0];
    var $rt = $(this).parent().parent().find(".review-text");
    var $more = $(this).data('more');
    var $less = $(this).data('less');

    if ($($paragraph).data('expand') === 0) {
        $($paragraph).data('expand', 1);
        $($paragraph).css("max-height", "none");
        $($rt).css("margin-bottom", "75px");
        $(this).parent().parent().find(".read-more").css("background", "none").css("bottom", "50px");
        $('.read-more-button').html($less + ' <i class="fa fa-chevron-circle-up"></i>');
        return $($paragraph)
    }
    if ($($paragraph).data('expand') === 1) {
        $($paragraph).data('expand', 0);
        $($paragraph).css("max-height", "220px");
        $($rt).css("margin-bottom", "auto");
        $(this).parent().parent().find(".read-more").css("background", "rgba(255,255,255,.67)").css("bottom", "90px");
        $('.read-more-button').html($more + ' <i class="fa fa-chevron-circle-down"></i>');
        return $($paragraph)
    }
});

// Check for empty paragraphs
$(document).ready(function () {
    var paragraphs = $(".rating-reply").find("p");

    paragraphs.each(function () {
        if ($(this).text().length < 2 && !$(this).hasClass('quill-editor')) {
            $(this).remove();
        }

        $(this).css('margin', 0);

    });

    renderReviewLikes();

});

// Vote for the usefulness of reviews
function renderReviewLikes(){
    var cookie = JSON.parse(getCookie('jagdreisencheck_review')) || {};
    var helpful_reviews = [$('.btn-vote').data('target')];

    for(var k in cookie) {
        if(cookie.hasOwnProperty(k)) {
            if(helpful_reviews.includes(parseInt(k))) {
                var containerID = "#helpfulness-".concat(k);

                $(''.concat(containerID, ' .fa-thumbs-up')).parent().attr('disabled', 'disabled');
                $(''.concat(containerID, ' .fa-thumbs-down')).parent().attr('disabled', 'disabled');

                if(cookie[k]['direction'] === "up") {
                    $(''.concat(containerID, ' .fa-thumbs-up')).parent().removeClass('btn-default').addClass('btn-success');
                } else {
                    $(''.concat(containerID, ' .fa-thumbs-down')).parent().removeClass('btn-default').addClass('btn-danger');
                }
            }
        }

    }
}

$(".btn-vote").click(function () {
    var btn = $(this);
    var url = $(this).data('url');
    var target = $(this).data('target');
    var direction = $(this).data('direction');
    
    var cookie = JSON.parse(getCookie('jagdreisencheck_review')) || {};

    if(!cookie.hasOwnProperty(target)) {
        $.ajax({
            url: url,
            data: {target: target, direction: direction},
            method: "post",
            success: function (data, status, xhr) {
                cookie[target] = {direction: direction};
                createCookie('jagdreisencheck_review', JSON.stringify(cookie));
                btn.parent().find('.thumbs-up').text(data.data['likes']);
                btn.parent().find('.thumbs-down').text(data.data['dislikes']);
                renderReviewLikes();
            },
            error: function (status, xhr) {
                console.log(status, xhr);
            }
        });
    }
});