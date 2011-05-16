$(document).ready(function () {

$('#categories').jqGrid({
    url: 'category_tree' + window.location.pathname + '0/',
    datatype: 'json',
    height: 'auto',
    treeGrid: true,
    treeGridModel: 'adjacency',
    caption: 'Categories',
    colNames: ['id', 'name', 'true_id'],
    colModel: [
        { name: 'id', hidden: true, key: true },
        { name: 'name', width: 400, search: true },
        { name: 'true_id', hidden: true }
    ],
    ExpandColumn: 'name',
    ExpandColClick: true,
    rowNum: 200,
    shrinkToFit: 400,
    width: 200,
    onSelectRow: function (rid, status)
    {
        row = $('.jqgrow[id="' + rid + '"]');
        true_id = $('td[aria-describedby=categories_true_id]', row).attr('title');
        window.location.pathname = '/theMarket/categories/' + true_id;
    }
});

$('#categories').jqGrid('filterToolbar', { stringResult: true, searchOnEnter: false });

$('.ui-jqgrid-titlebar-close').remove();
$('.ui-jqgrid-labels').remove();

});