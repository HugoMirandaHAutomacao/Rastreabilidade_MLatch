$(document).ready(function () {
    const loadHours = () => {
        const body = $("#hourSelect")
        body.empty()
        body.append('<option selected value="-1">Filtre por Hora</option>')
  
        for (i = 0; i <= 24; i++) {
            body.append(`<option value="${i}">${i}:00</option>`)
        }
    }
  
    loadHours()
  
    const grid = new gridjs.Grid({
        columns: ["Código", "Data"],
        resizable: true,
        search: true,
        sort: true,
        pagination: {
            limit: 9,
            resetPageOnUpdate: true,
        },
        language: {
            'search': {
                'placeholder': 'Pesquisar na tabela'
              },
              'pagination': {
                'previous': 'Anterior',
                'next': 'Próximo',
                'showing': 'Mostrando',
                'results': () => 'Resultados'
              }
        },
        data: []
      }).render(document.getElementById("tableAprovados"));
  
    const updateTable = async (dataArray) => {
        return new Promise((resolve, reject) => {
          grid.updateConfig({data: dataArray}).forceRender()
        })
  
    }
  
    $("#searchButton").click(function() {
        const data = $("#dateSelect").val() || ""
        const hour = parseInt($("#hourSelect").val()) >= 0 ? parseInt($("#hourSelect").val()) : ""
        const receita = parseInt($("#receitasSelect").val()) >= 0 ? parseInt($("#receitasSelect").val()) : ""
        const ciclo = $("#cycleSelect").val()
  
        let form_data = new FormData()
        form_data.append("hora", hour)
        form_data.append("receita", receita)
        form_data.append("data", data)
  
        $.ajax({
            url: `/searchAprovas`,
            method: "GET",
            contentType: false,
            cache: false,
            processData: false,
            method: "POST",
            data: form_data,
            success: async (res) => {

              console.log(res.data)
      
                    let dataArray = res.data.map((aprova, indx) => {
                      
                        return [aprova.code, aprova.date]
                    })
  
                    updateTable(dataArray)
            }
        }).then(async () => {
           await new Promise((resolve, reject) => {
                      setTimeout(function () {
                        resolve()
                      }, 100)
            })
        })
    })
  
    $("#seeModal").click(function () {
        $("#modal_grafico").modal("show")
    })
  
  
  
    
  
    // ########################################################################### \\
    //                                                                             \\
    //                               AREA DO GRAFICO                               \\
    //                                                                             \\
    // ########################################################################### \\
  
            //######## Gráfico totalizador ########## \\
  
            // Create root element
        // https://www.amcharts.com/docs/v5/getting-started/#Root_element
        var root = am5.Root.new("main_canvas");
        
        
        // Set themes
        // https://www.amcharts.com/docs/v5/concepts/themes/
        root.setThemes([
          am5themes_Animated.new(root)
        ]);
        
        
        // Create chart
        // https://www.amcharts.com/docs/v5/charts/xy-chart/
        var chart = root.container.children.push(am5xy.XYChart.new(root, {
          panX: true,
          panY: true,
          wheelX: "panX",
          wheelY: "zoomX",
          pinchZoomX:true
        }));
        
        
        // Add cursor
        // https://www.amcharts.com/docs/v5/charts/xy-chart/cursor/
        var cursor = chart.set("cursor", am5xy.XYCursor.new(root, {
          behavior: "none"
        }));
        cursor.lineY.set("visible", false);
        
        
        // Create axes
        // https://www.amcharts.com/docs/v5/charts/xy-chart/axes/
        var xAxis = chart.xAxes.push(am5xy.ValueAxis.new(root, {
            maxPrecision: 0,
            renderer: am5xy.AxisRendererX.new(root, {})
        }));
        
        var yRenderer = am5xy.AxisRendererY.new(root, {
            minGridDistance: 30
          });
          
          yRenderer.grid.template.set("location", 1);
          
          var yAxis = chart.yAxes.push(am5xy.CategoryAxis.new(root, {
            maxDeviation: 0,
            categoryField: "category",
            renderer: yRenderer,
            tooltip: am5.Tooltip.new(root, { themeTags: ["axis"] })
          }));
        
        
        // Add series
        // https://www.amcharts.com/docs/v5/charts/xy-chart/series/
        var series = chart.series.push(am5xy.ColumnSeries.new(root, {
            name: "Series 1",
            xAxis: xAxis,
            yAxis: yAxis,
            valueXField: "value",
            categoryYField: "category",
            tooltip: am5.Tooltip.new(root, {
              pointerOrientation: "left",
              labelText: "{valueX}"
            })
          }));
  
          series.columns.template.setAll({
            cornerRadiusTR: 5,
            cornerRadiusBR: 5,
            strokeOpacity: 0
          });
          
          // Make each column to be of a different color
          series.columns.template.adapters.add("fill", function(fill, target) {
            return chart.get("colors").getIndex(series.columns.indexOf(target));
          });
          
          series.columns.template.adapters.add("stroke", function(stroke, target) {
            return chart.get("colors").getIndex(series.columns.indexOf(target));
          });
  
  
        const resetGraph = () => {
            yAxis.data.setAll([])
            series.data.setAll([])
        }
        
        const reloadGraph = (seriesAxisFormated, XAxisFormated) => {
            resetGraph()
            yAxis.data.setAll(seriesAxisFormated)
            series.data.setAll(seriesAxisFormated)
            sortCategoryAxis()
        }
  
        yAxis.data.setAll([])
        series.data.setAll([])
  
        sortCategoryAxis()
  
        function getSeriesItem(category) {
            for (var i = 0; i < series.dataItems.length; i++) {
              var dataItem = series.dataItems[i];
              if (dataItem.get("categoryY") == category) {
                return dataItem;
              }
            }
          }
  
        function sortCategoryAxis() {
  
            // Sort by value
            series.dataItems.sort(function(x, y) {
              return x.get("valueX") - y.get("valueX"); // descending
              //return y.get("valueY") - x.get("valueX"); // ascending
            })
          
            // Go through each axis item
            am5.array.each(yAxis.dataItems, function(dataItem) {
              // get corresponding series item
              var seriesDataItem = getSeriesItem(dataItem.get("category"));
          
              if (seriesDataItem) {
                // get index of series data item
                var index = series.dataItems.indexOf(seriesDataItem);
                // calculate delta position
                var deltaPosition = (index - dataItem.get("index", 0)) / series.dataItems.length;
                // set index to be the same as series data item index
                dataItem.set("index", index);
                // set deltaPosition instanlty
                dataItem.set("deltaPosition", -deltaPosition);
                // animate delta position to 0
                dataItem.animate({
                  key: "deltaPosition",
                  to: 0,
                  duration: 1000,
                  easing: am5.ease.out(am5.ease.cubic)
                })
              }
            });
          
            // Sort axis items by index.
            // This changes the order instantly, but as deltaPosition is set,
            // they keep in the same places and then animate to true positions.
            yAxis.dataItems.sort(function(x, y) {
              return x.get("index") - y.get("index");
            });
          }
    
        
        
        // Add scrollbar
        // https://www.amcharts.com/docs/v5/charts/xy-chart/scrollbars/
        chart.set("scrollbarX", am5.Scrollbar.new(root, {
          orientation: "horizontal"
        }));
        
        
        
        // Make stuff animate on load
        // https://www.amcharts.com/docs/v5/concepts/animations/
        series.appear(1000);
        chart.appear(1000, 100);
  
  
  
  
  
  
  
  
  
  
  
  
  
        // ################################ Gráfico Paradas Durante o Dia #################### \\
        
        var rootGraph = am5.Root.new("graphMotivePerDay");
  
  
        // Set themes
        // https://www.amcharts.com/docs/v5/concepts/themes/
        rootGraph.setThemes([
        am5themes_Animated.new(rootGraph)
        ]);
  
  
        // Create chart
        // https://www.amcharts.com/docs/v5/charts/xy-chart/
        var chartGraph = rootGraph.container.children.push(am5xy.XYChart.new(rootGraph, {
        panX: true,
        panY: true,
        wheelX: "panX",
        wheelY: "zoomX",
        pinchZoomX: true
        }));
  
        // Add cursor
        // https://www.amcharts.com/docs/v5/charts/xy-chart/cursor/
        var cursor = chartGraph.set("cursor", am5xy.XYCursor.new(rootGraph, {}));
        cursor.lineY.set("visible", false);
  
  
        // Create axes
        // https://www.amcharts.com/docs/v5/charts/xy-chart/axes/
        var xRenderer = am5xy.AxisRendererX.new(rootGraph, { minGridDistance: 30 });
        xRenderer.labels.template.setAll({
        rotation: -90,
        centerY: am5.p50,
        centerX: am5.p100,
        paddingRight: 15
        });
  
        xRenderer.grid.template.setAll({
        location: 1
        })
  
        var xAxisGraph = chartGraph.xAxes.push(am5xy.CategoryAxis.new(rootGraph, {
        maxDeviation: 0.3,
        categoryField: "category",
        renderer: xRenderer,
        tooltip: am5.Tooltip.new(rootGraph, {})
        }));
  
        var yAxisGraph = chartGraph.yAxes.push(am5xy.ValueAxis.new(rootGraph, {
        maxDeviation: 0.3,
        maxPrecision: 0,
        renderer: am5xy.AxisRendererY.new(rootGraph, {
            strokeOpacity: 0.1
        })
        }));
  
  
        // Create series
        // https://www.amcharts.com/docs/v5/charts/xy-chart/series/
        var seriesGraph = chartGraph.series.push(am5xy.ColumnSeries.new(rootGraph, {
        name: "Series 1",
        xAxis: xAxisGraph,
        yAxis: yAxisGraph,
        valueYField: "value",
        sequencedInterpolation: true,
        categoryXField: "category",
        tooltip: am5.Tooltip.new(rootGraph, {
            labelText: "{valueY}"
        })
        }));
  
        seriesGraph.columns.template.setAll({ cornerRadiusTL: 5, cornerRadiusTR: 5, strokeOpacity: 0 });
        seriesGraph.columns.template.adapters.add("fill", function(fill, target) {
        return chartGraph.get("colors").getIndex(seriesGraph.columns.indexOf(target));
        });
  
        seriesGraph.columns.template.adapters.add("stroke", function(stroke, target) {
        return chartGraph.get("colors").getIndex(seriesGraph.columns.indexOf(target));
        });
  
  
  
  
        // Make stuff animate on load
        // https://www.amcharts.com/docs/v5/concepts/animations/
        seriesGraph.appear(1000);
        chart.appear(1000, 100);
  })