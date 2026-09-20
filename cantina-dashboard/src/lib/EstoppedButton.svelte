<script>
    import { bind } from "leaflet";
    import Box from "./Box.svelte";
    import { blur } from "svelte/transition";

    let {
        title,
         ESTOP,
        Runnable,
        color,
    } = $props();
    let blurFactor = $state(2);

    function clicked() {
        if (ESTOP == true) {
          Runnable();
        }
    }
    $effect(() => {
        if (ESTOP == true) {
            blurFactor = 0;
        } else {
            blurFactor = 2;
        }
    });
</script>

<button
    class="ESTOP"
    style="--color:{color};--blurF:{blurFactor}px"
    onclick={clicked}>{title}</button
>

<style>
    .ESTOP {
        width: 100px;
        height: 100px;
        border-radius: 12px;
        background-color: var(--color);
        filter: blur(var(--blurF));
        
    }
</style>
