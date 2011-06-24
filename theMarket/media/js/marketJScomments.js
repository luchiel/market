function changeRating(commentId) {
    $.post(
        '/theMarket/add_vote/' + commentId + '/', $('#comment_form').serialize(),
        function(data) {
            $('#' + commentId + '_rating').html('(+' + data + ')');
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
            }
        }
    );
});

function addComment(productId) {
    $.post(
        '/theMarket/products/' + productId + '/comments/add_comment/', $('#new_comment').serialize(),
        //comment, response_to_id
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
            externalDiv = $('#' + commentId + '_div');
            externalDiv.hide().append(data['form']);
            if(commentId == 0)
                $('#add_root_comment').hide();
            else
                $('#add_root_comment').show();
            $('#response_to_id').val(commentId);
            $('#new_comment_table').css({
                'margin-left': commentId == 0 ? 0 : 40
            });
            $('#id_comment').css('width', 450);
            externalDiv.show();
        }
    );
}

function deleteComment(commentId) {
    $.post(
        '/theMarket/products/comments/' + commentId + '/delete_comment/', $('#comment_form').serialize(),
        function(data) {
            if(data['result'] == 'ok') {
                $('#' + commentId + '_div').remove();
            }
            else {
                alert('You can not delete this comment');
            }
        }
    );
}