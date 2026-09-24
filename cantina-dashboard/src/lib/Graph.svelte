<script>
    import { onMount } from "svelte";
    import * as echarts from "echarts";

    let {
        titleText,
        Units,
        UnitSub,
        liveData,
        option,
        chartInstance = $bindable(),
    } = $props();

    let chartContainer;
    let liveNumberBar = $state(0);

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

    $effect(() => {
        if (chartInstance && liveData) {
            chartInstance.setOption({
                series: [{ data: liveData }],
            });
            liveNumberBar = liveData.at(-1)[1];
        }
    });
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
