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