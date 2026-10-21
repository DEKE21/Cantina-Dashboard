<script>
    import { onMount } from "svelte";
    import * as echarts from "echarts";

    let {
        titleText = "Graph",
        Units = "",
        UnitSub = "",
        time = [],
        liveData = [],
        liveData2 = undefined,
        option = {},
        chartInstance = $bindable(null),
    } = $props();

    let chartContainer;
    let localChart = $state.raw(null);
    let liveNumberBar = $state(0);
    let liveNumberBar2 = $state(null);

    onMount(() => {
        const instance = echarts.init(chartContainer);

        // Clone option so 4 graphs don't mutate the exact same object reference
        if (option) {
            instance.setOption(structuredClone(option));
        }

        instance.setOption({
            title: { text: titleText, textStyle: {} },
            xAxis: { type: "category" },
            yAxis: { name: Units },
        });

        localChart = instance;
        chartInstance = instance;

        const resizeObserver = new ResizeObserver(() => {
            instance.resize();
        });
        resizeObserver.observe(chartContainer);

        return () => {
            resizeObserver.disconnect();
            instance.dispose();
        };
    });

    $effect(() => {
        const xArray = Array.isArray(time) ? [...time] : [];
        const yArray1 = Array.isArray(liveData) ? [...liveData] : [];
        const yArray2 = Array.isArray(liveData2) ? [...liveData2] : null;

        if (!localChart || yArray1.length === 0) return;

        const seriesList = [
            {
                name: yArray2 ? "Channel 1" : titleText,
                data: yArray1,
                type: "line",
                smooth: true,
                showSymbol: false,
                sampling: "lttb",
                color: "#5580bf",
            },
        ];

        if (yArray2) {
            seriesList.push({
                name: "Channel 2",
                data: yArray2,
                type: "line",
                smooth: true,
                showSymbol: false,
                sampling: "lttb",
                color: "#c94a4a",
            });
        }

        localChart.setOption({
            xAxis: { data: xArray },
            series: seriesList,
        });

        liveNumberBar = yArray1.at(-1) ?? 0;
        liveNumberBar2 = yArray2 ? (yArray2.at(-1) ?? 0) : null;
    });
</script>

<div class="GM">
    <div class="graph" bind:this={chartContainer}></div>
    <div class="box">
        {#if liveNumberBar2 !== null}
            <span class="dual-text"
                >{liveNumberBar} {UnitSub} | {liveNumberBar2} {UnitSub}</span
            >
        {:else}
            {liveNumberBar} {UnitSub}
        {/if}
    </div>
</div>

<style>
    .GM {
        display: flex;
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
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .dual-text {
        font-size: 26px;
        font-weight: bold;
    }
</style>
