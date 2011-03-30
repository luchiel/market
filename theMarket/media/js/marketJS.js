$(document).ready(function () {

$('#categories').jqGrid({
    url: 'category_tree' + window.location.pathname,
    datatype: 'json',
    height: 'auto',
    treeGrid: true,
    treeGridModel: 'adjacency',
    caption: 'Categories',
    colNames: ['id', 'name', 'true_id'],
    colModel: [
        { name: 'id', hidden: true, key: true },
        { name: 'name' },
        { name: 'true_id', hidden: true }
    ],
    ExpandColumn: 'name',
    ExpandColClick: true,
    autowidth: true,
    onSelectRow: function (rid, status)
    {
        row = $('.jqgrow[id="' + rid + '"]');
        true_id = $('td[aria-describedby=categories_true_id]', row).attr('title');
        window.location.pathname = '/theMarket/categories/' + true_id;
    }
});

$('.ui-jqgrid-titlebar-close').remove();
$('.ui-jqgrid-labels').remove();

});