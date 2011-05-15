function changeRating(commentId) {
    $.post(
        '/theMarket/add_vote/' + commentId + '/', $('#' + commentId + '_comment_form').serialize(),
        function(data) {
            $('#' + commentId + '_rating').html('(+' + data + ')');
        }
    );
}

function addComment(productId) {
    $.post(
        '/theMarket/products/' + productId + '/comments/add_comment/', $('#new_comment').serialize(),
        function(data) {
            if(data['result'] == 'ok') {
                $('#comments').append(data['page']);
                $('#mark_errors').html('');
                $('#comment_errors').html('');
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
}

function deleteComment(commentId) {
    $.post(
        '/theMarket/products/comments/' + commentId + '/delete_comment/', $('#' + commentId + '_comment_form').serialize(),
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