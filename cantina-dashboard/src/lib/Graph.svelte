<script>
    import { onMount } from "svelte";
    import * as echarts from "echarts";
    //  /**@property {Array} [time=[]] */
    let {
        titleText,
        Units,
        UnitSub,
        time = $bindable(),
        liveData = $bindable(),
        option,
        chartInstance = $bindable(),
    } = $props();

    let chartContainer;
    let liveNumberBar = $state(0);
    let yBuffer = [];
    let xBuffer = [];

    onMount(() => {
        chartInstance = echarts.init(chartContainer);
        chartInstance.setOption(option);
        chartInstance.setOption({
            title: { text: titleText, textStyle: {} },
            yAxis: { name: Units },
        });
        const resizeObserver = new ResizeObserver(() =>
            chartInstance?.resize(),
        );
        resizeObserver.observe(chartContainer);

        return () => {
            resizeObserver.disconnect();
            chartInstance?.dispose();
        };
    });
    let m = setInterval(() => {
       // console.log("gr", liveData);
        if (liveData != yBuffer[-1] || time != xBuffer[-1]) {
            yBuffer.push(parseInt(liveData));
            xBuffer.push(parseInt(time));
              console.log([xBuffer, yBuffer]);

            if (chartInstance && yBuffer & xBuffer) {
                chartInstance.setOption({
                    xAxis:[{data:xBuffer}],
                    series: [{ data: [ yBuffer] }
                ],
                });
                liveNumberBar = liveData[-1];
            }
        }
    },250);

  //  $effect(() => {});
</script>

<div class="GM">
    <div class="graph" bind:this={chartContainer}></div>
    <div class="box">{liveNumberBar} {UnitSub}</div>
</div>

<style>
    .GM {
        flex: auto;
        flex-direction: column;
    }
    .graph {
        height: 300px;
        width: 300px;
        border-radius: 12px;
        overflow: hidden;
    }
    .box {
        width: 300px;
        height: 50px;
        border-radius: 12px;
        background-color: #cb913a;
        text-align: center;
        font-size: 45px;
    }
</style>
