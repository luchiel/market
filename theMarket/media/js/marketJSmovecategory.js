$(document).ready(function () {

$('#move_category').jqGrid({
    url: 'category_tree' + window.location.pathname + $('#category_id').attr('value') + '/',
    datatype: 'json',
    height: 'auto',
    treeGrid: true,
    treeGridModel: 'adjacency',
    caption: 'Categories',
    colNames: ['id', 'name', 'true_id'],
    colModel: [
        { name: 'id', hidden: true, key: true },
        { name: 'name', width: 400 },
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
        $('#id_parent').attr('value', $('td[aria-describedby=categories_name]', row).attr('title'));
        $('#id_parent_id').attr('value', $('td[aria-describedby=categories_true_id]', row).attr('title'));
    }
});

$('.ui-jqgrid-titlebar-close').remove();
$('.ui-jqgrid-labels').remove();

});