function my_stocks() {
    $.getJSON('/mystocks', function (json) {
        $('tbody').empty();
        $.each(json, function (i, item) {
            if (item !== null) {
                var last = parseFloat(item.last);
                var href = '"/' + item.index + '/' + item.code + '"'
                var $tr = $("<tr onclick='window.location=" + href + ";'>").append(
                    $('<td>').text(item.index),
                    $('<td>').text(item.code),
                    $('<td>').text(item.name)
                );
                add_color_tr(last, item.now, $tr);
                if (parseFloat(item.change) > 0) {
                    $tr.append($('<td>').text(item.change).css('color', 'red'));
                    $tr.append($('<td>').text(item.percent).css('color', 'red'));
                } else if (parseFloat(item.change) < 0) {
                    $tr.append($('<td>').text(item.change).css('color', 'green'));
                    $tr.append($('<td>').text(item.percent).css('color', 'green'));
                };
                add_color_tr(last, item.high, $tr);
                add_color_tr(last, item.low, $tr);
                add_color_tr(last, item.open, $tr);
                $tr.append($('<td>').text(item.last));
                $tr.appendTo('tbody');
            };
        });
    });
};
function add_color_tr(last, value, element) {
    if (last < parseFloat(value)) {
        element.append($('<td>').text(value).css('color', 'red'));
    } else if (last > parseFloat(value)) {
        element.append($('<td>').text(value).css('color', 'green'));
    } else {
        element.append($('<td>').text(value));
    };
};
function update_realtime(index, code) {
    $.getJSON('/get', { index: index, code: code, q: 'realtime' }, function (json) {
        if (json !== null) {
            document.title = json['name'] + ' ' + json['now'] + ' ' + json['percent'];
            var last = chart.data.datasets[0].data;
            if (last.length != 0) {
                last[last.length - 1]['y'] = json['now'];
                chart.update();
            };
            $.each(json, function (key, val) {
                if (key == 'sell5' || key == 'buy5') {
                    var list = '';
                    $.each(val, function (idx, data) {
                        list = list + '<div class="buysell">' + data[0] + '-' + data[1] + '</div>';
                    });
                    $('.' + key).html(list);
                } else {
                    $('.' + key).text(val);
                };
            });
        };
    }).done(function () {
        update_color();
    });
};
function update_chart(index, code) {
    $.get('/get', { index: index, code: code, q: 'chart' }, function (json) {
        if (json !== null) {
            chart.data.datasets.forEach((dataset) => {
                dataset.data = json['chart'];
            });
            chart.options.scales.yAxes[0].ticks = {
                suggestedMin: json['last'] / 1.01,
                suggestedMax: json['last'] * 1.01
            };
            chart.update();
        };
    });
};
function update_color() {
    change_color('now');
    change_color('high');
    change_color('low');
    change_color('open');
    var change = parseFloat($('.change').text());
    if (change > 0) {
        $('.change').css('color', 'red');
        $('.percent').css('color', 'red');
    } else if (change < 0) {
        $('.change').css('color', 'green');
        $('.percent').css('color', 'green');
    } else {
        $('.change').css('color', '');
        $('.percent').css('color', '');
    };
};
function change_color(name) {
    var last = parseFloat($('.last').text());
    var num = parseFloat($('.' + name).text());
    if (num > last) {
        $('.' + name).css('color', 'red');
    } else if (num < last) {
        $('.' + name).css('color', 'green');
    } else {
        $('.' + name).css('color', '');
    };
};
