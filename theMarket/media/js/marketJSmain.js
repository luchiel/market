function userList(user_id) {
    $.get(
        url_user_list, {},
        function(data) {
            $('#content').html(data);
        }, 'html'
    );
}

function login() {
    $.get(
        url_login, {},
        function(data) {
            $('#content').html(data);
        }, 'html'
    );
}

function register() {
    $.get(
        url_register, {},
        function(data) {
            $('#content').html(data);
        }, 'html'
    );
}

function saveBasketBeforeOrder() {
    formCounter = 0;
    successCounter = 0;
    $('.basket_product').each(function(index) {
        formCounter++;
        $.post(
            '/theMarket/products/' + $(this).attr('product_id') + '/update_basket/', $(this).serialize(),
            function(data) { successCounter++; }
        );
    });
    while(successCounter != formCounter) {}
}

$(document).ready(function () {
});