function update_indices(ct=false) {
  if ( check_time() === 1 || ct === false ) {
    $.getJSON('/indices', function (data) {
      $.each(data, function (index, json) {
        if (json !== null) {
          $('#' + index).prop('href', '/' + json.index + '/' + json.code);
          var change = parseFloat(json.change);
          if (change > 0) {
            $('#' + index + ' .now').text(json.now).css('color', 'red');
            $('#' + index + ' .change').text(json.change).css('color', 'red');
            $('#' + index + ' .percent').text(json.percent).css('color', 'red');
          } else if (change < 0) {
            $('#' + index + ' .now').text(json.now).css('color', 'green');
            $('#' + index + ' .change').text(json.change).css('color', 'green');
            $('#' + index + ' .percent').text(json.percent).css('color', 'green');
          } else {
            $('#' + index + ' .now').text(json.now);
            $('#' + index + ' .change').text(json.change);
            $('#' + index + ' .percent').text(json.percent);
          };
        };
      });
    }).done(function () {
      update_color();
    });
  };
};
function my_stocks(ct=false) {
  if ( check_time() === 1 || ct === false ) {
    mystocks = $.getJSON('/mystocks', function (json) {
      $('#mystocks').empty();
      $.each(json, function (i, item) {
        if (item !== null && item.name != 'n/a') {
          var last = parseFloat(item.last);
          var href = '"/' + item.index + '/' + item.code + '"';
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
          } else {
            $tr.append($('<td>').text(item.change));
            $tr.append($('<td>').text(item.percent));
          };
          add_color_tr(last, item.high, $tr);
          add_color_tr(last, item.low, $tr);
          add_color_tr(last, item.open, $tr);
          $tr.append($('<td>').text(item.last));
          $tr.appendTo('#mystocks');
        } else if (item.name == 'n/a') {
          var href = '"/' + item.index + '/' + item.code + '"';
          $("<tr onclick='window.location=" + href + ";'>").append(
            $('<td>').text(item.index),
            $('<td>').text(item.code),
            $('<td>').text('n/a'),
            $('<td>').text('n/a'),
            $('<td>').text('n/a'),
            $('<td>').text('n/a'),
            $('<td>').text('n/a'),
            $('<td>').text('n/a'),
            $('<td>').text('n/a'),
            $('<td>').text('n/a')
          ).appendTo('#mystocks');
        };
      });
    });
  };
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
function update_realtime(index, code, ct=false) {
  if ( check_time() === 1 || ct === false ) {
    $.getJSON('/get', { index: index, code: code, q: 'realtime' }, function (json) {
      if (json !== null && json.name != 'n/a') {
        document.title = json.name + ' ' + json.now + ' ' + json.percent;
        var last = chart.data.datasets[0].data;
        if (last.length != 0) {
          last[last.length - 1].y = json.now;
          chart.update();
        };
        if (json.sell5 === null && json.buy5 === null) {
          $('#info').width(480)
          $('#buysell').hide();
        };
        $.each(json, function (key, val) {
          if (key == 'sell5' || key == 'buy5') {
            if (key == 'sell5') {
              var list = '卖盘:&nbsp;';
              var color = 'red';
            } else {
              var list = '买盘:&nbsp;';
              var color = 'green';
            };
            $.each(val, function (i, item) {
              list = list + '<div class="buysell" style="color: ' + color + ';">' + item[0] + '-' + item[1] + '</div>';
            });
            $('header .' + key).html(list);
          } else {
            $('header .' + key).text(val);
          };
        });
      };
    }).done(function () {
      update_color();
    });
  };
};
function update_chart(index, code, ct=false) {
  if ( check_time() === 1 || ct === false ) {
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
};
function update_color() {
  change_color('now');
  change_color('high');
  change_color('low');
  change_color('open');
  var change = parseFloat($('header .change').text());
  if (change > 0) {
    $('header .change').css('color', 'red');
    $('header .percent').css('color', 'red');
  } else if (change < 0) {
    $('header .change').css('color', 'green');
    $('header .percent').css('color', 'green');
  } else {
    $('header .change').css('color', '');
    $('header .percent').css('color', '');
  };
};
function change_color(name) {
  var last = parseFloat($('header .last').text());
  var num = parseFloat($('header .' + name).text());
  if (num > last) {
    $('header .' + name).css('color', 'red');
  } else if (num < last) {
    $('header .' + name).css('color', 'green');
  } else {
    $('header .' + name).css('color', '');
  };
};
function check_time() {
  var date = new Date();
  var hour = date.getUTCHours();
  var day = date.getDay();
  if ( hour >= 1 && hour <= 8 && day >= 1 && day <= 5 ) {
    return 1;
  };
};
