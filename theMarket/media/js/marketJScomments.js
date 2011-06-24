function toggleTree(commentId) {
    element = $('#' + commentId + '_div');
    if(element.is(':hidden')) {
        s = 'Click to hide';
        p = '-';
    }
    else {
        s = 'Click to show';
        p = '+';
    }
    element.slideToggle(400);
    //element.toggle();
    $('#' + commentId + '_togglestatus').html(s);
}

var BAD_COMMENT = 5;//-10

function changeRating(commentId, value) {
    $('#vote_input').val(value);
    $.post(
        '/theMarket/add_vote/' + commentId + '/', $('#comment_form').serialize(),
        function(data) {
            if(data['result'] == 'ok') {
                $('#' + commentId + '_rating').html('(' + data['rating'] + ')');
                if(!data['votes_ok'])
                    $('.vote_input').hide();
                if(parseInt(data['rating']) > BAD_COMMENT)
                    $('#' + d[i]['id'] + '_toggleerror').html('');
            }
            else if(data['result'] != '') {
                alert(data['result']);
            }
        }
    );
}

$(document).ready(function () {
    $.get(
        '/theMarket/products/' + productIdForTree + '/get_comments/', $('#comment_form').serialize(),
        function(data) {
            var d = data['comment_list'];
            for(var i = 0; i < d.length; ++i) {
                $('#' + d[i]['parent'] + '_subtree').append(d[i]['block']);
                if(d[i]['rating'] <= BAD_COMMENT) {
                    toggleTree(d[i]['id']);
                    $('#' + d[i]['id'] + '_toggleerror').html('Comment was rated too negatively');
                }
            }
        }
    );
});

function addComment(productId) {
    $.post(
        '/theMarket/products/' + productId + '/comments/add_comment/', $('#new_comment').serialize(),
        function(data) {
            if(data['result'] == 'ok') {
                commentId = $('#response_to_id').val();
                $('#' + commentId + '_subtree')
                    .append(data['comment']);
                $('#new_comment_table').remove();
                $('#add_root_comment').show();
            }
            else {
                function addErrorListToField(errorField) {
                    if(data[errorField]) {
                        var ul = $('<ul>');
                        $.each(data[errorField], function(index, value) {
                            var li = $('<li>');
                            li.append(value).appendTo(ul);
                        });
                        $('#' + errorField + 's').html('');
                        ul.addClass('errorlist').appendTo($('#' + errorField + 's'));
                    }
                }
                addErrorListToField('comment_error');
            }
        }
    );
    return false;
}

function addResponse(productId, commentId) {
    $.get(
        '/theMarket/products/' + productId + '/comments/add_comment_field/' + commentId + '/',
        $('#comment_form').serialize(),
        function(data) {
            $('#new_comment').remove();
            externalDiv = $('#' + commentId + '_subtree');
            if(commentId == 0) {
                $('#add_root_comment').hide();
                externalDiv.append(data['form']);
            }
            else {
                $('#add_root_comment').show();
                externalDiv.prepend(data['form']);
            }
            $('#response_to_id').val(commentId);
            $('#id_comment').css('width', 500);
        }
    );
}

function deleteComment(commentId) {
    $.post(
        '/theMarket/products/comments/' + commentId + '/delete_comment/', $('#comment_form').serialize(),
        function(data) {
            if(data['result'] == 'ok') {
                $('#' + commentId + '_toggler').remove();
                $('#' + commentId + '_div').remove();
            }
            else {
                alert('You can not delete this comment');
            }
        }
    );
}