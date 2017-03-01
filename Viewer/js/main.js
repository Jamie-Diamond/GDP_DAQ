$(function() {

    var expandPreviousCheckboxes = $('.expand-previous')
    var goBtn = $('#Go')
    var sections = $('.viewer-section')

    var graph_selects = $('select[name=section_0_Graph]').add($('select[name=section_1_Graph]')).add($('select[name=section_2_Graph]')).add($('select[name=section_3_Graph]')).add($('select[name=section_4_Graph]')).add($('select[name=section_5_Graph]'))
    var graph_type_radios = $('input[name=section_0_Graph_Type]').add($('input[name=section_1_Graph_Type]')).add($('input[name=section_2_Graph_Type]')).add($('input[name=section_3_Graph_Type]')).add($('input[name=section_4_Graph_Type]')).add($('input[name=section_5_Graph_Type]'))
    var axis_limit_radios = $('input[name=section_0_X_Lim_Type]').add($('input[name=section_0_Y_Lim_Type]')).add($('input[name=section_1_X_Lim_Type]')).add($('input[name=section_1_Y_Lim_Type]')).add($('input[name=section_2_X_Lim_Type]')).add($('input[name=section_2_Y_Lim_Type]')).add($('input[name=section_3_X_Lim_Type]')).add($('input[name=section_3_Y_Lim_Type]')).add($('input[name=section_4_X_Lim_Type]')).add($('input[name=section_4_Y_Lim_Type]')).add($('input[name=section_5_X_Lim_Type]')).add($('input[name=section_5_Y_Lim_Type]'))
    var graph_data = {}
    var graph_numbers = []
    var text_numbers = []
    var video_numbers = []

    var default_trail = 5       // in %



    var maxTime
    var minTime
    var data
    var data_file_name
    var anim_frame = 1
    var last_frame = 1
    var data_points_per_second

    function convertToTime(endTime, startTime=0, perc=100){
        timedelta = endTime - startTime;
        newTime = Math.round(timedelta * perc/100);

        seconds = newTime % 60;
        minutes = Math.floor(newTime / 60) % 60;
        hours = Math.floor(newTime/3600)

        if (seconds < 10){
            seconds = "0" + seconds
        }

        if (minutes < 10){
            minutes = "0" + minutes
        }

        return hours + ":" + minutes + ":" + seconds
    }

    function clearSections(callback) {
        sectionsChildren = $('.viewer-section').children()

        sectionsChildren.fadeOut(function(){
            sectionsChildren.remove()
        }, callback())
    }

    function getSettings() {
        settings_json = {}

        var i = 0
        for(i; i < sections.length; i++){
            temp = {
                'graph'         : $('select[name=section_' + i + '_Graph]').val(),
                'graph type'    : $('input[name=section_' + i + '_Graph_Type]:checked').val(),
                'x lim type'    : $('input[name=section_' + i + '_X_Lim_Type]:checked').val(),
                'y lim type'    : $('input[name=section_' + i + '_Y_Lim_Type]:checked').val(),
                'x limit values': [
                    $('input[name=section_' + i + '_X_Axis_Min]').val(),
                    $('input[name=section_' + i + '_X_Axis_Max]').val()
                    ],
                'y limit values': [
                    $('input[name=section_' + i + '_Y_Axis_Min]').val(),
                    $('input[name=section_' + i + '_Y_Axis_Max]').val()
                    ],
                'expand'        : $('input[name=section_' + i + '_expand]').is(":checked")
            }
            settings_json['section '+i] = temp
        }

        var data_length
        for(var key in data){
            data_length = data[key]['data'].length
            data_points_per_second = (data[key]['data'][data_length-1][0] - data[key]['data'][0][0]) / data_length
            break
        }

        if($('input[name=trail-point-value]').val() == ''){
            $('input[name=trail-perc-value]').val(default_trail)
            $('input[name=trail-point-value]').val(Math.floor(data_length*default_trail/100))
        }

        if($('input[name=playback-speed-multiplier]').val() == ''){
            $('input[name=playback-speed-multiplier]').val(5)
        }

        settings_json['trail length'] = parseInt($('input[name=trail-point-value]').val())
        settings_json['playback speed'] = parseInt($('input[name=playback-speed-multiplier]').val())

        return settings_json
    }

    function generateGraphChoicesData() {
        var grouped_data = {}

        i = 0
        for(data_set in data){
            var data_group = data[data_set]["group"]
            if(data_group in grouped_data){
                grouped_data[data_group].push([data[data_set]["verbose name"], data_set])
            } else {
                grouped_data[data_group] = [[data[data_set]["verbose name"], data_set]]
            }
        }

        return grouped_data
    }

    function generateGroupedOptionHTML(grouped_data){
        var html = '<option>None</option>'

        for(group in grouped_data){
            html = html + '<optgroup label="' + group + '">'

            for(index in grouped_data[group]){
                html = html + '<option value="' + grouped_data[group][index][1] + '">' + grouped_data[group][index][0] + '</option>'
            }

            html = html + '</optgroup>'
        }

        return html
    }

    function updateGraphChoices() {
        grouped_data = generateGraphChoicesData()
        html = generateGroupedOptionHTML(grouped_data)
        graph_selects.html(html)
    }

    function clearGraphCoices() {
        graph_selects.html('<option>None</option>')
    }

    function updateGraphOptions(data_set_name, section){
        var data_set_data = data[data_set_name]
        var graph_type_def = data_set_data['default graph type']
        var x_lim_def = data_set_data['default x lim type']
        var y_lim_def = data_set_data['default y lim type']
        var i = section.attr('id')

        section.find('input[name=section_' + i + '_Graph_Type][value=' + graph_type_def + ']').prop('checked', true)
        section.find('input[name=section_' + i + '_X_Lim_Type][value=' + x_lim_def + ']').prop('checked', true)
        section.find('input[name=section_' + i + '_Y_Lim_Type][value=' + y_lim_def + ']').prop('checked', true)

        if(x_lim_def == 'set'){
            var x_limits = data_set_data['x limit values']
            section.find('input[name=section_' + i + '_X_Axis_Min]').val(x_limits[0])
            section.find('input[name=section_' + i + '_X_Axis_Max]').val(x_limits[1])
        }

        if(y_lim_def == 'set'){
            var y_limits = data_set_data['y limit values']
            section.find('input[name=section_' + i + '_Y_Axis_Min]').val(y_limits[0])
            section.find('input[name=section_' + i + '_Y_Axis_Max]').val(y_limits[1])
        }
    }

    (function getDataOptions() {
        select = $("#data-select")
        $.ajax({
            url: "data/",
            success: function(data){
                $(data).find("a:contains(.json)").each(function(){
                    select.append('<option>' + $(this).html().replace('.json', '') + '</option>')
                });
            }
            });
    })()

    $('#data-select').on('change', function(){
        data_file_name = $(this).val()
        var data_url = 'data/' + data_file_name + '.json'
        if(data_file_name == '--'){
            clearGraphCoices()
        } else {
            $.ajax({
                url: 'data/' + data_file_name + '.json',
                success: function(ajax_data){
                    data = ajax_data
                    updateGraphChoices()

                    var data_length

                    for(var key in data){
                        data_length = data[key]['data'].length
                        break
                    }

                    $('input[name=trail-perc-value]').prop('disabled', false)
                    $('input[name=trail-perc-value]').on('keyup', function(){
                        if($(this).val() > 100){
                            $(this).val(100)
                        } else if (Math.floor(data_length * $(this).val()/100) < 1){
                            $('input[name=trail-point-value]').val(1)
                            $('input[name=trail-perc-value]').val(1 / data_length * 100)
                        }

                        $('input[name=trail-point-value]').val(Math.floor(data_length * $(this).val()/100))
                    })
                    $('input[name=trail-point-value]').prop('disabled', false)
                    $('input[name=trail-point-value]').on('keyup', function(){
                        if($(this).val() > data_length){
                            $(this).val(data_length)
                        }
                        $('input[name=trail-perc-value]').val($(this).val() / data_length * 100)
                    })

                },
                error: function (xhr, ajaxOptions, thrownError) {
                    clearGraphCoices()
                    alert('Error loading in file: \n'+thrownError)
                }
            })
        }

    })

    graph_selects.on('change', function(){
        var section = $(this).parent().parent()
        var graph_choice = $(this).val()
        var i = section.attr('id')

        if($(this).val() == 'Video'){
            section.find('input[name=section_' + i + '_Graph_Type]').prop('disabled', true).prop('checked', false)
            section.find('input[name=section_' + i + '_X_Lim_Type]').prop('disabled', true).prop('checked', false)
            section.find('input[name=section_' + i + '_X_Axis_Min]').val('').prop('disabled', true)
            section.find('input[name=section_' + i + '_X_Axis_Max]').val('').prop('disabled', true)
            section.find('input[name=section_' + i + '_Y_Lim_Type]').prop('disabled', true).prop('checked', false)
            section.find('input[name=section_' + i + '_Y_Axis_Min]').val('').prop('disabled', true)
            section.find('input[name=section_' + i + '_Y_Axis_Max]').val('').prop('disabled', true)
        }

        updateGraphOptions(graph_choice, section)
    })

    graph_type_radios.on('click', function(){
        section = $(this).parent().parent().parent()
        var i = section.attr('id')

        if($(this).val() == 'Pol-Scat'){
            section.find('input[name=section_' + i + '_X_Lim_Type][value=Set]').prop('checked', true)
            section.find('input[name=section_' + i + '_X_Lim_Type]').prop('disabled', true)
            section.find('input[name=section_' + i + '_X_Axis_Min]').val(0).prop('disabled', true)
            section.find('input[name=section_' + i + '_X_Axis_Max]').val(360).prop('disabled', true)
            section.find('input[name=section_' + i + '_Y_Lim_Type]').prop('disabled', false)
        } else if($(this).val() == 'Text'){
            section.find('input[name=section_' + i + '_X_Lim_Type]').prop('checked', false).prop('disabled', true)
            section.find('input[name=section_' + i + '_X_Axis_Min]').val('').prop('disabled', true)
            section.find('input[name=section_' + i + '_X_Axis_Max]').val('').prop('disabled', true)
            section.find('input[name=section_' + i + '_Y_Lim_Type]').prop('checked', false).prop('disabled', true)
            section.find('input[name=section_' + i + '_Y_Axis_Min]').val('').prop('disabled', true)
            section.find('input[name=section_' + i + '_Y_Axis_Max]').val('').prop('disabled', true)
        } else {
            section.find('input[name=section_' + i + '_X_Lim_Type]').prop('disabled', false)
            section.find('input[name=section_' + i + '_Y_Lim_Type]').prop('disabled', false)
            section.find('input[name=section_' + i + '_X_Axis_Min]').val('')
            section.find('input[name=section_' + i + '_X_Axis_Max]').val('')
        }
    })

    axis_limit_radios.on('click', function(){
        var control_group = $(this).parent().parent()
        if($(this).val() == 'Set') {
            control_group.children().eq(4).children().prop('disabled', false)
        } else {
            control_group.children().eq(4).children().prop('disabled', true)
        }
    })

    expandPreviousCheckboxes.on('click', function(){
        checked = this.checked
        dropdown = $(this).parent().parent().find('select')

        if (checked == true){
            dropdown.addClass('disabled').val('None')
        }else{
            dropdown.removeClass('disabled')
        }
    })

    goBtn.on('click', function(){
        var maxTimeStr
        var maxTime

        for(var key in data){
            maxTime = data[key]['data'][data[key]['data'].length-1][0] - data[key]['data'][0][0]
            maxTimeStr = convertToTime(maxTime)
            break
        }

        $(this).parent().html(
            '<div id="play-pause-btn" class="play"></div>\
             <input id="time-slider" type="range" value="0" min="0" max="100000"/>\
             <div>00:00:00/' + maxTimeStr + '</div>'
             )

        var timeSlider = $('#time-slider')
        var settings = getSettings()

        clearSections(function(){
            i = 0
            for(i; i < sections.length; i++){
                if(settings['section '+i]['expand']){
                    if(settings['section '+(i-1)]['expand']){
                        sections.eq(i).hide()
                        sections.eq(i-2).removeClass('double').addClass('triple')
                    } else {
                        sections.eq(i).hide()
                        sections.eq(i-1).addClass('double')
                    }
                }

                if(settings['section '+i]['graph'] == 'None') {

                }
                else if(settings['section '+i]['graph'] == 'Video' && !settings['section '+i]['expand']){

                }
                else if(!(settings['section '+i]['expand'])){
                    if(settings['section '+i]['graph type'] && settings['section '+i]['graph type'] == 'Text'){
                        text_numbers.push(i)
                        var xheader = ''
                        if (data[settings['section '+i]['graph']]['x axis title']){
                          xheader = '<div class="text-column-header">'+ data[settings['section '+i]['graph']]['x axis title'] +'</div>'
                        }
                        sections.eq(i).html('<div id="grid-'+i+'-text">' +
                        '<div class="text-title">'+ data[settings['section '+i]['graph']]['verbose name'] +'</div>' +
                        '<div class="text-column-header">Time</div>' +
                        xheader +
                        '<div class="text-column-header">'+ data[settings['section '+i]['graph']]['y axis title'] +'</div>' +
                        '<div class="text-column-header">Conf.</div>' +
                        '<div class="text-data"></div>' +
                        '</div>')

                        var xdata = ''
                        if (data[settings['section '+i]['graph']]['x axis title']){
                          xdata = data[settings['section '+i]['graph']]['data'][anim_frame-1][1].toFixed(2) + '</div><div class="text-data-cell">'
                        }
                        var data_box = $('#grid-'+i+'-text .text-data')
                        data_box.html('<div class="text-data-row"><div class="text-data-cell">' +
                            data[settings['section '+i]['graph']]['data'][anim_frame-1][0].toFixed(2) + '</div><div class="text-data-cell">' +
                            xdata +
                            data[settings['section '+i]['graph']]['data'][anim_frame-1][2].toFixed(2) + '</div><div class="text-data-cell">' +
                            data[settings['section '+i]['graph']]['data'][anim_frame-1][3].toFixed(2) + '</div></div>' + data_box.html())

                        var graph_name = settings['section '+i]['graph']

                        if(!(graph_name in graph_data)){
                            var temp_graph_data = [[],[],[],[]]
                            var loop = 0
                            for(loop; loop < data[graph_name]['data'].length; loop++){
                                var time = data[graph_name]['data'][loop][0]
                                var x = data[graph_name]['data'][loop][1]
                                var y = data[graph_name]['data'][loop][2]
                                var conf = data[graph_name]['data'][loop][3]

                                temp_graph_data[0].push(time)
                                temp_graph_data[1].push(x)
                                temp_graph_data[2].push(y)
                                temp_graph_data[3].push(conf)
                            }
                            graph_data[graph_name] = temp_graph_data
                        }

                    }
                    else if(settings['section '+i]['graph type']){
                        graph_numbers.push(i)

                        var graph_name = settings['section '+i]['graph']
                        var graph_type = settings['section '+i]['graph type']
                        var graph_expa = settings['section '+i]['expand']
                        var graph_xaxis = settings['section '+i]['x lim type']
                        var graph_yaxis = settings['section '+i]['y lim type']

                        sections.eq(i).html('<div class="text-title">'+data[graph_name]['verbose name']+'</div><div id="grid-'+i+'-graph"></div>')
                        CANVAS = document.getElementById('grid-'+i+'-graph');

                        if(!(graph_name in graph_data)){
                            var temp_graph_data = [[],[],[],[]]
                            var loop = 0
                            for(loop; loop < data[graph_name]['data'].length; loop++){
                                var time = data[graph_name]['data'][loop][0]
                                var x = data[graph_name]['data'][loop][1]
                                var y = data[graph_name]['data'][loop][2]
                                var conf = data[graph_name]['data'][loop][3]

                                temp_graph_data[0].push(time)
                                temp_graph_data[1].push(x)
                                temp_graph_data[2].push(y)
                                temp_graph_data[3].push(conf)
                            }
                            graph_data[graph_name] = temp_graph_data
                        }



                        var layout = {
                            autosize: false,
                            width: 500,
                            height: 300,
                            margin: {
                                l: 50,
                                r: 20,
                                b: 40,
                                t: 40,
                                pad: 0
                            },
                            yaxis: {range: [Math.min.apply(null,graph_data[graph_name][2])*0.9, Math.max.apply(null,graph_data[graph_name][2])*1.1]},
                            showlegend: true,
                            legend: {
                                "orientation": "h",
                                x: 0.1,
                                y: 1.1,
                            }
                        };

                        var trace1
                        var xaxis
                        var yaxis

                        if(graph_type == 'Pol-Scat'){
                            layout.orientation = -90
                            layout.margin.t = 20
                            if(graph_yaxis == 'Set'){
                                layout.radialaxis = {range: settings['section '+i]['y limit values']}
                            } else if(graph_yaxis == 'MinMax'){
                                layout.radialaxis = {
                                    range: [Math.min.apply(null, graph_data[graph_name][2]), Math.max.apply(null, graph_data[graph_name][2])]}
                            }

                            var radial = []
                            var thetas = []

                            if(data[graph_name]["default graph type"] != 'Pol-Scat'){
                                for(i in graph_data[graph_name][1].slice(0,settings['trail length'])){
                                    layout.radialaxis.showticklabels = false
                                    radial.push(1)
                                    thetas.push(graph_data[graph_name][2].slice(0,settings['trail length'])[i])
                                }
                            } else {
                                radial = graph_data[graph_name][1].slice(0,1)
                                thetas = graph_data[graph_name][2].slice(0,1)
                            }

                            trace1 = {
                                r: radial,
                                t: thetas,
                                mode: 'markers',
                                type: 'scatter',
                                name: data[graph_name]['verbose name'],
                                marker: {
                                    size: 10,
                                    opacity: 0.7
                                },
                            };

                        }else{
                            var xtitle
                            if(data[graph_name]['x axis title']){
                                xtitle = data[graph_name]['x axis title']
                            } else {
                                xtitle = 'Time (s)'
                            }

                            if(graph_yaxis == 'Set'){
                                layout.yaxis = {range: settings['section '+i]['y limit values'], title: data[graph_name]['y axis title']}
                            }
                            else if(graph_yaxis == 'MinMax'){
                                layout.yaxis = {range: [Math.min.apply(null,graph_data[graph_name][2]),Math.max.apply(null,graph_data[graph_name][2])], title: data[graph_name]['y axis title']}
                            } else {
                                layout.yaxis = {title: data[graph_name]['y axis title']}
                            }

                            if(graph_xaxis == 'Set'){
                                layout.xaxis = {range: settings['section '+i]['x limit values'], title: xtitle}
                            }
                            else if(graph_xaxis == 'MinMax' && xtitle != 'Time (s)'){
                                layout.xaxis = {range: [Math.min.apply(null,graph_data[graph_name][1]),Math.max.apply(null,graph_data[graph_name][1])], title: xtitle}
                            }
                            else if(graph_xaxis == 'MinMax'){
                                layout.xaxis = {range: [Math.min.apply(null,graph_data[graph_name][0]),Math.max.apply(null,graph_data[graph_name][0])], title: xtitle}
                            } else {
                                layout.yaxis = {title: xtitle}
                            }

                            if(xtitle == 'Time (s)'){
                                trace1 = {
                                    x: graph_data[graph_name][0].slice(0,1),
                                    y: graph_data[graph_name][2].slice(0,1),
                                    type: 'scatter',
                                    name: data[graph_name]['verbose name']
                                };
                            } else {
                              trace1 = {
                                  x: graph_data[graph_name][1].slice(0,1),
                                  y: graph_data[graph_name][2].slice(0,1),
                                  type: 'scatter',
                                  name: data[graph_name]['verbose name']
                              };
                            }
                        }

                        var traces = [trace1];

                        Plotly.plot(
                            CANVAS,
                            traces,
                            layout
                        );
                    }
                }
            }

            function goToFrame(frame_no){
              var currentTimePerc = anim_frame / maxTime
              if(currentTimePerc > 1){
                  clearInterval(ticker)

              }else if(frame_no != last_frame){
                  $('#time-slider').val(currentTimePerc*100000)
                  $('#time-slider').next().html(convertToTime(maxTime, 0, currentTimePerc*100) + '/' + maxTimeStr)

                  var min = frame_no - settings['trail length']
                  if (min < 0) {min = 0}
                  for(i in graph_numbers){
                      CANVAS = document.getElementById('grid-'+graph_numbers[i]+'-graph');

                      var graph_name = settings['section '+graph_numbers[i]]['graph']
                      var layout
                      Plotly.purge(CANVAS)
                      var layout = {
                          autosize: false,
                          width: 500,
                          height: 300,
                          margin: {
                              l: 40,
                              r: 20,
                              b: 40,
                              t: 50,
                              pad: 0
                          },
                          showlegend: true,
                          legend: {
                              "orientation": "h",
                              x: 0.1,
                              y: 1.1,
                          }
                      };

                      var trace1
                      var xaxis
                      var yaxis

                      if(settings['section '+graph_numbers[i]]['graph type'] == 'Pol-Scat'){
                          layout.orientation = -90
                          layout.margin.t = 20
                          if(graph_yaxis == 'Set'){
                              layout.radialaxis = {range: settings['section '+i]['y limit values']}
                          } else if(graph_yaxis == 'MinMax'){
                              layout.radialaxis = {
                                  range: [Math.min.apply(null, graph_data[graph_name][2]), Math.max.apply(null, graph_data[graph_name][2])]}
                          }

                          var radial = []
                          var thetas = []

                          if(data[graph_name]["default graph type"] != 'Pol-Scat'){
                              for(i in graph_data[graph_name][1].slice(0,settings['trail length'])){
                                  layout.radialaxis.showticklabels = false
                                  radial.push(1)
                                  thetas.push(graph_data[graph_name][1].slice(frame_no, settings['trail length']+anim_frame)[i])
                              }
                          } else {
                              radial = graph_data[graph_name][2].slice(min, frame_no)
                              thetas = graph_data[graph_name][1].slice(min, frame_no)
                          }

                          trace1 = {
                              r: radial,
                              t: thetas,
                              mode: 'markers',
                              type: 'scatter',
                              name: data[graph_name]['verbose name'],
                              marker: {
                                  size: 10,
                                  opacity: 0.7
                              },
                          };
                      } else {
                          var xtitle
                          if(data[graph_name]['x axis title']){
                              xtitle = data[graph_name]['x axis title']
                          } else {
                              xtitle = 'Time (s)'
                          }

                          if(graph_yaxis == 'Set'){
                              layout.yaxis = {range: settings['section '+i]['y limit values'], title: data[graph_name]['y axis title']}
                          }
                          else if(graph_yaxis == 'MinMax'){
                              layout.yaxis = {range: [Math.min.apply(null,graph_data[graph_name][2]),Math.max.apply(null,graph_data[graph_name][2])], title: data[graph_name]['y axis title']}
                          } else {
                              layout.yaxis = {title: data[graph_name]['y axis title']}
                          }

                          if(graph_xaxis == 'Set'){
                              layout.xaxis = {range: settings['section '+i]['x limit values'], title: xtitle}
                          }
                          else if(graph_xaxis == 'MinMax' && xtitle != 'Time (s)'){
                              layout.xaxis = {range: [Math.min.apply(null,graph_data[graph_name][1]),Math.max.apply(null,graph_data[graph_name][1])], title: xtitle}
                          } else if(graph_xaxis == 'MinMax'){
                              layout.xaxis = {range: [Math.min.apply(null,graph_data[graph_name][0]),Math.max.apply(null,graph_data[graph_name][0])], title: xtitle}
                          } else {
                              layout.yaxis = {title: xtitle}
                          }

                          if(xtitle == 'Time (s)'){
                              trace1 = {
                                  x: graph_data[graph_name][0].slice(min, frame_no),
                                  y: graph_data[graph_name][2].slice(min, frame_no),
                                  type: 'scatter',
                                  name: data[graph_name]['verbose name']
                              };
                          } else {
                            trace1 = {
                                x: graph_data[graph_name][1].slice(min, frame_no),
                                y: graph_data[graph_name][2].slice(min, frame_no),
                                type: 'scatter',
                                name: data[graph_name]['verbose name']
                            };
                          }
                      }

                      var traces = [trace1];

                      Plotly.plot(
                          CANVAS,
                          traces,
                          layout
                      );

                  }



                  for(i in text_numbers){
                    var xdata = ''
                    if (data[settings['section '+text_numbers[i]]['graph']]['x axis title']){
                      xdata = data[settings['section '+text_numbers[i]]['graph']]['data'][frame_no-1][1].toFixed(2) + '</div><div class="text-data-cell">'
                    }
                    var data_box = $('#grid-'+text_numbers[i]+'-text .text-data')
                    data_box.html('<div class="text-data-row"><div class="text-data-cell">' +
                        data[settings['section '+text_numbers[i]]['graph']]['data'][frame_no-1][0].toFixed(2) + '</div><div class="text-data-cell">' +
                        xdata +
                        data[settings['section '+text_numbers[i]]['graph']]['data'][frame_no-1][2].toFixed(2) + '</div><div class="text-data-cell">' +
                        data[settings['section '+text_numbers[i]]['graph']]['data'][frame_no-1][3].toFixed(2) + '</div></div>' + data_box.html())
                  }
                  last_frame = frame_no
              }
            }

            var pp_btn = $('#play-pause-btn')
            var ticker
            var ticks_per_second = 30

            pp_btn.on('click', function(){
              if($(this).attr('class') == 'play'){
                    $(this).attr('class', 'pause')
                    ticker = setInterval(function(){
                        var frames_per_tick = data_points_per_second/ticks_per_second * $('input[name=playback-speed-multiplier]').val()
                        anim_frame += frames_per_tick
                        frame_no = Math.floor(anim_frame)
                        goToFrame(frame_no)
                    }, 1000/ticks_per_second)
                } else {
                    $(this).attr('class', 'play')
                    clearInterval(ticker)
                }
            })

            timeSlider.on("change mousemove", function() {
                $(this).next().html(convertToTime(maxTime,minTime,$(this).val()/1000) + '/' + maxTimeStr)
                $(this).attr('class', 'play')
                clearInterval(ticker)
                anim_frame = Math.floor(maxTime * $(this).val()/100000)
                goToFrame(anim_frame)
            });
        })

    })

})
