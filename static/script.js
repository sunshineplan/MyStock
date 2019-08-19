function update_realtime(index, code) {
    $.getJSON('/get', { index: index, code: code, q: 'realtime' }, function (json) {
        document.title = json['name'] + ' ' + json['now'] + ' ' + json['percent'];
        $.each(json, function (key, val) {
            if (key == 'sell5' || key == 'buy5') {
                var list = '';
                $.each(val, function (idx, data) {
                    list = list + '<div class="buysell">' + data[0] + '-' + data[1] + '</div>'
                });
                $('.' + key).html(list);
            } else {
                $('.' + key).text(val);
            }
        });
    }).then(() => update_color());
};
function update_chart(index, code) {
    $.get('/get', { index: index, code: code, q: 'chart' }, function (json) {
        chart.data.datasets.forEach((dataset) => {
            dataset.data = json['chart'];
        });
        chart.options.scales.yAxes[0].ticks = {
            suggestedMin: json['last'] / 1.01,
            suggestedMax: json['last'] * 1.01
        };
        chart.update();
    });
};
function update_color() {
    change_color('now')
    change_color('high')
    change_color('low')
    change_color('open')
    change = parseFloat($('.change').text());
    if (change > 0) {
        $('.change').css('color', 'red');
        $('.percent').css('color', 'red');
    } else if (change < 0) {
        $('.change').css('color', 'green');
        $('.percent').css('color', 'green');
    } else {
        $('.change').css('color', '');
        $('.percent').css('color', '');
    }
};
function change_color(name) {
    last = parseFloat($('.last').text());
    num = parseFloat($('.' + name).text());
    if (num > last) {
        $('.' + name).css('color', 'red');
    } else if (num < last) {
        $('.' + name).css('color', 'green');
    } else {
        $('.' + name).css('color', '');
    }
};