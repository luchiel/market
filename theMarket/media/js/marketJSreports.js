function parameterExtention(is_column) {    var dimension = is_column ? 'column' : 'row';    $('#id_' + dimension).change(function() {        $.get(            '/theMarket/reports/extend_params/' + is_column + '/', $('#parameters').serialize(), //0 is row            function(data) {                params = $('#' + dimension + '_parameters');                params.html('');                if(data['extendable'] == 'true') {                    var select = $('<select>').attr('name', 'detail' + is_column);                    var opt = data['parameters']['options'];                    for(var i = 0; i < opt.length; ++i) {                        select.append($('<option>').val(i).html(opt[i]));                    }                    params.append($('<label>').html(data['parameters']['comment']));                    params.append(select);                }            }        );        $('#output_report_button').attr(            'disabled', $('#id_row').val() == $('#id_column').val() ? 'disabled' : ''        );    });}function outputReport() {    $.post(        '/theMarket/reports/output/', $('#parameters').serialize(),        function(data) {            $('#results')                .append($('<p>').html('Your report will be here:').addClass('message')                    .append($('<a>')                        .attr('href', '/theMarket/reports/output/' + data['report'] + '/')                        .html('/theMarket/reports/output/' + data['report'] + '/')                        .addClass('report_link'))                );        }    );    return false;}function datePicking(name) {    var format = 'dd.mm.yy';    $(name).datepicker(        {            dateFormat: format,            changeMonth: true,            changeYear: true,            defaultDate: -1        }    );}$(document).ready(function () {    $('#id_row').val(0);    $('#id_column').val(1);    datePicking('#id_start_date');    datePicking('#id_end_date');    parameterExtention(0);    parameterExtention(1);});