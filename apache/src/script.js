var barChartOptions = {
    series: [{
    data: [400, 430, 448, 470, 540, 580, 690]
  }],
    chart: {
    type: 'bar',
    height: 350
  },
  annotations: {
    xaxis: [{
      x: 500,
      borderColor: '#00E396',
      label: {
        borderColor: '#00E396',
        style: {
          color: '#fff',
          background: '#00E396',
        },
        text: 'X annotation',
      }
    }],
    yaxis: [{
      y: 'July',
      y2: 'September',
      label: {
        text: 'Y annotation'
      }
    }]
  },
  plotOptions: {
    bar: {
      horizontal: true,
    }
  },
  dataLabels: {
    enabled: true
  },
  xaxis: {
    categories: ['June', 'July', 'August', 'September', 'October', 'November', 'December'],
  },
  grid: {
    xaxis: {
      lines: {
        show: true
      }
    }
  },
  yaxis: {
    reversed: true,
    axisTicks: {
      show: true
    }
  }
  };

  var barChart = new ApexCharts(document.querySelector("#bar-chart"), barChartOptions);
  barChart.render();

  // area chart

  var areaChartOptions = {
    series: [{
    name: 'series1',
    data: [31, 40, 28, 51, 42, 109, 100]
  }, {
    name: 'series2',
    data: [11, 32, 45, 32, 34, 52, 41]
  }],
    chart: {
    height: 350,
    type: 'area'
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  xaxis: {
    type: 'datetime',
    categories: ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z", "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z", "2018-09-19T06:30:00.000Z"]
  },
  tooltip: {
    x: {
      format: 'dd/MM/yy HH:mm'
    },
  },
  };

  var areaChart = new ApexCharts(document.querySelector("#area-chart"), areaChartOptions);
  areaChart.render();