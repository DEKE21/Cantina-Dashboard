<script>
    import { onMount } from "svelte";
    import * as echarts from "echarts";

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
        // Initialize Chart
        chartInstance = echarts.init(chartContainer);
        chartInstance.setOption(option);
        chartInstance.setOption({
            title: { text: titleText, textStyle: {} },
            yAxis: { name: Units },
        });

        // Handle Resizing
        const resizeObserver = new ResizeObserver(() =>
            chartInstance?.resize(),
        );
        resizeObserver.observe(chartContainer);

        // Safe Live Interval updates
        let m = setInterval(() => {
            // FIX: Use .at(-1) instead of [-1]
            if (liveData !== yBuffer.at(-1) || time !== xBuffer.at(-1)) {
                yBuffer.push(parseInt(liveData));
                xBuffer.push(parseInt(time));

                // FIX: Correct logical && and remove extra array nesting in series data
                if (chartInstance && liveData && xBuffer.length) {
                    chartInstance.setOption({
                        xAxis: [{ data: time }],
                        series: [{ data: liveData }],
                    });

                    // FIX: Set label to the last item
                    liveNumberBar = liveData[-1] || liveData.at(-1) || 0;
                }
            }
        }, 100);

        // Clean up intervals and observers when destroyed
        return () => {
            clearInterval(m);
            resizeObserver.disconnect();
            chartInstance?.dispose();
        };
    });
</script>

<div class="GM">
    <div class="graph" bind:this={chartContainer}></div>
    <div class="box">{liveNumberBar} {UnitSub}</div>
</div>

<style>
    .GM {
        display: flex; /* Added display: flex to make flex properties work */
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
