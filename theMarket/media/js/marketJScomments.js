function changeRating(commentId) {
    $.post(
        '/theMarket/add_vote/' + commentId + '/', $('#comment_form').serialize(),
        function(data) {
            $('#' + commentId + '_rating').html('(+' + data + ')');
        }
    );
}

function addComment(productId) {
    $.post(
        '/theMarket/products/' + productId + '/comments/add_comment/', $('#new_comment').serialize(),
        //mark, comment, response_to_id
        function(data) {
            if(data['result'] == 'ok') {
                $('#comments').append(data['comment']);
                //look where to append!
                $('#new_comment_table').remove();
                $('#add_root_comment').attr('hidden', '');
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
                
                addErrorListToField('mark_error');
                addErrorListToField('comment_error');
            }
        }
    );
    return false;
}

function addResponse(productId, commentId) {
    $('#new_comment_table').remove();
    $.get(
        '/theMarket/products/' + productId + '/comments/add_comment_field/' + commentId + '/',
        $('#comment_form').serialize(),
        function(data) {
            externalDiv = $('#comment' + commentId);
            //check later if it does blink
            externalDiv.attr('hidden', 'hidden').append(data['form']);
            $('#add_root_comment').attr('hidden', commentId == 0 ? 'hidden': '');
            $('#response_to_id').val(commentId);
            var widthParam = 40 * data['depth'];
            $('#new_comment_table').css({
                'margin-left': widthParam//, 'width': 600 - widthParam
            });
            $('#id_comment').css('width', 450);// - widthParam);
            externalDiv.attr('hidden', '');
        }
    );
}

function deleteComment(commentId) {
    $.post(
        '/theMarket/products/comments/' + commentId + '/delete_comment/', $('#comment_form').serialize(),
        function(data) {
            if(data['result'] == 'ok') {
                $('#' + commentId + '_table').remove();
            }
            else {
                alert('You can not delete this comment');
            }
        }
    );
}