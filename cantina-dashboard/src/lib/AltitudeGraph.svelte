<script>
  import * as echarts from "echarts";
  import { BarChart } from "echarts/charts";
  import {
    GridComponent,
    SingleAxisComponent,
    TitleComponent,
  } from "echarts/components";
  import { init, use } from "echarts/core";
  import { CanvasRenderer } from "echarts/renderers";
  import { onMount } from "svelte";
  let { altitudeData, chartInstance = $bindable() } = $props();
  let chartContainer;

  onMount(() => {
    let option = {
      title: { text: "Altitude Graph    ", textStyle: { color: "#d3e1dc" } },

      backgroundColor: "#153056",

      xAxis: {
        type: "value",
        min: 0,
        max: 1,
        show: false, 
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 600,

        splitLine: { show: true },
        lineStyle: { color: "#d3e1dc" },
      },
      textStyle: { color: "rgb(211,225,220)" },

      series: [
        {
          symbolSize: 10,
          lineStyle: {
            width: 4,
          },
          type: "line",
          showSymbol: false, // Speeds up rendering significantly by omitting point dots
          sampling: "lttb",
          smooth: true,
          color: "rgb(226,160,82)",

          data: altitudeData,
        },
      ],
    };
    chartInstance = echarts.init(chartContainer);

    use([BarChart, GridComponent, CanvasRenderer, TitleComponent]);
    chartInstance.setOption(option);

    const resizeObserver = new ResizeObserver(() => chartInstance?.resize());
    resizeObserver.observe(chartContainer);

    return () => {
      //clearInterval(updateInterval);
      resizeObserver.disconnect();
      chartInstance?.dispose();
    };
  });
  $effect(() => {
    if (chartInstance & altitudeData) {
      chartInstance.setOption({
        series: [
          {
            data: [altitudeData],
          },
        ],
      });
    }
  });
</script>

<div class="altGraph" bind:this={chartContainer}></div>

<style>
  .altGraph {
    height: 400px;
    width: 150px;
    border-radius: 12px;
    overflow: hidden;
  }
</style>
