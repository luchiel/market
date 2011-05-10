$(document).ready(function () {

$('#products_table').jqGrid({
    //http://www.trirand.com/blog/jqgrid/jqgrid.html
    url: 'product_grid' + window.location.pathname + '1/',
    datatype: 'json',
    height: 'auto',
    caption: 'Products',
    colNames: ['id', 'name', 'true_id', 'image'],
    colModel: [
        { name: 'id', hidden: true, key: true },
        { name: 'name' },
        { name: 'true_id', hidden: true },
        { name: 'image' }
    ],
    rowNum: 20,
    rowList: 10, 20, 30,
    pager: '#products_pager',
    sortname: 'name',
    sortorder: 'asc',
    onSelectRow: function (rid, status)
    {
        row = $('.jqgrow[id="' + rid + '"]');
        true_id = $('td[aria-describedby=products_true_id]', row).attr('title');
        window.location.pathname = '/theMarket/products/' + true_id;
    }
});

//$('#products_table').jqGrid('filterToolbar', { stringResult: true, searchOnEnter: false });

$('.ui-jqgrid-titlebar-close').remove();
$('.ui-jqgrid-labels').remove();

});